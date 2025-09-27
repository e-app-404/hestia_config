Registry Compactor utilities
===========================

This directory contains utilities and helpers for running a dry-run compaction
of a Home Assistant entity registry. The goal is to safely produce auditable
outputs (prune candidate lists, compacted registry JSON, and summary reports)
without overwriting authoritative input files.

Core scripts
------------
- `compact_registry.py` — the compactor CLI (makes deterministic pruning
	decisions under configured heuristics). It is intended to be run in a dry-
	run mode so results can be audited before any live changes.
- `ops_run_step.sh` — a small-step POSIX runner used to run scenarios with
	per-step logs and a timeout; includes a Python fallback for environments
	missing a `timeout` binary.
- `strip_deleted_entities.py` — sanitizer that trims or drops `data.deleted_entities`
	(tombstones) from a registry JSON while preserving top-level shape. Useful
	to reduce backup size while keeping compaction decisions reproducible.

Integration with ReportKit
-------------------------
If you want compaction runs to publish a tiny provenance report alongside
other audits, use the `hestia.tools.utils.reportkit` helpers. Example snippet
to add into `compact_registry.py` after computing a `summary` dict:

		when = utc_now_id()
		batch = new_batch_dir('hestia/reports', tool='compactor', label='scenarioF', when=when)
		artifact = Path(batch) / 'compactor_summary.json'
		payload = {
				'_meta': {
						'meta_schema':'v1',
						'created_at': when,
						'tool':'compactor',
						'script':'hestia/tools/utils/compactor/compact_registry.py',
						'purpose':'registry cleanup',
						'batch_id': Path(batch).name,
						'input_path': args.input,
						'format':'json',
				},
				'data': summary,
		}
		atomic_write_text(str(artifact), json.dumps(payload, ensure_ascii=False))
		append_manifest({
				'meta_schema':'v1', 'created_at': when, 'tool':'compactor',
				'script':'hestia/tools/utils/compactor/compact_registry.py', 'purpose':'registry cleanup',
				'batch_id': Path(batch).name, 'file_relpath': str(artifact.relative_to('hestia/reports')), 'format':'json',
		})

Safe-run guidance
-----------------
- Never run compactor with an output path identical to the authoritative `precompact` file.
- Use the sanitizer `strip_deleted_entities.py` if you need to preserve pruning decisions while
	reducing backup size; it preserves the `data.deleted_entities` key as an empty list when
	dropping tombstones.
- Produce audit TSVs (kept/pruned lists) and verify them before applying any changes.

Validation & auditing
---------------------
- Use the audit scripts under `hestia/tools/utils/audit/` to produce `pruned_entities.tsv`,
	`kept_entities.tsv`, and `quick_counts.json` that summarize compaction decisions.
- Use ReportKit's `verify_frontmatter.py` to check checksums for any TSV/CSV artifacts.

Commands (examples)
--------------------
Create a sanitized registry (no tombstones):

```sh
python3 strip_deleted_entities.py --drop-all --in registry/core.entity_registry.precompact.json --out registry/core.entity_registry.nodel.json
```

Run compactor scenario F using the step runner:

```sh
PYTHONPATH=$(pwd) sh ops_run_step.sh F --input registry/core.entity_registry.nodel.json --out report_F.json
```

Bundle artifacts for offline export:

```sh
tar -C registry -czf /tmp/registry_final_bundle_v3.tgz core.entity_registry.canonical.json core.entity_registry.nodel.json final_candidate.json report_F.json audit/*.tsv hestia/reports/_index.jsonl
```

Notes
-----
- These scripts are implemented to be portable and use only the Python stdlib.
- The recommended workflow is: sanitize -> dry-run compactor -> audit diffs -> bundle
	and inspect on an offline workstation before any live copy to the HA host.

