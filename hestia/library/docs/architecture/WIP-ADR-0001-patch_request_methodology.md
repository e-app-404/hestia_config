---
Status: WIP
Date: 2025-10-03
Authors: Hestia contributors (drafted by Copilot)
---

# WIP ADR-0001: Patch request methodology & AI/agent todo workflow

Context
-------
Developers and automated agents (Copilot/GPT) will propose code or configuration changes to the Hestia workspace. We need a lightweight, auditable, and secure method for proposing, reviewing, and applying patches — especially when human and AI agents interact.

Goals
-----
- Define a canonical place to drop patch requests / todos.
- Provide a robust todo template for any proposed change (human or agent-originated).
- Define protocols for validation tokens and reviewer interactions when an AI suggests a patch.
- Ensure the process is adaptable and auditable (timestamps, authorship, review status).

Canonical todo location
-------------------------
We define the canonical location for todos as:

`hestia/workspace/todo`

Rationale: this location fits the existing workspace layout (`hestia/workspace/todo`) and keeps todos alongside generated operational artifacts and logs.

Todo ticket lifecycle and file naming
-------------------------------
- New todos are added as markdown files using the todo template. Filenames MUST be prefixed with a zero-padded sequence number and short slug, e.g. `0001-ci-regression-checks.md`.
- Todos should live as individual markdown files. When a todo is closed, update the `status:` field rather than deleting.

Todo ownership and review
---------------------------
- Each todo must include an `author:` field. AI-generated todos must include `agent: copilot` (or agent name) and `human_owner:` to indicate the human responsible for shepherding the change.
- Reviewers should add `reviewer:` and `review_status:` fields. A PR should reference the todo filename in its description.

Validation tokens and secure operations
--------------------------------------
- For sensitive or automatic patch application pipelines, todos may include an optional `validation_token:` field. Tokens are short-lived and signed by a trusted operator; how tokens are generated and distributed should be handled out-of-band (for now, document as a placeholder).
- Tokens allow automated runners to confidently apply patches for low-risk changes. High-risk changes require human-reviewed PRs.

AI/agent-specific recommendations
---------------------------------
- Agents must not directly push changes to long-lived branches unless explicitly authorized by a human reviewer.
- Agents are encouraged to create fully self-contained todos with proposed patches (diff inlined or linked) and test steps. The todo template (see `hestia/workspace/todo/TODO_TEMPLATE.md`) supports an area to paste a patch.

Security & auditability
-----------------------
- Each todo must carry an audit header: `status: open|in-progress|closed`, `created_at:`, `updated_at:`, `author:`, `agent:` (optional), `human_owner:`.
- Keep todos under source control. Todo ticket changes and history are visible in the git log for auditing.

Next steps
----------
- Implement the todos directory and template (done in a companion README and template file).
- Decide policy for validation tokens and automated application of low-risk patches.
- Add a small helper script to render todos into PR bodies and to create branches automatically (future work).

Appendix: Minimal example todo naming
--------------------------------------
`hestia/workspace/operations/todos/0001-ci-regression-checks.md`

