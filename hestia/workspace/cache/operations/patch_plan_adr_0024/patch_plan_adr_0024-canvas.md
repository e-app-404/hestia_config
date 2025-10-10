# Patch Plan (Authoritative Execution Guide)

This plan makes the repo, hosts, and CI comply with ADR-0024 and ensures there is **no conflicting information** for machine parsers.

## P0 — Repo Hardening (code & CI)

1. **Add helpers** `bin/require-config-root` and `bin/lint-paths.sh`; mark executable.
2. **Wire CI**: add a job that runs the linter before tests/builds.
3. **Replace legacy paths in code**: one-time sweep replacing `~/hass`, `$HOME/`, `/Volumes/HA/Config`, `/n/ha`, and actions-runner-specific roots → `/config` (code only; not in `ADR/deprecated/**` or `docs/history/**`). Create `.bak` backups as needed.
4. **Remove HOME-stabilizers** that attempted to rewrite `$HOME` in scripts. Replace with `require-config-root`.

## P1 — Documentation & ADR State

1. **Create `ADR/deprecated/`** if it does not exist.
2. **Move:** ADR-0016, ADR-0010, ADR-0012 → `ADR/deprecated/`.
3. **Update front-matter** of moved ADRs: `status: Superseded`, `superseded_by: ADR-0024`.
4. **Amend** ADR-0015, ADR-0019, ADR-0014, ADR-0022 with an addendum referencing ADR-0024; ensure examples use `/config`.
5. **Add an index** entry linking ADR-0024 as the canonical path policy (if using adr-tools, run `adr generate toc`).

## P2 — macOS Operator Host Setup

1. Create backing directory: `/System/Volumes/Data/homeassistant`.
2. Add `config\thomeassistant` (and optional `homeassistant\thomeassistant`) to `/etc/synthetic.conf`.
3. Materialize entries: `sudo automount -vc` (or reboot).
4. Mount SMB share at login to the Data path via LaunchAgent.

## P2 — GitHub Actions & Containers

1. Prefer container jobs with `volumes: ${{ github.workspace }}:/config`.
2. If host-runner is mandatory, add the bind-mount step shown above.

---

## Patch Instructions (Concrete Commands)

> Run from the repo root. Adjust paths if your structure differs.

**1) Add helpers**

```bash
mkdir -p bin
install -m 0755 -D -T /dev/stdin bin/require-config-root <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[ -d /config ] && [ -r /config ] || { echo 'Missing or unreadable /config' >&2; exit 2; }
EOF

install -m 0755 -D -T /dev/stdin bin/lint-paths.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
PATTERN='\$HOME/|~/hass|/Volumes/|/n/ha|actions-runner/.+?/hass'
if rg -nE "$PATTERN" --hidden --glob '!**/*.md' --glob '!ADR/deprecated/**' --glob '!docs/history/**' .; then
  echo 'ERROR: Disallowed path alias detected. Use /config only.' >&2
  exit 1
fi
EOF
```

**2) CI job (GitHub Actions)**

```yaml
# .github/workflows/ha-ci.yml
name: ha-ci
on: [push, pull_request]
jobs:
  lint-and-validate:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/home-assistant/home-assistant:stable
      volumes:
        - ${{ github.workspace }}:/config
    steps:
      - uses: actions/checkout@v4
      - name: Path guard
        run: /config/bin/lint-paths.sh
      - name: Validate HA config
        run: ha core check
```

**3) Repo-wide replacement (code only)**

```bash
# Review-only first
rg -nE '\$HOME/|~/hass|/Volumes/HA|/n/ha|actions-runner/.+?/hass' --hidden \
  --glob '!**/*.md' --glob '!ADR/deprecated/**' --glob '!docs/history/**'

# Replace `$HOME/` → `/config/` for scripts likely to touch HA
fd -t f . | xargs -I{} perl -0777 -i.bak -pe 's|\$HOME/|/config/|g' {}
# Replace `~/hass` → `/config`
fd -t f . | xargs -I{} perl -0777 -i -pe 's|~/hass|/config|g' {}
# Replace legacy mount aliases → `/config`
fd -t f . | xargs -I{} perl -0777 -i -pe 's|/Volumes/HA/Config|/config|g;s|/n/ha|/config|g' {}
```

**4) Remove HOME stabilizers from scripts**

```bash
# Example: drop REAL_HA_PATH, HA_MOUNT, HOME_SAFE rewrites and replace with:
. "$(git rev-parse --show-toplevel)/bin/require-config-root"
```

**5) Deprecate conflicting ADRs**

```bash
mkdir -p ADR/deprecated
for n in 0016 0010 0012; do
  git mv ADR/ADR-$n*.md ADR/deprecated/ || true
  # Update front-matter in each moved file accordingly (manual edit or sed)
  # status: Superseded
  # superseded_by: ADR-0024
done
```

**6) Amend related ADRs**

* Edit ADR-0015, ADR-0019, ADR-0014, ADR-0022 to reference ADR-0024 and update examples to `/config`.

**7) macOS host**

```bash
sudo mkdir -p /System/Volumes/Data/homeassistant
printf 'config\thomeassistant\n' | sudo tee -a /etc/synthetic.conf
sudo automount -vc
# Mount at login (add LaunchAgent that runs `mount_smbfs` to the Data path)
```

---

## Validation Plan (Definition of Done)

**Operator macOS**

* `test -d /config && test -w /config` returns success.
* `realpath /config` equals `/System/Volumes/Data/homeassistant`.

**Home Assistant container/host**

* `ls /config/.storage` succeeds.
* `ha core check` passes under a job with `/config` as working directory.

**CI**

* Linter passes (no occurrences of disallowed paths in code).
* `ha core check` passes in container job.

**Repository**

* ADR-0024 present; ADR-0016/0010/0012 moved to `ADR/deprecated/` with updated front-matter.
* Amended ADRs reference ADR-0024 and use `/config` examples.

---

## Open Items & Next Steps (finite closure)

1. **macOS LaunchAgent plist**: Provide or confirm the exact plist used to mount the SMB share at login to the Data path. *Next step:* add `~/Library/LaunchAgents/com.ha.mount-config.plist` that runs `mount_smbfs` pointing to `/System/Volumes/Data/homeassistant`.
2. **Windows operator (if any):** Not currently in scope. *Next step:* mirror this policy via WSL2 or a drive mapping that presents `/config` inside the working shell (e.g., bind-mount `X:\config` → `/config` in containers).
3. **ADR index automation:** If using adr-tools, regenerate the TOC. *Next step:* run `adr generate toc` (or equivalent) and verify links.
4. **Legacy artifacts in docs:** Historical examples may still show `~/hass`. *Next step:* move those to `docs/history/**` and ensure the path-lint excludes only that folder.

Each item above requires a single, bounded action: (a) create one plist; (b) configure one mapping (if Windows is needed); (c) run one indexing command; (d) move and edit legacy docs. No ongoing maintenance is expected once completed.