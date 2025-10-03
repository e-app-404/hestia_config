Todos & Patch Requests - README (Hestia workspace)
====================================================

Purpose
-------
This README explains where to place todos, patch requests, and how AI agents and humans should interact when proposing changes to the Hestia workspace.

Location
--------
- Todos: `hestia/workspace/todos/`
- Patch submission guidelines: include patches inline in todos or attach PR links.

Patch request flow
------------------
1. Create a todo using the `TODO_TEMPLATE.md` and place it in the todos directory with the `000N-` prefix.
2. Add `human_owner` and `author` fields. If an AI created the todo, include `agent: copilot`.
3. For low-risk changes, include a `proposed_patch` diff in the todo. For higher-risk changes, propose a branch/PR and link it in the todo.
4. A human reviewer should assign `reviewer` and change `status` to `in-progress` when work begins.

Agent operation protocol
------------------------
- Agents may create todos but must not merge PRs without human approval.
- Agents may request a short-lived validation token (documented in the todo) to allow automated runners to apply trivial patches; token creation and distribution is out-of-band.

Audit & validation
------------------
- All todos are tracked in git for auditability.
- Todos must not contain secrets. If secrets are needed, store them in the vault and reference securely.

Contact
-------
Assign `human_owner` in todos to indicate who will shepherd the change.