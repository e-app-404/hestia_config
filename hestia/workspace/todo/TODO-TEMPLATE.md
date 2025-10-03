---
status: open
created_at: 2025-10-03T00:00:00Z
updated_at: 2025-10-03T00:00:00Z
author: __REPLACE_ME__
agent: __OPTIONAL__  # e.g. copilot
human_owner: __REPLACE_ME__
priority: low  # low|medium|high
labels: []
---

# Title

Short, descriptive title (e.g. "CI: add template provenance check")

## Description

Describe the task or change in plain language.

## Proposed change / patch

Provide a short description of the proposed change. Inline a patch in unified diff format if available under a fenced block, or attach a link to a branch/PR.

```
# Example: small patch
# --- a/file
# +++ b/file
# @@ -1,2 +1,3 @@
# -old
# +new
```

## Files changed

List the repository paths that will be added/modified.

## Test plan

Describe how to validate the change locally and in CI.

## Security / validation tokens

If this todo requires an automated runner to apply privileged changes, note that a short-lived `validation_token` will be required. DO NOT include the token in the todo body; instead include a vault reference or instruction to request it from an owner.

## Notes / references

Link to related ADRs or todos.

## Change log

- 2025-10-03: created (author: __REPLACE_ME__)
