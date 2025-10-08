#!/usr/bin/env python3
"""Maintain by_tier and by_persona as hard copies of by_domain"""

import shutil
from pathlib import Path

import yaml

CATALOG_ROOT = Path("/config/hestia/library/prompts/catalog")

def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from markdown file"""
    content = filepath.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    return {}

def copy_if_different(src: Path, dest: Path) -> bool:
    """Copy file only if different or missing"""
    if not dest.exists() or src.read_bytes() != dest.read_bytes():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return True
    return False

def sync_catalog_copies():
    """Synchronize tier and persona copies from primary domain files"""
    by_domain = CATALOG_ROOT / "by_domain"
    by_tier = CATALOG_ROOT / "by_tier"
    by_persona = CATALOG_ROOT / "by_persona"
    
    stats = {"updated": 0, "created": 0, "errors": 0}
    
    for primary in by_domain.rglob("*.md"):
        try:
            metadata = extract_frontmatter(primary)
            
            # Generate tier copy
            tier = metadata.get('tier')
            if tier:
                tier_path = by_tier / tier / primary.name
                if copy_if_different(primary, tier_path):
                    stats["updated" if tier_path.exists() else "created"] += 1
            
            # Generate persona copy
            persona = metadata.get('persona')
            if persona:
                persona_path = by_persona / persona / primary.name
                if copy_if_different(primary, persona_path):
                    stats["updated" if persona_path.exists() else "created"] += 1
                    
        except Exception as e:
            print(f"Error processing {primary}: {e}")
            stats["errors"] += 1
    
    print(f"Sync complete: {stats['created']} created, {stats['updated']} updated, {stats['errors']} errors")
    return stats["errors"] == 0

if __name__ == "__main__":
    import sys
    sys.exit(0 if sync_catalog_copies() else 1)
