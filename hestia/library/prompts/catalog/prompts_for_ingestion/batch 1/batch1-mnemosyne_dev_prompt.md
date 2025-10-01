
design_context: |  # 🧭 Snapshot Engine (Codename: `mnemosyne`)

  ## Why "Snapshot Engine"?

  Mnemosyne is not merely a template or validation processor:

  - It **aggregates and compresses** runtime configuration state
  - It **enforces archival fidelity**
  - It logs **file-level lineage and metadata**
  - It reconciles **tree manifests with tar contents**
  - It anchors to **git commits**, symlink states, and toolchain runtime topology

  Named after the Titaness of memory in Greek mythology, `mnemosyne` embodies the principle of **mnemonic integrity**—preserving the memory of runtime state with structured fidelity.

  ## 🔧 Functional Scope

  | Function              | Description                                                                          |
  |-----------------------|--------------------------------------------------------------------------------------|
  | Phase execution       | Orchestrates Git pull, symlink merge, tar creation, and manifest stamping           |
  | Log fidelity          | Segmented, ANSI-free logs with error rollup                                         |
  | Metadata enrichment   | SHA, volume source, template IDs, version                                            |
  | Delta awareness       | Diffs archive against filesystem tree; flags missing or skipped entries              |
  | Archive integrity     | Reports compression ratios, retention, and file path correctness                    |

  ## 🔄 Relationship to Other Engines

  | Engine Type              | Purpose                                                             |
  |--------------------------|---------------------------------------------------------------------|
  | `template_engine`        | Renders YAMLs from structured Jinja sources                         |
  | `validation_engine`      | Validates compliance, outputs, and tier rules (Olympus)             |
  | `snapshot_engine`        | Preserves state and provenance at runtime (`mnemosyne`)             |

  ## ✅ Why Modularization?

  1. **Precedent**  
     Olympus and Template Engine isolate logic in pluggable modules (`validate_yaml`, `compose_template`).  
     They are **traceable**, **testable**, and **extendable**.

  2. **Themis Snapshot Monolithism**  
     `themis_snapshot.command` implements all logic inline: mount, analyze, archive, validate, report.  
     Failure in one phase (e.g., `find`) compromises all downstream outputs.

  3. **Reference Scripts (Modular Candidates)**  
     - `git-cat.sh`: Git content retriever with log-awareness  
     - `update-hass-repos.sh`: Git repo synchronizer  
     - `refresh_symlinks.sh`: Includes log rotation, retries, and canonical symlink logic

     These exhibit the structure and clarity required for the new snapshot engine.

  ## 🔧 Proposed Modular Structure

  | Component                   | Role                                            | Source                                  |
  |----------------------------|-------------------------------------------------|-----------------------------------------|
  | `phase_git_refresh.sh`     | Sync & validate Git mirror                      | `update-hass-repos.sh`                  |
  | `phase_symlink_merge.sh`   | Canonicalize symlinks, handle retry layers      | `refresh_symlinks.sh`                   |
  | `phase_tar_pack.sh`        | Create volume archives                          | Refactored from `themis_snapshot.command` |
  | `phase_tree_generate.sh`   | Create file tree manifests (`tree -J`)          | New                                     |
  | `phase_manifest_compile.sh`| Generate SHA manifest, include file metadata    | New                                     |
  | `themis_pipeline.sh`       | Orchestrate the above phases                    | NEW                                     |

  ## 📦 Engine Directory Layout

```plaintext
/config/hestia/tools/themis/
├── themis\_pipeline.sh
├── lib/
│   ├── phase\_git\_refresh.sh
│   ├── phase\_symlink\_merge.sh
│   ├── phase\_tar\_pack.sh
│   ├── phase\_tree\_generate.sh
│   └── phase\_manifest\_compile.sh
└── logs/
```

Each module must:

- Accept environment variables or config inputs
- Output logs to `/logs/themis/`
- Return success/failure codes
- Be unit-testable in isolation

## 🧱 Prototype Scaffold

```plaintext
themis\_modular\_engine/
├── themis\_pipeline.sh
├── lib/
│   └── phase\_git\_refresh.sh
└── logs/
```

- `themis_pipeline.sh`: Main entrypoint
- `phase_git_refresh.sh`: First working module (already implemented)