chore(workspace): parameterize HA_MOUNT; add guard + samples (ADR-0016)

Summary

Normalize the developer workspace so it no longer depends on a hard-coded /n/ha path. Add guardrails to prevent regressions. Aligns with ADR-0016 — Canonical HA SMB mount and formatting rules in ADR-0009.

Scope

Developer-local ergonomics and repo guardrails only. No runtime HA behavior changes.

What changed
	•	Validator hestia/tools/validators/scan_hardcoded_ha.sh
	•	Flags hard-coded /n/ha outside docs; uses rg with a grep fallback.
	•	CI guard .github/workflows/hardcoded-ha-guard.yml
	•	Runs the validator on every push/PR.
	•	Env sample .env.sample
	•	export HA_MOUNT="${HA_MOUNT:-$HOME/hass}" (safe, parameterized default).
	•	VS Code sample .vscode-configs/config-lean.sample.code-workspace
	•	Uses ${workspaceFolder}; no absolute /n/ha.
	•	Docs
	•	hestia/docs/ADR/ADR-0016-canonical-ha-smb-mount.md — Implementation section references the workspace sample.
	•	.vscode-configs/README.md — how to use the sample workspace locally.

Local pre-commit hook was demonstrated but is intentionally not tracked. Developers may opt-in.

Why
	•	Make the repo portable across machines while preserving the architectural contract that /n/ha is canonical in docs/ADRs.
	•	Prevent accidental reintroduction of hard-coded /n/ha in scripts.

Verification (local)

# 1) Validator
./hestia/tools/validators/scan_hardcoded_ha.sh

# 2) (optional) Local pre-commit guard
mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'H'
#!/usr/bin/env bash
set -e
hestia/tools/validators/scan_hardcoded_ha.sh
H
chmod +x .git/hooks/pre-commit

# 3) Sanity test: fail then pass
echo '/n/ha' > hestia/tools/one_shots/_tmp_guard_probe.sh
git add hestia/tools/one_shots/_tmp_guard_probe.sh
git commit -m "probe: expect guard to fail" || echo "✅ blocked as expected"
git reset -q
rm -f hestia/tools/one_shots/_tmp_guard_probe.sh

# 4) Developer setup (local only; not committed)
cp -n .env.sample .env
# VS Code: open .vscode-configs/config-lean.sample.code-workspace

Risk & Rollback
	•	Low risk (docs, samples, guards).
	•	Rollback: revert the merge commit.

Acceptance checklist
	•	CI “Hardcoded /n/ha guard” workflow passes on this PR.
	•	Local validator prints “OK: no hard-coded /n/ha outside docs”.
	•	.env remains untracked; .env.sample committed.
	•	config-lean.sample.code-workspace opens with ${workspaceFolder} paths (no absolute /n/ha).
	•	ADR-0016 Implementation references the workspace sample and remains consistent with ADR-0009 formatting.
	•	(Optional) Local pre-commit hook blocks a simulated /n/ha re-introduction and allows commits after cleanup.

Follow-ups (separate PRs)
	•	Parameterize selected shell scripts to read HA_MOUNT from environment (keep ADRs/docs unchanged).
	•	Optionally add a tracked tools/dev/setup-hooks.sh to install the local pre-commit hook for contributors.
