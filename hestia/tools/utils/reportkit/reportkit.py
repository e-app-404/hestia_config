"""ReportKit helpers: batch dirs, atomic writes, frontmatter, and manifest append.

Guarantees:
- Atomic writes (temp file in same dir, fsync, os.replace)
- Single manifest: hestia/reports/_index.jsonl (append-only)
- BusyBox-friendly locking using O_EXCL to create a lock file
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional

# Monotonic per-process timestamp state
_LAST_TS: Optional[str] = None
_SEQ: int = 0


def utc_now_id() -> str:
    """Return UTC timestamp ID like YYYYMMDDTHHMMSSZ; monotonic per process.

    If called multiple times within the same second, append __2, __3, etc.
    """
    import datetime
    global _LAST_TS, _SEQ

    base = datetime.datetime.utcnow().replace(microsecond=0).isoformat().replace("-", "").replace(":", "").replace("T", "T") + "Z"
    if base == _LAST_TS:
        _SEQ += 1
        return f"{base}__{_SEQ}"
    _LAST_TS = base
    _SEQ = 1
    return base


def slugify(text: str) -> str:
    """Return a filesystem-safe slug: keep alnum and replace others with underscore."""
    out = []
    for ch in text:
        if ch.isalnum() or ch in ("-", "_"):
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out)
    # collapse sequential underscores
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")[:128]


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def new_batch_dir(base_dir: str, tool: str, label: str, when: Optional[str] = None) -> str:
    """Create a new batch dir and return its path.

    Path format: hestia/reports/YYYYMMDD/YYYYMMDDTHHMMSSZ__<tool>__<label>/
    Creates the dir and updates hestia/reports/latest -> this dir (symlink best-effort).
    If the dir exists, append __N suffix to avoid collision.
    """
    when = when or utc_now_id()
    dt = when[:8]
    tool_s = slugify(tool)
    label_s = slugify(label)
    base = Path(base_dir)
    daydir = base / dt
    _ensure_dir(daydir)
    batch_name = f"{when}__{tool_s}__{label_s}"
    batch_dir = daydir / batch_name
    n = 0
    while batch_dir.exists():
        n += 1
        batch_dir = daydir / f"{batch_name}__{n}"
    _ensure_dir(batch_dir)
    # update latest symlink
    try:
        latest = base / "latest"
        if latest.exists() or latest.is_symlink():
            try:
                latest.unlink()
            except Exception:
                pass
        latest.symlink_to(batch_dir)
    except Exception:
        # ignore symlink errors on BusyBox
        pass
    return str(batch_dir)


def _compute_sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _frontmatter_lines(meta: Dict[str, str]) -> str:
    lines = ["# ---"]
    for k, v in meta.items():
        lines.append(f"# {k}: {v}")
    lines.append("# ---")
    return "\n".join(lines) + "\n"


def atomic_write_text(path: str, text: str, mode: int = 0o600) -> None:
    """Atomically write text to path: temp file in same dir -> fsync -> os.replace.

    mode: permission mode to apply to the final file (default 0o600).
    """
    p = Path(path)
    _ensure_dir(p.parent)
    tmp = None
    try:
        # NamedTemporaryFile with delete=False so we can fsync and replace
        tf = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=str(p.parent))
        tmp = Path(tf.name)
        tf.write(text)
        tf.flush()
        os.fsync(tf.fileno())
        tf.close()
        os.replace(str(tmp), str(p))
        try:
            # Ensure strict permissions
            os.chmod(str(p), mode)
        except Exception:
            pass
        try:
            # fsync parent dir if possible
            dirfd = os.open(str(p.parent), os.O_RDONLY)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
        except Exception:
            pass
    finally:
        if tmp and tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def write_tsv_with_frontmatter(path: str, meta: Dict[str, str], header: str, rows: str) -> None:
    """Write a TSV/MD/CSV file with commented YAML frontmatter and atomic write.

    meta: mapping of metadata fields (values should be stringable)
    header: header line for body (e.g., 'name\tcount')
    rows: body lines (each line ending with \n)
    """
    # compute checksum of body (not including header comment)
    body = header + "\n" + rows
    checksum = _compute_sha256_bytes(body.encode("utf-8"))
    meta2 = dict(meta)
    meta2.setdefault("checksum_sha256", checksum)
    meta2.setdefault("rows", str(rows.count("\n")))
    fm = _frontmatter_lines(meta2)
    text = fm + body
    atomic_write_text(path, text, mode=0o600)


def write_json_report(path: str, meta: Dict[str, str], data: object) -> None:
    """Write a JSON object {"_meta": meta, "data": data} atomically."""
    obj = {"_meta": meta, "data": data}
    text = json.dumps(obj, ensure_ascii=False, separators=(",",":")) + "\n"
    atomic_write_text(path, text, mode=0o600)


def append_manifest(entry: Dict[str, object], base_reports_dir: str = "hestia/reports") -> None:
    """Append a single JSON line to hestia/reports/_index.jsonl using O_EXCL lock.

    Locking: create hestia/reports/.index.lock with O_CREAT|O_EXCL. Retry with small backoff up to 2s.
    """
    base = Path(base_reports_dir)
    _ensure_dir(base)
    manifest = base / "_index.jsonl"
    lock = base / ".index.lock"
    start = time.time()
    got = False
    while time.time() - start < 2.0:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            os.close(fd)
            got = True
            break
        except FileExistsError:
            time.sleep(0.05)
    if not got:
        raise RuntimeError("failed to acquire manifest lock")
    try:
        line = json.dumps(entry, ensure_ascii=False, separators=(",",":"))
        with open(manifest, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.chmod(str(manifest), 0o600)
        except Exception:
            pass
    finally:
        try:
            lock.unlink()
        except Exception:
            pass
