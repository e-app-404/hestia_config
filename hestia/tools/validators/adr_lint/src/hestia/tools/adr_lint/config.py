"""Configuration and small dataclasses for the ADR linter."""
from dataclasses import dataclass
from typing import Iterable


@dataclass
class WalkerConfig:
    max_bytes: int = 1048576
    follow_symlinks: bool = False


ALLOWED_VARS = {"HA_MOUNT", "HA_ROOT", "EFFECTIVE", "SRC_MOUNT", "DST_MOUNT", "TEMPLATE_CANONICAL"}

CANONICAL_TEMPLATE = "/config/custom_templates/template.library.jinja"

OPERATOR_PATHS = ("docs/playbooks", "docs/runbooks")
