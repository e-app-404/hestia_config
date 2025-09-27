ReportKit — small, atomic, self-describing reporting helpers
===========================================================

What this is
-------------
ReportKit is a tiny stdlib-only helper collection used to write deterministic,
atomic, self-describing report artifacts into a repository-local `hestia/reports/`
tree. It is intentionally minimal and BusyBox-friendly so it can run on
constrained Home Assistant environments.

Key features
-------------
- Create time-grouped batch directories under `hestia/reports/YYYYMMDD/`.
- Write TSV/CSV/MD artifacts with commented frontmatter (YAML-like) and a
	checksum that covers the data body (not the header).
- Write JSON reports that embed a `_meta` object.
- Append a single-line NDJSON manifest at `hestia/reports/_index.jsonl` with
	repo-relative `file_relpath` references.
- Atomic writes (temp file in same dir -> fsync -> os.replace) and best-effort
	strict file permissions (mode `0o600`).
- BusyBox-safe manifest locking via O_CREAT|O_EXCL `.index.lock` with retry up
	to 2s.

Why use it
----------
If you need reproducible, auditable report artifacts that are safe to publish
from an offline workstation and ingestable on a Home Assistant host, ReportKit
provides a small, self-contained convention:

- Each artifact carries human-readable metadata in a well-known place.
- A single append-only manifest provides fast indexing and retention queries.
- Atomic semantics and strict permissions make accidental overwrites and
	information leaks less likely.

Core helpers
------------
All helpers live in `hestia.tools.utils.reportkit.reportkit`.

- utc_now_id() -> str
	- Returns UTC timestamp id like `20250926T164453Z`. If called multiple
		times within the same second the function appends `__2`, `__3`, etc. (mono-
		tonic per-process guarantee).

- new_batch_dir(base_dir, tool, label, when=None) -> str
	- Creates `hestia/reports/YYYYMMDD/<when>__<tool>__<label>/` and returns the
		directory path. Also updates `hestia/reports/latest` symlink (best-effort).

- write_tsv_with_frontmatter(path, meta, header, rows)
	- Writes a commented frontmatter block (lines starting with `# `), then the
		header and body. Computes sha256 over the body only and stores it in the
		frontmatter key `checksum_sha256`. Uses atomic write and sets mode `0o600`.

- write_json_report(path, meta, data)
	- Writes `{"_meta": meta, "data": data}` as JSON (NDJSON-style trailing
		newline). Uses atomic write and sets mode `0o600`.

- append_manifest(entry, base_reports_dir='hestia/reports')
	- Append the provided mapping as a compact, single-line JSON to
		`hestia/reports/_index.jsonl`. The manifest write uses a `.index.lock`
		O_EXCL lock with retries up to 2s and fsync on the manifest file.

Manifest conventions
--------------------
Each manifest line is a JSON object with at least these keys:

- meta_schema: 'v1'
- created_at: timestamp from `utc_now_id()`
- tool: the producing tool name (string)
- script: repo-relative script path that created the file (string)
- purpose: human short purpose (string)
- batch_id: the batch dir name (string)
- file_relpath: repo-relative path under `hestia/reports` (POSIX-style)
- format: 'tsv'|'json' etc.
- rows: optional integer row count

The manifest is intended to be append-only; `append_manifest()` will not
attempt to remove or mutate old entries.

Security & permissions
----------------------
All files written by ReportKit are set to mode `0o600` where the system
permits it. The manifest itself is also set to `0o600` after writes. These are
best-effort operations: some constrained hosts may ignore chmod or have
different semantics; the code ignores chmod failures rather than failing the
write.

Frontmatter checksum semantics
------------------------------
Report files (TSV/CSV/MD) include a commented frontmatter block. The checksum
stored in `checksum_sha256` is the SHA256 of the data body only — that is,
everything after the frontmatter comments. Use `verify_frontmatter.py` to
recompute the body hash and compare.

Utilities included
------------------
- `verify_frontmatter.py --file <path>` — parses the frontmatter and recomputes
	the body SHA256; prints JSON `{file, meta, body_sha256, match}`.
- `retention.py` — CLI to scan `_index.jsonl` and delete batch dirs older than
	a TTL (dry-run supported, requires `--yes` to actually delete). The manifest
	remains append-only.

Example quick-flow
------------------
Write a small audit that uses ReportKit:

1) Create a batch and compute results:

		when = utc_now_id()
		batch = new_batch_dir('hestia/reports', tool='audit', label='chatty', when=when)

2) Write TSV with frontmatter:

		meta = { 'meta_schema':'v1', 'created_at': when, 'tool':'audit', 'script':'hestia/tools/utils/audit/parse_top_chatty_entities.py', 'purpose':'diagnostic', 'batch_id': Path(batch).name, 'input_path': 'sample_home-assistant.log' }
		write_tsv_with_frontmatter(os.path.join(batch,'top_entities.tsv'), meta, 'name\tcount', rows_text)

3) Append manifest entries:

		append_manifest({ **meta, 'file_relpath': f"{Path(batch).relative_to('hestia/reports').as_posix()}/top_entities.tsv", 'format':'tsv', 'rows':9 })

Notes and testing
-----------------
- Use `verify_frontmatter.py` to validate checksums locally before copying
	artifacts to a live Home Assistant host.
- The `append_manifest()` lock uses a short retry loop (2s). If you have
	parallel processes writing many entries, consider batching appends or adding
	small jitter between attempts.

License and compatibility
-------------------------
This code uses only the Python standard library and targets Python 3.10+.
It is suitable for running on Home Assistant hosts that offer a Python
interpreter and a POSIX-like filesystem. The code avoids exotic dependencies
and uses conservative filesystem operations to maximize portability.

