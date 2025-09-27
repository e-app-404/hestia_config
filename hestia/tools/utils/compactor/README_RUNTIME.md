Runtime notes — promote, rollback, and safe usage
================================================

Runtime-safe vs Requires downtime
--------------------------------
- Runtime-safe: Using `promote_registry.sh` to atomically swap a candidate
  `core.entity_registry` into place. This is intended to be safe while Home
  Assistant is running, but you should still be cautious: swapping the
  registry can cause temporary inconsistencies in the frontend or entity
  resolution until HA re-reads the file.

- Requires downtime: Any manual edits to hardware device files, or operations
  that require stopping the Home Assistant process to avoid writes to the
  `.storage` directory.

Promote command (safe, BusyBox-friendly)
---------------------------------------
From the offline workstation or copied candidate file on the HA host:

```sh
sh hestia/tools/utils/compactor/promote_registry.sh /path/to/final_candidate.json /config
```

What it does:
- Verifies the candidate exists and `.storage` directory exists
- Backs up `/config/.storage/core.entity_registry` to `/config/.storage/core.entity_registry.<TIMESTAMP>.bak`
- Copies the candidate to `/config/.storage/core.entity_registry`
- Runs `chmod 600` on the new file and calls `sync`
- Prints file size and the first line for a quick sanity check

Rollback snippet
----------------
If you need to revert to the backup produced by the promote step:

```sh
# on HA host
BACKUP=/config/.storage/core.entity_registry.<TIMESTAMP>.bak
cp "$BACKUP" /config/.storage/core.entity_registry
chmod 600 /config/.storage/core.entity_registry
sync
```

Run compactor dry-run from macOS (offline)
-----------------------------------------
From your offline workspace root:

```sh
PYTHONPATH=$(pwd) python3 -m hestia.tools.utils.compactor.cli compact \
  registry/core.entity_registry.nodel.json --out final_candidate.json --cap-trim-threshold 4096 --effect-list-max 50
```

Then verify and promote via the promote script above.
