"""Command-line interface for the compactor toolkit.

All subcommands print a single-line compact JSON summary to stderr. Primary outputs go to --out or stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
import tarfile
from pathlib import Path

from . import audit, core


def _print_summary(data: dict) -> None:
    print(json.dumps(data, separators=(",",":")), file=sys.stderr)


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        doc, file_bytes, canonical_bytes, sha_file, sha_canon, trailing = core.canonicalize(args.input)
    except json.JSONDecodeError:
        _print_summary({"error": "json_parse", "code": 3})
        return 3
    except OSError:
        _print_summary({"error": "open_input", "code": 4})
        return 4

    ok = doc.get("key") == "core.entity_registry" and isinstance(doc.get("data", {}).get("entities"), list)
    summary = {
        "file_bytes": file_bytes,
        "canonical_bytes": canonical_bytes,
        "trailing_bytes": trailing,
        "sha_file": sha_file,
        "sha_canon": sha_canon,
        "entities_count": len(doc.get("data", {}).get("entities", [])),
        "sanity_key_ok": ok,
    }
    if args.out and args.out != "-":
        try:
            Path(args.out).write_bytes(json.dumps(doc, ensure_ascii=False, separators=(",",":" )).encode("utf-8"))
        except OSError:
            _print_summary({"error": "write_out", "code": 5})
            return 5
    _print_summary(summary)
    return 0 if ok else 6


def cmd_profile(args: argparse.Namespace) -> int:
    try:
        doc, *_ = core.canonicalize(args.input)
    except Exception:
        _print_summary({"error": "json_parse", "code": 3})
        return 3
    audit.write_size_profile_md(doc, args.report, args.largest)
    _print_summary({"ok": True, "report": args.report, "largest": args.largest})
    return 0


def cmd_sanitize(args: argparse.Namespace) -> int:
    try:
        doc, *_ = core.canonicalize(args.input)
    except Exception:
        _print_summary({"error": "json_parse", "code": 3})
        return 3
    new_doc, stats = core.sanitize_deleted(doc, keep_last=(args.keep_last or 0))
    out_bytes = json.dumps(new_doc, ensure_ascii=False, separators=(",",":" )).encode("utf-8")
    try:
        if args.out == "-":
            sys.stdout.buffer.write(out_bytes)
        else:
            Path(args.out).write_bytes(out_bytes)
    except OSError:
        _print_summary({"error": "write_out", "code": 5})
        return 5
    # optionally write a small provenance report into a ReportKit batch
    if getattr(args, 'out_batch', None):
        try:
            from hestia.tools.utils.reportkit.reportkit import utc_now_id, new_batch_dir, write_json_report, append_manifest
            when = utc_now_id()
            batch = new_batch_dir(args.out_batch, tool="compactor", label="scenario", when=when)
            batch_id = Path(batch).name
            artifact = Path(batch) / "compactor_summary.json"
            payload_meta = {
                "meta_schema":"v1",
                "created_at": when,
                "tool": "compactor",
                "script": "hestia/tools/utils/compactor/cli.py",
                "purpose": "registry cleanup",
                "batch_id": batch_id,
                "input_path": args.input,
                "format": "json",
            }
            write_json_report(str(artifact), payload_meta, stats)
            append_manifest({
                "meta_schema":"v1",
                "created_at": when,
                "tool":"compactor",
                "script":"hestia/tools/utils/compactor/cli.py",
                "purpose":"registry cleanup",
                "batch_id": batch_id,
                "file_relpath": str(artifact.relative_to(args.out_batch)),
                "format":"json",
            }, base_reports_dir=args.out_batch)
        except Exception:
            # Do not fail the compaction if reporting fails
            pass
    _print_summary({**stats, "out": args.out})
    return 0


def _build_compact_args(parser: argparse.ArgumentParser):
    parser.add_argument("--prune-disabled", action="append", choices=["integration", "device", "user"], default=[])
    parser.add_argument("--prune-duplicates", action="store_true")
    parser.add_argument("--prune-mobile-app", action="store_true")
    parser.add_argument("--prune-orphaned", action="store_true")
    parser.add_argument("--cap-trim-threshold", type=int, default=4096)
    parser.add_argument("--cap-drop-threshold", type=int, default=16384)
    parser.add_argument("--effect-list-max", type=int, default=50)
    parser.add_argument("--options-trim-threshold", type=int, default=0)
    parser.add_argument("--options-drop-threshold", type=int, default=0)


def cmd_dry_run(args: argparse.Namespace) -> int:
    try:
        doc, *_ = core.canonicalize(args.input)
    except Exception:
        _print_summary({"error": "json_parse", "code": 3})
        return 3
    _, stats = core.compact(
        doc,
        cap_trim=args.cap_trim_threshold,
        cap_drop=args.cap_drop_threshold,
        effect_list_max=args.effect_list_max,
        opt_trim=args.options_trim_threshold,
        opt_drop=args.options_drop_threshold,
        prune_disabled=set(args.prune_disabled),
        prune_duplicates=args.prune_duplicates,
        prune_mobile_app=args.prune_mobile_app,
        prune_orphaned=args.prune_orphaned,
    )
    _print_summary(stats)
    return 0


def cmd_compact(args: argparse.Namespace) -> int:
    try:
        doc, *_ = core.canonicalize(args.input)
    except Exception:
        _print_summary({"error": "json_parse", "code": 3})
        return 3
    new_doc, stats = core.compact(
        doc,
        cap_trim=args.cap_trim_threshold,
        cap_drop=args.cap_drop_threshold,
        effect_list_max=args.effect_list_max,
        opt_trim=args.options_trim_threshold,
        opt_drop=args.options_drop_threshold,
        prune_disabled=set(args.prune_disabled),
        prune_duplicates=args.prune_duplicates,
        prune_mobile_app=args.prune_mobile_app,
        prune_orphaned=args.prune_orphaned,
    )
    reduction_ok = True
    if args.require_reduction is not None:
        reduction_ok = (stats.get("reduction_pct", 0.0) >= (args.require_reduction * 100.0))
    if not reduction_ok:
        _print_summary({"error": "reduction_gate", "code": 10, "stats": stats})
        return 10
    out_bytes = json.dumps(new_doc, ensure_ascii=False, separators=(",",":" )).encode("utf-8")
    try:
        if args.out == "-":
            sys.stdout.buffer.write(out_bytes)
        else:
            Path(args.out).write_bytes(out_bytes)
    except OSError:
        _print_summary({"error": "write_out", "code": 5})
        return 5
    _print_summary(stats)
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    try:
        b = json.loads(Path(args.before).read_text(encoding="utf-8"))
        a = json.loads(Path(args.after).read_text(encoding="utf-8"))
    except Exception:
        _print_summary({"error": "json_parse", "code": 3})
        return 3
    dif = core.diff_entities(b, a)
    outdir = Path(args.report)
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "removed.tsv", "w", encoding="utf-8") as fh:
        fh.write("entity_id\n")
        for r in dif.get("removed", []):
            fh.write(r + "\n")
    with open(outdir / "kept.tsv", "w", encoding="utf-8") as fh:
        fh.write("entity_id\n")
        for k in dif.get("kept", []):
            fh.write(k + "\n")
    _print_summary({"removed": len(dif.get("removed", [])), "kept": len(dif.get("kept", []))})
    return 0


def cmd_bundle(args: argparse.Namespace) -> int:
    # args.include is a space-separated list for simplicity
    items = [] if not args.include else args.include.split()
    try:
        with tarfile.open(args.out, "w:gz") as tar:
            for it in items:
                p = Path(it)
                if p.exists():
                    tar.add(str(p), arcname=str(p))
    except Exception:
        _print_summary({"error": "bundle_failed", "code": 5})
        return 5
    _print_summary({"ok": True, "out": args.out})
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hestia.tools.utils.compactor")
    sub = parser.add_subparsers(dest="cmd")

    p_val = sub.add_parser("validate")
    p_val.add_argument("input")
    p_val.add_argument("--out", default=None)
    p_val.set_defaults(func=cmd_validate)

    p_prof = sub.add_parser("profile")
    p_prof.add_argument("input")
    p_prof.add_argument("--report", required=True)
    p_prof.add_argument("--largest", required=True)
    p_prof.set_defaults(func=cmd_profile)

    p_san = sub.add_parser("sanitize")
    p_san.add_argument("input")
    p_san.add_argument("--keep-last", type=int, default=0)
    p_san.add_argument("--out", required=True)
    p_san.set_defaults(func=cmd_sanitize)

    p_dry = sub.add_parser("dry-run")
    p_dry.add_argument("input")
    _build_compact_args(p_dry)
    p_dry.set_defaults(func=cmd_dry_run)

    p_comp = sub.add_parser("compact")
    p_comp.add_argument("input")
    p_comp.add_argument("--out", required=True)
    p_comp.add_argument("--out-batch", required=False, help="optional ReportKit base dir to write a compactor summary batch")
    p_comp.add_argument("--require-reduction", type=float, default=None)
    _build_compact_args(p_comp)
    p_comp.set_defaults(func=cmd_compact)

    p_diff = sub.add_parser("diff")
    p_diff.add_argument("before")
    p_diff.add_argument("after")
    p_diff.add_argument("--report", required=True)
    p_diff.set_defaults(func=cmd_diff)

    p_bundle = sub.add_parser("bundle")
    p_bundle.add_argument("--include")
    p_bundle.add_argument("--out", required=True)
    p_bundle.set_defaults(func=cmd_bundle)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
