Hestia Workspace Todo/Tickets
=========================

Location
--------
All Copilot/GPT and human patch requests / operational todos live under:

`hestia/workspace/todo/`

Why
---
This directory centralizes requests for changes to configs, templates, and operational artifacts in a human-readable, git-tracked format. It is intentionally simple: each todo is a markdown file with a defined metadata header and a structured body.

How to open a todo
--------------------
1. Copy `TODO_TEMPLATE.md` into a new filename prefixed with a zero-padded sequence: `0002-short-slug.md`.
2. Fill in the required fields (title, author, human_owner, status, priority, description, proposed_patch, test_plan).
3. Commit the new file and open a PR referencing the todo filename in the PR description.

AI / Agent guidelines
---------------------
- When an AI agent drafts a todo, include `agent: copilot` and a `human_owner:` field with a GitHub username or local maintainer.
- Do not include secrets or validation tokens in the todo body. If a token is required, store it in a secure vault and reference it only by ID in the todo.

Filenames
---------
Use filenames like `0001-ci-regression-checks.md`.

Status lifecycle
----------------
- `status: open` — todo filed and awaiting triage.
- `status: in-progress` — human or agent is actively working on the change.
- `status: blocked` — waiting on external input.
- `status: closed` — work complete; include `closed_at:` and `resolution:`.

Maintainers
-----------
The `hestia` workspace maintainers are the initial owners of this directory. 

