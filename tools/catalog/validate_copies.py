#!/usr/bin/env python3
"""Validate that tier/persona copies match primary domain files"""

import hashlib
import sys
from pathlib import Path

import yaml

CATALOG_ROOT = Path("/config/hestia/library/prompts/catalog")

def file_hash(path: Path) -> str:
    """Calculate SHA-256 hash of file"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from markdown file"""
    content = filepath.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    return {}

def main():
    errors = []
    
    for primary in (CATALOG_ROOT / "by_domain").rglob("*.md"):
        try:
            # Extract metadata to find tier and persona
            metadata = extract_frontmatter(primary)
            tier = metadata.get('tier')
            persona = metadata.get('persona')
            
            # Validate tier copy
            if tier:
                tier_copy = CATALOG_ROOT / "by_tier" / tier / primary.name
                if tier_copy.exists():
                    if file_hash(primary) != file_hash(tier_copy):
                        errors.append(f"Hash mismatch: {primary.name} (tier)")
                else:
                    errors.append(f"Missing tier copy: {tier_copy}")
            
            # Validate persona copy
            if persona:
                persona_copy = CATALOG_ROOT / "by_persona" / persona / primary.name
                if persona_copy.exists():
                    if file_hash(primary) != file_hash(persona_copy):
                        errors.append(f"Hash mismatch: {primary.name} (persona)")
                else:
                    errors.append(f"Missing persona copy: {persona_copy}")
                    
        except Exception as e:
            errors.append(f"Error processing {primary.name}: {e}")
    
    if errors:
        print("❌ Copy validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ All copies validated successfully")

if __name__ == "__main__":
    main()
