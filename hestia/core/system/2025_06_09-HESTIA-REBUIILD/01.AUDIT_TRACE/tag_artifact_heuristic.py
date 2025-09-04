"""
tag_artifact_heuristic.py

Expanded tagging rules for meta-layer parsing and schema assimilation.
Each rule includes file extension targeting, keyword matching, and tagging rationale.
"""

tagging_rules = {
    "archivable": {
        "extensions": [".md", ".txt", ".log"],
        "keywords": ["legacy", "archive", "decommissioned"],
        "rationale": "Legacy or deprecated artifacts to be moved to cold storage."
    },
    "doctrine": {
        "extensions": [".md"],
        "keywords": ["doctrine", "philosophy", "tier", "governance"],
        "rationale": "Doctrinal, philosophical, or rule-defining texts used in system interpretation."
    },
    "schema_fragment": {
        "extensions": [".yaml"],
        "keywords": ["schema", "template", "structure"],
        "rationale": "YAML-based definitions used in validation, template generation, or schema enforcement."
    },
    "regulatory": {
        "extensions": [".md", ".yaml"],
        "keywords": ["error", "validation", "fix_chain", "remediation"],
        "rationale": "Content regulating system behavior or linking to validation chains and error patterns."
    },
    "orphaned": {
        "extensions": [".md", ".txt"],
        "keywords": ["readme", "todo", "notes"],
        "rationale": "Contextual or disconnected notes with no binding to active config or schema."
    },
    "scaffold": {
        "extensions": [".jinja", ".py", ".yaml"],
        "keywords": ["template", "macro", "hook"],
        "rationale": "Scaffolding files used for macro generation, input templating, or signal-to-logic paths."
    }
}
