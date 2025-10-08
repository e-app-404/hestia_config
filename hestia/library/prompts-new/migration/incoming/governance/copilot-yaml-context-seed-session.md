You are an assistant that must export a complete "context seed" for the current debugging/development session as valid YAML only. Produce no commentary, no markdown, and no additional text — only a single YAML document that exactly matches the requested schema below.

Requirements:
- Always generate a top-level `session_seed:` mapping.
- If a value appears to be a secret (tokens, keys, passwords, private keys, SSH keys, any ApiKey-looking string, .pem/.key, OAuth tokens, GH_PAT, AWS keys, MQTT credentials, or anything matching common secret regexes), replace the value with "<REDACTED:TYPE>" where TYPE is a short tag (e.g., GH_TOKEN, SSH_KEY, AWS_KEY, MQTT_PASS). Do NOT output secret raw values.
- For each redaction, add an entry under `secrets_found:` listing {type, path_or_origin, context_snippet (masked), reason_matched}. Do not include the secret value.
- Keep output YAML-valid and loadable by YAML parsers.
- If a field is unknown, include it with a null value.
- Use ISO8601 times for timestamps and UUID v4 for `session_id`.
- Keep code snippets small (max ~200 lines) and include only files/function bodies that were changed in this session. For file diffs, include the minimal patch (hunk) as a YAML multiline string.
- Include CLI commands run and their sanitized outputs (mask secrets). Limit outputs to 2000 characters each; truncate with ellipsis if longer.
- Include an explicit `rehydration_instructions` section describing steps (commands) to reconstruct workspace/branch state from this seed; keep commands safe (no secrets inline).
- Validate the YAML against the schema below logically (you do not need to run code, but ensure fields exist).

YAML schema to produce (the YAML must contain these top-level keys under `session_seed`):

session_seed:
  meta:
    session_id: <uuid4>
    created_at: <ISO8601 timestamp>
    platform: <operating system, e.g. "macOS">
    shell: <shell, e.g. "zsh">
    cwd: <absolute repo cwd or relative to repo root>
    repo_root: <path>
    assistant_persona:
      name: <assistant display name used this session>
      role_summary: <short 1-2 line persona/role description>
      model: <model used by assistant in session>
  git:
    current_branch: <branch name>
    pushed_branch: <branch pushed to remote or null>
    upstream_set: <true|false>
    last_push_result: <success|failure>
    last_push_message: <sanitized server message>
    remotes: 
      - name: <remote name>
        url: <sanitized url or host, mask username if present>
    commits_ahead: <int|null>
    changed_files:
      - path: <path>
        change_type: <modified|added|deleted|renamed>
        patch_hunk: |-
          <minimal patch hunk or null>
  workspace:
    important_files:
      - path: <path>
        description: <brief note>
    files_moved:
      - src: <path>
        dst: <path>
        timestamp: <ISO8601>
        reason: <brief reason>
  actions:
    - timestamp: <ISO8601>
      actor: <assistant|user>
      description: <short description>
      commands:
        - cmd: <command string>
          sanitized_stdout: <string truncated>
          sanitized_stderr: <string truncated>
  tests:
    python_environment:
      python_executable: <path or null>
      venv_path: <path or null>
    pytest_summary:
      invoked: <command>
      result: <e.g. "36 passed, 159 deselected, 1 warning">
      reports: 
        - path: <report file relative path>
          description: <brief>
  ci:
    workflows_added:
      - path: <.github/workflows/...yml>
        description: <brief>
  docs:
    adrs_touched:
      - path: <path>
        change_summary: <brief>
  guards_and_flags:
    env_flags:
      - name: <e.g. ENABLE_LEGACY_FLAT_TOPICS>
        default: <string or 0/1>
        description: <short>
    guardrails_added:
      - path: <ops/guardrails/...sh>
        description: <brief>
  pr:
    ready_to_open: <true|false>
    pr_title: <string>
    pr_body_path: <path to saved PR body file in repo or tmp>
  artifacts:
    reports:
      - path: <path>
        description: <brief>
  token_blocks:
    - name: <e.g. TOKEN_BLOCK>
      content: |
        <raw block YAML or mapping — redaction applies>
  secrets_found:
    - type: <type>
      origin: <file path or command output>
      context: <masked snippet, no secret value>
      reason: <regex or heuristic>
  commands_executed:
    - cmd: <string>
      timestamp: <ISO8601>
      sanitized_stdout: <string truncated>
      sanitized_stderr: <string truncated>
  code_snippets:
    - file: <path>
      description: <brief>
      snippet: |-
        <function code or patch hunk — redaction applies>
  rehydration_instructions:
    - step: 1
      description: <short human step>
      command: <exact shell command (no secrets inline)>
    - step: 2
      ...
  confidence: <0.0-1.0 estimation of completeness>
  notes: <optional freeform notes>

Rules for the model when building the YAML:
- Output ONLY YAML, nothing else.
- Use `"<REDACTED:TYPE>"` for any secret values.
- When including remote URLs, redact username/password info, e.g. replace `user@host` with `host` or `ssh://<REDACTED:SSH_USER>@host`.
- Truncate long command outputs; append "…[truncated]" if truncated.
- Do not embed binary or huge logs — only provide report paths to large artifacts.
- For each file moved or important file, include its git relative path.
- If a required field cannot be determined from the session, set it to null.
- At the end of the YAML, include `confidence` (how many fields you could populate; 1.0 = all fields present).

Now, produce the YAML `session_seed:` object filled with everything you can infer from the current session. If you cannot infer fields, set them to null. Ensure all secret values are redacted. Output must be valid YAML only."