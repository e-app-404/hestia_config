Core config artifacts (extracted snapshots, connectivity maps, generated previews)
--------------------------------------------------------------------------

Purpose:
- `hestia/core/config/` stores machine-consumable artifacts discovered from the
  environment (extracted device configs, generated topology, connectivity maps).
- Files here are intended for indexing (see `index/hades_config_index.yaml`) and
  CI validation (yaml_load, path_exists, tag_policy).

Naming and placement rules:
- `<device>.extract.cfg` — device-level extracted snapshot (machine-friendly).
- `connectivity/*.yaml` — tailscale/mullvad related artifacts.
- `network/*.yaml` — topology, vlans, dhcp/dns configs.

Retention:
- These artifacts may be rotated; treat them as canonical discovery outputs. Move
  older snapshots to `vault/backups/` when archiving.
