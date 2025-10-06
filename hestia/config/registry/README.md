room_registry.yaml — conversion notes

What changed
- On 2025-10-05 the `room_registry.yaml` file was converted from a list-of-single-key mappings
  shape into mappings keyed by `area_id` (the area slug). This avoids misinterpretation by linters
  and editors that expect keyed mappings and improves schema validation.

Backups
- Multiple backups were created next to the original file with UTC timestamps:
  - `room_registry.yaml.bk.20251005T105804Z`
  - `room_registry.yaml.bk.20251005T110028Z`
  - `room_registry.yaml.bk.finalizing.20251005T110101Z`

How to re-run the conversion
- A small Python script was used during the automated patch process. To re-run locally (uses the
  workspace Python environment):

```bash
# from the workspace root
python -c "import pathlib,yaml,shutil,datetime; p=pathlib.Path('hestia/config/registry/room_registry.yaml'); shutil.copy2(p, p.with_suffix('.yaml.bk.'+datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'))); print('backup created'); ..."
```

- If you'd like the exact script used, tell me and I will add it under `hestia/tools/` as a small utility with --dry-run and --apply flags.

Notes
- The conversion preserves ordering via a `__order` key in each converted mapping. If you'd prefer
  a different mechanism for ordering (e.g. kept as a top-level list) I can update the conversion.
- No data was removed; ambiguous entries were preserved under `__still_unconverted` if they lacked
  a discoverable area id.
