You are patching our HA path normalization work. Apply the following edits and additions exactly.

FILES TO EDIT (relative to repo root):
1) hestia/workspace/cache/scratch/patch-plan-adr-0024-R2-bundle.md
2) hestia/workspace/cache/scratch/patch-plan-adr-0024-touchpoints.md
3) hestia/workspace/cache/scratch/patch_plan_adr_0024-canvas.md
4) ADR/ADR-0024*.md  (Appendix A only)

A) Fix synthetic.conf lines
- In (1) and (2), replace every line "config\tSystem/Volumes/Data/homeassistant" with "config\thomeassistant".
- In (2), replace "config\tSystem/Volumes/Data/Users/evertappels/homeassistant" with "config\tUsers/evertappels/homeassistant".
- Keep the ADR canvas plan’s "config\thomeassistant" as-is.

B) Remove symlink assumptions
- In (2) section “Minimal smoke test”, replace the entire script with:

  #!/usr/bin/env bash
  set -euo pipefail
  [[ -d /config ]] || { echo "FAIL: /config not a directory"; exit 1; }
  python3 - <<'PY'
  import os; p="/config"
  assert os.path.isdir(p), "/config not a directory"
  print("OK:", os.path.realpath(p))
  PY
  echo "OK: directory check passed"

- In any verification lines using `readlink /config`, remove them or replace with `python3 -c 'import os; print(os.path.realpath("/config"))'`.

C) CI snippets
- In (2) and (1), replace Linux host-runner step that symlinks `/config` with the bind-mount version:

  - name: Ensure /config (Linux host-runner)
    if: runner.os == 'Linux' && !startsWith(matrix.container, 'ghcr.io/home-assistant')
    run: |
      set -euo pipefail
      sudo mkdir -p /config
      sudo mount --bind "$GITHUB_WORKSPACE" /config
      [[ -d /config ]] && ls -ld /config

- Ensure the container-first job remains unchanged.

D) Devcontainer
- In (2) devcontainer JSON, change mounts to target `/config` directly and remove any postCreate symlink:

  "mounts": ["source=${localWorkspaceFolder},target=/config,type=bind,consistency=cached"]

E) Compose example
- In (2), change volume mapping from "/homeassistant:/config" to "/System/Volumes/Data/homeassistant:/config".

F) Guard & scripts
- Create file tools/lib/require-config-root.sh with the robust, RO-aware guard:

  [paste the guard from section E verbatim]

- Create file tools/fix_path_drift.sh with the narrowed replace and BSD sed fallback:

  [paste the script from section F verbatim]

- Create/replace tools/lint_paths.sh with the hardened glob logic:

  [paste the script from section G verbatim]

G) ADR-0024 Appendix A
- In ADR-0024, update Appendix A to:
  - Reference `tools/lib/require-config-root.sh` instead of `bin/require-config-root`.
  - Replace the simple guard with the RO-aware guard from section E.

H) Make all three scripts executable:
- chmod +x tools/lib/require-config-root.sh tools/fix_path_drift.sh tools/lint_paths.sh

I) Commit message:
- feat(adr-0024): align patch plans + guard/linter; firmlink-safe, CI bind /config; devcontainer direct bind; compose realpath
