#!/usr/bin/env python3
"""
Place normalized prompts in catalog structure with hard copies
"""

import shutil
import sys
from pathlib import Path
import yaml

def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from markdown file"""
    content = filepath.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    return {}

def place_prompt(prompt_file: Path, catalog_root: Path, generate_copies: bool = True):
    """Place prompt in catalog with optional hard copies"""
    metadata = extract_frontmatter(prompt_file)
    
    # Validate required metadata
    required_fields = ['domain', 'tier', 'persona']
    missing = [f for f in required_fields if f not in metadata]
    if missing:
        print(f"⚠️  Skipping {prompt_file.name}: missing metadata fields: {missing}")
        return False
    
    # Primary canonical location
    domain = metadata['domain']
    domain_dir = catalog_root / 'by_domain' / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    primary_path = domain_dir / prompt_file.name
    
    # Copy to primary location
    shutil.copy2(prompt_file, primary_path)
    print(f"✅ Placed {prompt_file.name} in by_domain/{domain}/")
    
    if generate_copies:
        # Generate hard copy for tier navigation
        tier = metadata['tier']
        tier_dir = catalog_root / 'by_tier' / tier
        tier_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(primary_path, tier_dir / prompt_file.name)
        print(f"   📋 Created tier copy in by_tier/{tier}/")
        
        # Generate hard copy for persona navigation
        persona = metadata['persona']
        persona_dir = catalog_root / 'by_persona' / persona
        persona_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(primary_path, persona_dir / prompt_file.name)
        print(f"   📋 Created persona copy in by_persona/{persona}/")
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Place normalized prompts in catalog')
    parser.add_argument('--processed-dir', required=True, help='Directory with processed prompts')
    parser.add_argument('--catalog-root', required=True, help='Root of catalog structure')
    parser.add_argument('--generate-copies', action='store_true', help='Generate tier/persona copies')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    processed_dir = Path(args.processed_dir)
    catalog_root = Path(args.catalog_root)
    
    if not processed_dir.exists():
        print(f"❌ Processed directory does not exist: {processed_dir}")
        sys.exit(1)
    
    stats = {'placed': 0, 'skipped': 0, 'errors': 0}
    
    for prompt_file in processed_dir.glob("*.md"):
        try:
            if args.dry_run:
                print(f"[DRY RUN] Would place: {prompt_file.name}")
                stats['placed'] += 1
            else:
                if place_prompt(prompt_file, catalog_root, args.generate_copies):
                    stats['placed'] += 1
                else:
                    stats['skipped'] += 1
        except Exception as e:
            print(f"❌ Error placing {prompt_file.name}: {e}")
            stats['errors'] += 1
    
    print(f"\n📊 Summary: {stats['placed']} placed, {stats['skipped']} skipped, {stats['errors']} errors")
    sys.exit(0 if stats['errors'] == 0 else 1)

if __name__ == "__main__":
    main()
