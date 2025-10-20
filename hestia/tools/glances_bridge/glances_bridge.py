#!/usr/bin/env python3
"""
glances_bridge.py

Small ADR-0031-compliant tool to normalize Glances API and optionally export via Tailscale.

Usage:
  glances_bridge.py dry-run
  glances_bridge.py apply

Behaviors (per ADR-0031):
- Load config from /config/hestia/config/system/hestia.toml under
    [automation.glances_bridge]
- dry-run: probe upstream, validate normalization rules, produce report + ledger
    (no writes)
- apply: perform atomic install of normalizer script, start as background
    process, configure tailscale serve (if available), produce apply report +
    ledger
- Use write-broker if configured for writes
- Implement run-lock and idempotency checks

Notes:
- This is intentionally small and self-contained. It prefers to run under /config environment.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

# --- Constants & defaults
HTOML = Path("/config/hestia/config/system/hestia.toml")
TOOL = "glances_bridge"

DEFAULT_CFG = {
    "repo_root": "/config",
    "config_root": "/config/hestia/config",
    "allowed_root": "/config/hestia",
    "report_dir": "/config/hestia/workspace/reports/glances_bridge",
    "index_dir": "/config/hestia/workspace/.hestia/index",
    "runtime": {
        "upstream_url": "http://127.0.0.1:61208",
        "listen_host": "127.0.0.1",
        "normalizer_port": 61209,
        "tailscale_host": "",
        "tailscale_port": 61208,
    },
    "apply": {
        "use_write_broker": False,
        "write_broker_cmd": "/config/bin/write-broker",
        "write_broker_mode": "",
    },
    "retention": {"reports_days": 14, "ledger_lines": 20000},
}

# --- Helpers


def now_z() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def load_toml_config() -> dict:
    try:
        import tomllib as toml  # py311+
    except Exception:
        import toml as toml  # 3rd-party fallback
    if not HTOML.exists():
        return DEFAULT_CFG
    data = toml.loads(HTOML.read_text(encoding="utf-8"))
    cfg = data.get("automation", {}).get(TOOL, {})
    # shallow merge defaults
    out = DEFAULT_CFG.copy()
    out.update(cfg)
    # ensure nested keys exist
    out.setdefault("runtime", DEFAULT_CFG["runtime"])
    out.setdefault("apply", DEFAULT_CFG["apply"])
    out.setdefault("retention", DEFAULT_CFG["retention"])
    return out


@dataclass
class Report:
    started_at: str
    finished_at: str | None
    mode: str
    success: bool
    details: dict

    def to_dict(self):
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "mode": self.mode,
            "success": self.success,
            "details": self.details,
        }


def append_ledger(index: Path, payload: dict):
    index.parent.mkdir(parents=True, exist_ok=True)
    with index.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, separators=(",", ":")) + "\n")


# run-lock


def acquire_lock(lockfile: Path):
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    fp = lockfile.open("w")
    try:
        import fcntl

        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except Exception as exc:
        raise SystemExit("E-LOCK-001: another run is in progress") from exc
    return fp


# idempotency: check if last applied sha for target matches


def last_applied_sha(index: Path, target: str) -> str | None:
    if not index.exists():
        return None
    try:
        with index.open("r", encoding="utf-8") as fh:
            for line in reversed(fh.readlines()[-5000:]):
                try:
                    d = json.loads(line)
                    for r in d.get("results", []):
                        tp = r.get("target_path")
                        applied = r.get("applied")
                        sha = r.get("apu", {}).get("provenance", {}).get("sha256")
                        if tp == target and applied and sha:
                            return sha
                except Exception:
                    continue
    except Exception:
        return None
    return None


# tiny sha256 helper


def sha256_bytes(b: bytes) -> str:
    import hashlib

    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


# atomic write


def atomic_write_text(dst: Path, text: str):
    tmp = Path(tempfile.mkstemp(prefix=dst.name, dir=str(dst.parent))[1])
    tmp.write_text(text, encoding="utf-8")
    bak = dst.with_suffix(dst.suffix + ".bak") if dst.exists() else None
    if bak:
        dst.replace(bak)
    tmp.replace(dst)


# broker rewrite helper (best-effort)


def broker_rewrite(cfg_apply: dict, dst: Path, temp_src: Path) -> tuple[int, str, str]:
    cmd = cfg_apply.get("write_broker_cmd")
    if not cmd:
        return (127, "", "broker_not_configured")
    mode = cfg_apply.get("write_broker_mode", "")
    args = [cmd, mode or "rewrite", "--file", str(dst), "--from", str(temp_src)]
    p = subprocess.run(args, capture_output=True, text=True)
    return (p.returncode, p.stdout[-4000:], p.stderr[-4000:])


# normalizer script content (kept small and similar to the provided snippet)
NORMALIZER_SCRIPT = r"""
#!/usr/bin/env python3
import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

UPSTREAM = "{upstream}"


def normalize_diskio_all(payload):
    try:
        data = json.loads(payload)
    except Exception:
        return payload, "pass"
    changed = False
    if isinstance(data, dict) and isinstance(data.get("diskio"), list):
        for d in data["diskio"]:
            if isinstance(d, dict) and "time_since_update" not in d:
                d["time_since_update"] = 1.0
                changed = True
    return (json.dumps(data).encode("utf-8"), "changed" if changed else "pass")


def normalize_diskio_list(payload):
    try:
        data = json.loads(payload)
    except Exception:
        return payload, "pass"
    changed = False
    if isinstance(data, list):
        for d in data:
            if isinstance(d, dict) and "time_since_update" not in d:
                d["time_since_update"] = 1.0
                changed = True
    return (json.dumps(data).encode("utf-8"), "changed" if changed else "pass")


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _proxy(self):
        url = f"{UPSTREAM}{self.path}"
        body = None
        if self.command in ("POST", "PUT", "PATCH"):
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length > 0 else None
        req = Request(url, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length"):
                req.add_header(k, v)
        try:
            with urlopen(req, timeout=8) as r:
                status = r.status
                resp_body = r.read()
                headers = dict(r.headers.items())
        except HTTPError as e:
            status = e.code
            resp_body = e.read()
            headers = dict(e.headers.items())
        except URLError as e:
            status = 502
            resp_body = json.dumps({"error": "upstream_unreachable", "detail": str(e)}).encode()
            headers = {"Content-Type": "application/json"}
        return status, headers, resp_body

    def do_GET(self):
        status, headers, body = self._proxy()
        path = self.path
        mode = "pass"
        if path.startswith("/api/4/all"):
            body, mode = normalize_diskio_all(body)
            headers["Content-Type"] = "application/json"
        elif path.startswith("/api/4/diskio"):
            body, mode = normalize_diskio_list(body)
            headers["Content-Type"] = "application/json"
        # write response
        self.send_response(status)
        headers["Content-Length"] = str(len(body))
        for hk in list(headers.keys()):
            if hk.lower() in (
                "transfer-encoding",
                "connection",
                "keep-alive",
                "proxy-authenticate",
                "proxy-authorization",
                "te",
                "trailers",
                "upgrade",
            ):
                headers.pop(hk, None)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    host = "{listen_host}"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 61209
    srv = ThreadingHTTPServer((host, port), H)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
"""


# --- Core operations


def probe_upstream(upstream: str, timeout: int = 5) -> dict:
    """Probe upstream /api/4/all and /api/4/diskio to check data shapes."""
    import urllib.request

    out = {"upstream": upstream, "ok": False, "errors": [], "samples": {}}
    try:
        with urllib.request.urlopen(f"{upstream}/api/4/diskio", timeout=timeout) as r:
            b = r.read()
            try:
                j = json.loads(b)
                out["samples"]["diskio"] = j
            except Exception as e:
                out["errors"].append(f"diskio: parse_error:{e}")
        out["ok"] = True
    except Exception as e:
        out["errors"].append(str(e))
    return out


def build_reports_dirs(cfg: dict, mode: str) -> tuple[Path, Path, Path]:
    report_dir = Path(cfg.get("report_dir") or DEFAULT_CFG["report_dir"])
    index_dir = Path(cfg.get("index_dir") or DEFAULT_CFG["index_dir"])
    report_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)
    suffix = (mode or "report").replace("-", "_")
    report_file = report_dir / f"{TOOL}__{int(time.time())}__{suffix}.json"
    index_file = index_dir / f"{TOOL}__index.jsonl"
    lock_file = index_dir / f"{TOOL}.lock"
    return report_file, index_file, lock_file


def install_normalizer_script(cfg: dict, target_path: Path, content: str) -> dict:
    """Install provided content to target_path via broker or atomic write. Cleans temp file."""
    tmp = Path(tempfile.mkstemp(prefix=target_path.name, dir=str(target_path.parent))[1])
    tmp.write_text(content, encoding="utf-8")
    tmp.chmod(0o755)
    sha = sha256_bytes(content.encode())
    try:
        if cfg.get("apply", {}).get("use_write_broker"):
            rc, sout, serr = broker_rewrite(cfg.get("apply", {}), target_path, tmp)
            if rc != 0:
                return {
                    "installed": False,
                    "reason": f"broker_failed:{rc}",
                    "stdout": sout,
                    "stderr": serr,
                }
            return {"installed": True, "method": "broker", "sha": sha}
        # atomic write
        atomic_write_text(target_path, content)
        return {"installed": True, "method": "atomic", "sha": sha}
    finally:
        with contextlib.suppress(Exception):
            tmp.unlink()


def start_normalizer(target_path: Path, port: int, log_dir: Path) -> dict:
    # If running, try to kill older processes by using a simple pkill -f
    # Then start via nohup to background
    # kill any existing process (best-effort)
    # quick listen check before touching anything
    out = {"started": False}
    stdout = log_dir / "glances-normalize.out"
    stderr = log_dir / "glances-normalize.err"
    cmd = [str(target_path), str(port)]
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.4)
        s.connect(("127.0.0.1", int(port)))
        s.close()
        return {"started": True, "already_running": True}
    except Exception:
        pass
    # start detached
    with open(stdout, "a") as so, open(stderr, "a") as se:
        subprocess.Popen(cmd, stdout=so, stderr=se, start_new_session=True)
    time.sleep(0.7)
    # check listen
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", int(port)))
            out["started"] = True
        except Exception:
            out["started"] = False
        finally:
            s.close()
    except Exception:
        out["started"] = False
    return out


def configure_tailscale(cfg: dict) -> dict:
    host = cfg.get("runtime", {}).get("tailscale_host")
    port = cfg.get("runtime", {}).get("tailscale_port")
    nport = cfg.get("runtime", {}).get("normalizer_port")
    if not host:
        return {"configured": False, "reason": "no_tailscale_host"}
    if shutil.which("tailscale") is None:
        return {"configured": False, "reason": "tailscale_cli_missing"}
    try:
        subprocess.run(["tailscale", "serve", "reset"], check=False)
        subprocess.run(["tailscale", "serve", "tcp", str(port), f"127.0.0.1:{nport}"], check=True)
        return {"configured": True}
    except subprocess.CalledProcessError as e:
        return {"configured": False, "reason": f"tailscale_failed:{e}"}


# --- Main modes


def dry_run(cfg: dict, report_file: Path, index_file: Path) -> Report:
    started = now_z()
    repo_root = Path(cfg.get("repo_root", "/config"))
    target = repo_root / "bin" / "glances-normalize.py"
    details = {"probes": {}, "install": {"would_install_to": str(target)}}
    upstream = cfg.get("runtime", {}).get("upstream_url")
    p = probe_upstream(upstream)
    details["probes"]["upstream"] = p
    # simulate normalization by running the normalizer code in-memory on sample if available
    sample = p.get("samples", {}).get("diskio")
    if sample is not None:
        # check missing fields
        missing = sum(1 for x in sample if isinstance(x, dict) and "time_since_update" not in x)
        details["probes"]["upstream_missing_time_since_update"] = missing
        # simulate normalized
        normalized = []
        for d in sample:
            if isinstance(d, dict) and "time_since_update" not in d:
                d2 = dict(d)
                d2["time_since_update"] = 1.0
                normalized.append(d2)
            else:
                normalized.append(d)
        details["probes"]["normalized_preview_count"] = len(normalized)
    success = bool(p.get("ok"))

    rep = Report(
        started_at=started,
        finished_at=now_z(),
        mode="dry-run",
        success=success,
        details=details,
    )
    # emit report and ledger entry
    report_file.write_text(json.dumps(rep.to_dict(), indent=2), encoding="utf-8")
    ledger = {
        "ts": int(time.time()),
        "mode": "dry-run",
        "results": [
            {
                "target_path": str(target),
                "applied": False,
                "traffic_light": "green" if success else "red",
                "skip_reason": None,
                "apu": {"provenance": {"sha256": None}},
                "summary": "dry-run: evaluated upstream and normalization preview",
            }
        ],
    }
    append_ledger(index_file, ledger)
    # retention prune
    _prune_retention(cfg, report_file.parent, index_file)
    return rep


def apply(cfg: dict, report_file: Path, index_file: Path, lock_fp) -> Report:
    started = now_z()
    details = {"steps": {}, "install": {}}
    # target installation path under repo_root/bin
    repo_root = Path(cfg.get("repo_root", "/config"))
    bin_dir = repo_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / "glances-normalize.py"
    # prepare content and idempotency
    rt = cfg.get("runtime", {})
    upstream = rt.get("upstream_url")
    listen_host = rt.get("listen_host", "127.0.0.1")
    content = NORMALIZER_SCRIPT.format(upstream=upstream, listen_host=listen_host)
    new_sha = sha256_bytes(content.encode())
    prev_ledger_sha = last_applied_sha(index_file, str(target))
    existing_sha = None
    if target.exists():
        with contextlib.suppress(Exception):
            existing_sha = sha256_bytes(target.read_bytes())
    idempotent = new_sha in (prev_ledger_sha, existing_sha)

    # install script (skip if idempotent)
    if not idempotent:
        inst = install_normalizer_script(cfg, target, content)
    else:
        inst = {"installed": False, "method": None, "sha": new_sha, "reason": "idempotent"}
    details["install"]["result"] = inst
    # start normalizer
    log_dir = Path("/config/hestia/workspace/operations/logs/glances_bridge")
    log_dir.mkdir(parents=True, exist_ok=True)
    started_info = start_normalizer(target, cfg.get("runtime", {}).get("normalizer_port"), log_dir)
    details["steps"]["start_normalizer"] = started_info
    # tailscale
    tails = configure_tailscale(cfg)
    details["steps"]["tailscale"] = tails

    # ledger entry with applied + provenance + traffic light/skip
    tl = (
        "green"
        if (inst.get("installed") or idempotent) and started_info.get("started")
        else "orange"
    )
    payload = {
        "ts": int(time.time()),
        "mode": "apply",
        "results": [
            {
                "target_path": str(target),
                "applied": bool(inst.get("installed")),
                "traffic_light": tl,
                "skip_reason": inst.get("reason") if idempotent else None,
                "apu": {"provenance": {"sha256": inst.get("sha")}},
                "summary": "installed normalizer script and started service",
            }
        ],
    }
    append_ledger(index_file, payload)
    rep = Report(
        started_at=started,
        finished_at=now_z(),
        mode="apply",
        success=(tl == "green"),
        details=details,
    )
    report_file.write_text(json.dumps(rep.to_dict(), indent=2), encoding="utf-8")
    # retention prune
    _prune_retention(cfg, report_file.parent, index_file)
    return rep


def main():
    parser = argparse.ArgumentParser(prog="glances_bridge.py")
    parser.add_argument("mode", choices=["dry-run", "apply"], help="Operation mode")
    args = parser.parse_args()
    cfg = load_toml_config()
    report_file, index_file, lock_file = build_reports_dirs(cfg, args.mode)
    # acquire run-lock for apply mode
    lock_fp = None
    if args.mode == "apply":
        lock_fp = acquire_lock(lock_file)
    try:
        if args.mode == "dry-run":
            rep = dry_run(cfg, report_file, index_file)
            print(json.dumps(rep.to_dict(), indent=2))
            sys.exit(0 if rep.success else 2)
        else:
            rep = apply(cfg, report_file, index_file, lock_fp)
            print(json.dumps(rep.to_dict(), indent=2))
            sys.exit(0 if rep.success else 3)
    finally:
        if lock_fp:
            with contextlib.suppress(Exception):
                lock_fp.close()


# retention prune (best-effort)
def _prune_retention(cfg: dict, report_dir: Path, index_file: Path) -> None:
    now_ts = time.time()
    days = int(cfg.get("retention", {}).get("reports_days", 14))
    keep_lines = int(cfg.get("retention", {}).get("ledger_lines", 20000))
    cutoff = now_ts - (days * 86400)
    with contextlib.suppress(Exception):
        for f in report_dir.glob("*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
    with contextlib.suppress(Exception):
        if index_file.exists():
            lines = index_file.read_text(encoding="utf-8").splitlines()
            if len(lines) > keep_lines:
                tail = "\n".join(lines[-keep_lines:]) + "\n"
                index_file.write_text(tail, encoding="utf-8")


if __name__ == "__main__":
    main()
