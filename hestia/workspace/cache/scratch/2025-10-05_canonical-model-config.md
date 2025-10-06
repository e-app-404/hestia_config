# Canonical model (simple + stable)

* **Docs & HA internals:** always refer to `/config`.
* **Scripts:** use a tiny resolver so they work *anywhere* but still prefer `/config`.

`hestia/lib/_ha_config_root.sh`

```bash
# Prefer the canonical /config; fall back only if missing.
if [ -z "${HA_CONFIG_ROOT:-}" ] && [ -f /config/configuration.yaml ]; then
  export HA_CONFIG_ROOT=/config
fi
if [ -z "${HA_CONFIG_ROOT:-}" ]; then
  for c in "$HOME_SAFE/hass" "$HOME/hass" "$PWD"; do
    [ -f "$c/configuration.yaml" ] && export HA_CONFIG_ROOT="$c" && break
  done
fi
[ -n "${HA_CONFIG_ROOT:-}" ] || { echo "HA_CONFIG_ROOT not found"; exit 2; }
```

Then call tools like:

```bash
. "/Users/evertappels/hass/hestia/lib/_ha_config_root.sh"
"$HA_CONFIG_ROOT/tools/ha_git_push.sh" "$HA_CONFIG_ROOT"
```

# Make `/config` exist in each place

## macOS (your laptop) — persistent and safe

```bash
REAL_HA_PATH="/Users/evertappels/hass"   # adjust if needed
sudo sh -c 'printf "config\t%s\n" "'"$REAL_HA_PATH"'" > /etc/synthetic.conf'
echo "Reboot to materialize /config"
```

## Self-hosted runner

* **If you have sudo:**
  **Linux:**

  ```bash
  sudo mkdir -p /config
  sudo mount --bind "$GITHUB_WORKSPACE/hass" /config
  ```

  **macOS:** use the same `synthetic.conf` approach, or `bindfs` if you have macFUSE.
* **If you don’t have sudo:** run scripts via the resolver above; `/config` stays canonical in code, and dev/CI uses `HA_CONFIG_ROOT` fallback transparently.

## Containerized CI (cleanest for GitHub Actions)

```yaml
jobs:
  check:
    runs-on: ubuntu-latest
    container: ghcr.io/home-assistant/home-assistant:stable
    steps:
      - uses: actions/checkout@v4
      - name: Map repo as /config
        run: |
          mkdir -p /config
          cp -a "$GITHUB_WORKSPACE/hass/." /config/
      - name: Validate
        run: ha core check
```

(or run the container with a `-v ${{ github.workspace }}/hass:/config` volume if your runner supports it.)

# Quick repo hygiene (kill the drift)

* **Policy:** no more absolute host paths in code; use `/config` (or `$HA_CONFIG_ROOT` from the resolver) only.
* **Preview what to replace:**

```bash
rg -n --hidden -S '/Users/evertappels|~/hass|/Volumes/HA/Config|/Volumes/Config|/n/ha' \
  -g '!**/*.md' -g '!**/docs/**'
```

* **Then fix intentionally (after reviewing the hits).**

That’s it: agree on `/config` as the canonical interface, make it exist on macOS + CI, and keep the tiny resolver as a guardrail. No more path drift, no more “machines revolt.”
