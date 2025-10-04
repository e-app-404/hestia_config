id: 20250527_debug01

## 🧠 Prompt Engineering for Validation & Assurance

To get a **line-by-line declared variable analysis**, use this request:

> **Prompt**:
> “Please analyze `mnemosyne.sh` line by line. For each variable declared (`declare`, `readonly`, `export`, etc.), identify:
>
> * Where it is declared
> * Whether it is ever referenced or used
> * Whether it is passed to subprocesses or sourced scripts
> * Whether its value is derived, defaulted, or static
> * If it is safe (fallback exists) or risky (no guard/default)
>   Provide this in a table.”

---

id: 20250527_debug02

### 🧠 Asking What You Don’t Know: Safety and Integration Checks

Here’s a guide to uncover areas you might not realize need attention:

| 🧩 Category                      | 🔍 What to Ask                                                                      | ✅ Why                               |
| -------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------- |
| **Phase Dependency**             | “Which phases depend on others? Does `manifest` rely on `tree` or `snapshot`?”      | Ensure execution order is valid     |
| **Cross-Phase Variable Leakage** | “Do any scripts rely on variables not scoped inside them? Should they be exported?” | Avoid invisible dependency bugs     |
| **Log & Error Safety**           | “Does every phase and utility log errors clearly? Are error codes standardized?”    | Critical for HA and debugging       |
| **Metadata Compliance**          | “Do all phases write `metadata.json` with expected keys?”                           | Required for HA audit trails        |
| **Shell Compatibility**          | “Does `mnemosyne.sh` rely on Bashisms? Is it POSIX compliant?”                      | Avoid breakage on restricted shells |
| **HA Integration**               | “Are all shell commands mapped in `configuration.yaml` used/tested?”                | Prevent dead automations            |
| **Security Check**               | “Do any scripts expose `eval`, `bash -c`, or unsafe user inputs?”                   | Audit attack surface                |
| **Stress Readiness**             | “Can Mnemosyne handle 1000s of files, 50MB+ archives, or network timeouts?”         | Production reliability              |
