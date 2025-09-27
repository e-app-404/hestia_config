"""Post-boot health summary: parse HA log for ERROR/WARNING counts and top lines.

Writes a TSV with commented frontmatter via ReportKit.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
from pathlib import Path
import sys

from hestia.tools.utils.reportkit.reportkit import utc_now_id, new_batch_dir, write_tsv_with_frontmatter, append_manifest


def top_lines(path: Path, limit: int = 20):
    cnt = collections.Counter()
    errs = 0
    warns = 0
    for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if 'ERROR' in ln:
            errs += 1
        if 'WARNING' in ln:
            warns += 1
        # normalize long lines mildly
        s = ln.strip()
        if s:
            cnt[s] += 1
    top = cnt.most_common(limit)
    return errs, warns, top


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--log', default='home-assistant.log')
    p.add_argument('--reports-dir', default='hestia/reports')
    p.add_argument('--tool', default='post-boot-health')
    p.add_argument('--label', default='boot')
    p.add_argument('--limit', type=int, default=20)
    args = p.parse_args(argv)

    path = Path(args.log)
    if not path.exists():
        print('{"error":"log_not_found","path":"%s"}' % str(path), file=sys.stderr)
        sys.exit(2)

    errs, warns, top = top_lines(path, args.limit)

    when = utc_now_id()
    batch = new_batch_dir(args.reports_dir, args.tool, args.label, when)
    batch_id = Path(batch).name

    # prepare rows: count	line
    rows = ''.join(f"{cnt}\t{line}\n" for line, cnt in ((t[0], t[1]) for t in top))
    # header is count	line
    meta = {
        'meta_schema': 'v1',
        'created_at': when,
        'tool': args.tool,
        'script': 'hestia/tools/utils/compactor/post_boot_health.py',
        'purpose': 'post-boot health summary',
        'batch_id': batch_id,
        'input_path': str(path),
    }

    outpath = Path(batch) / 'post_boot_top_lines.tsv'
    write_tsv_with_frontmatter(str(outpath), meta, 'count\tline', rows)

    # append manifest
    manifest_entry = dict(meta)
    manifest_entry.update({'file_relpath': f"{Path(batch).relative_to(args.reports_dir).as_posix()}/post_boot_top_lines.tsv", 'format': 'tsv', 'rows': int(len(top))})
    append_manifest(manifest_entry, base_reports_dir=args.reports_dir)

    # print concise summary to stderr
    print('{"ok":true,"errs":%d,"warns":%d,"batch":"%s"}' % (errs, warns, batch), file=sys.stderr)


if __name__ == '__main__':
    main()
