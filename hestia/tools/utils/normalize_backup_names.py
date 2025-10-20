#!/usr/bin/env python3
"""
Normalize backup file names to ADR-0018 standard pattern: <name>.<UTC>.bk
Handles various legacy patterns and converts them to canonical format.
"""
import argparse
import re
from pathlib import Path


def normalize_backup_name(filename):
    """Convert various backup naming patterns to canonical <name>.<UTC>.bk format"""
    
    # Pattern 1: Already correct format: name.YYYYMMDDTHHMMSSZ.bk
    if re.match(r'^.+\.\d{8}T\d{6}Z\.bk$', filename):
        return filename  # Already correct
    
    # Pattern 2: name.bk.YYYYMMDDTHHMMSSZ -> name.YYYYMMDDTHHMMSSZ.bk
    match = re.match(r'^(.+)\.bk\.(\d{8}T\d{6}Z)$', filename)
    if match:
        name, timestamp = match.groups()
        return f"{name}.{timestamp}.bk"
    
    # Pattern 3: name.YYYYMMDDTHHMMSSZ.bk (already correct but double-check)
    match = re.match(r'^(.+)\.(\d{8}T\d{6}Z)\.bk$', filename)
    if match:
        return filename  # Already correct
    
    # Pattern 4: name.YYYY-MM-DD_HHMMSS.bk.YYYYMMDDTHHMMSSZ -> name_YYYY-MM-DD_HHMMSS.YYYYMMDDTHHMMSSZ.bk
    match = re.match(r'^(.+)\.(\d{4}-\d{2}-\d{2}_\d{6})\.bk\.(\d{8}T\d{6}Z)$', filename)
    if match:
        base_name, old_timestamp, new_timestamp = match.groups()
        return f"{base_name}_{old_timestamp}.{new_timestamp}.bk"
    
    # Pattern 5: name.YYYYMMDD -> name.YYYYMMDD000000Z.bk (assume midnight UTC)
    match = re.match(r'^(.+)\.bk\.(\d{8})$', filename)
    if match:
        name, date = match.groups()
        return f"{name}.{date}T000000Z.bk"
    
    # Pattern 6: name.extension.YYYYMMDDTHHMMSSZ.bk -> name_extension.YYYYMMDDTHHMMSSZ.bk
    match = re.match(r'^(.+)\.([^.]+)\.(\d{8}T\d{6}Z)\.bk$', filename)
    if match:
        name, ext, timestamp = match.groups()
        return f"{name}_{ext}.{timestamp}.bk"
    
    # Pattern 7: name.bk.qualifier.YYYYMMDDTHHMMSSZ -> name_qualifier.YYYYMMDDTHHMMSSZ.bk
    match = re.match(r'^(.+)\.bk\.([^.]+)\.(\d{8}T\d{6}Z)$', filename)
    if match:
        name, qualifier, timestamp = match.groups()
        return f"{name}_{qualifier}.{timestamp}.bk"
    
    # Pattern 8: Files without .bk extension but with timestamps -> add .bk
    match = re.match(r'^(.+)\.(\d{8}T\d{6}Z)$', filename)
    if match:
        name, timestamp = match.groups()
        return f"{name}.{timestamp}.bk"
    
    # Pattern 9: Files ending with just date (YYYYMMDD) -> add time and .bk
    match = re.match(r'^(.+)\.bk\.(\d{8})$', filename)
    if match:
        name, date = match.groups()
        return f"{name}.{date}T000000Z.bk"
    
    # Pattern 10: Special case for .md files - keep extension in name
    match = re.match(r'^(.+)\.(\d{8}T\d{6}Z)\.md$', filename)
    if match:
        name, timestamp = match.groups()
        return f"{name}_md.{timestamp}.bk"
    
    # If no pattern matches, return original filename (manual review needed)
    return filename


def main():
    parser = argparse.ArgumentParser(description='Normalize backup file names to ADR-0018 standard')
    parser.add_argument('--backup-dir', default='/config/hestia/workspace/archive/vault/backups',
                       help='Directory containing backup files')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be renamed without making changes')
    parser.add_argument('--apply', action='store_true',
                       help='Actually perform the renames')
    
    args = parser.parse_args()
    
    if not args.apply and not args.dry_run:
        args.dry_run = True  # Default to dry-run
    
    backup_dir = Path(args.backup_dir)
    if not backup_dir.exists():
        print(f"❌ Backup directory does not exist: {backup_dir}")
        return 1
    
    # Get all files (not directories)
    files = [f for f in backup_dir.iterdir() if f.is_file()]
    
    changes = []
    for file_path in files:
        old_name = file_path.name
        new_name = normalize_backup_name(old_name)
        
        if old_name != new_name:
            changes.append((file_path, new_name))
    
    if not changes:
        print("✅ All backup files already follow ADR-0018 naming pattern")
        return 0
    
    print(f"📊 Found {len(changes)} files to normalize:")
    print()
    
    for file_path, new_name in changes:
        old_name = file_path.name
        print(f"  {old_name}")
        print(f"  → {new_name}")
        print()
    
    if args.dry_run:
        print("🔍 DRY RUN: No changes made. Use --apply to perform renames.")
        return 0
    
    if args.apply:
        print("🔄 Applying renames...")
        success_count = 0
        
        for file_path, new_name in changes:
            new_path = file_path.parent / new_name
            
            if new_path.exists():
                print(f"⚠️  Skipping {file_path.name} -> {new_name} (target exists)")
                continue
            
            try:
                file_path.rename(new_path)
                print(f"✅ Renamed: {file_path.name} -> {new_name}")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to rename {file_path.name}: {e}")
        
        print(f"\n📊 Successfully normalized {success_count}/{len(changes)} backup files")
        
        if success_count > 0:
            print("✅ Backup file names now follow ADR-0018 standard pattern")
    
    return 0


if __name__ == '__main__':
    exit(main())