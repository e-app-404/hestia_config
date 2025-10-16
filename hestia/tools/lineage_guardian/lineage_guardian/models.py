from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class EntityNode:
    entity_id: str
    file_path: str
    unique_id: Optional[str] = None
    domain: Optional[str] = None
    tier: Optional[str] = None
    upstream_refs: List[str] = field(default_factory=list)
    downstream_refs: List[str] = field(default_factory=list)
    macro_imports: List[str] = field(default_factory=list)
    attributes_declared_upstream: List[str] = field(default_factory=list)
    attributes_declared_downstream: List[str] = field(default_factory=list)
    source_count_declared: Optional[int] = None
