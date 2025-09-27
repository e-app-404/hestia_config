# ADR change / Workspace hygiene update

Use this template for PRs that introduce or update architecture decision records (ADRs) and workspace hygiene rules.

## Summary
- Brief description of the ADR or hygiene change.

## Files changed
- list changed ADR(s) under `hestia/docs/ADR/`:
  - [ ] ADR-0018-workspace-lifecycle-policy.md

## CI / Checks
- [ ] The `ADR-0018 include-scan` workflow will run in warn-first mode for 30 days. After the grace period, tracked banned paths or tracked backups will cause CI to fail.

## Migration notes
- If this PR moves or untracks files, describe any manual steps reviewers must take to preserve artifacts (e.g., `git rm --cached` or moving to `hestia/vault/backups/`).

## Reviewer checklist
- [ ] Confirm ADR frontmatter and references are correct.
- [ ] Confirm the `hestia/reports/` and `artifacts/` conventions are acceptable.
- [ ] Approve the migration plan and timing for flipping the include-scan to fail.

