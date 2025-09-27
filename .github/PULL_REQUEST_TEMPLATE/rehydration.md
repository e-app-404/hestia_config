# Rehydration Seed / Metadata Submission

Use this PR template when submitting a rehydration seed (session metadata, artifact index, or consolidated rehydration file).

## What this PR contains
- [ ] meta/rehydration/<id>/consolidated_rehydration.yaml
- [ ] meta/rehydration/<id>/rehydration_seed.yaml
- [ ] meta/rehydration/<id>/artifact_index.yaml
- [ ] Other supporting files (docs, patches)

## Why
Explain briefly the purpose of the seed and what it enables (rehydration, archival, patch replay).

## How CI validates
- The `Rehydration seed validation` workflow will check:
  - Presence of `consolidated_rehydration.yaml`
  - YAML parse validity
  - Minimal structure keys: `session_recap`, `artifacts`, `phases`, `memory_vars`, `rehydration_seed`

## Checklist before requesting review
- [ ] Consolidated YAML exists and parses locally
- [ ] Sensitive secrets are not included in the seed
- [ ] Artifacts referenced by the seed are either included or clearly documented as external references

## Reviewer notes
Provide any extra context reviewers will need. If you expect the PR to be merged and the seed used by automation, note that here and include any suggested verification steps.
