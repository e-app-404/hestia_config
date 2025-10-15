#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - LAST_UPDATED

Validates, normalizes, and updates the 'last_updated' field in ADR frontmatter.
Manages the auto-updating modification timestamp in ISO-8601 format.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def validate_field(field_value, creation_date=None):
    """Validate last_updated field according to meta-structure rules"""
    if not field_value:
        return False, "Last_updated field is missing"
    
    # Handle both string and date object types
    if hasattr(field_value, 'isoformat'):  # datetime.date object
        date_str = field_value.isoformat()
    else:
        date_str = str(field_value)
    
    # Check ISO date format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, "Last_updated must be in YYYY-MM-DD format"
    
    # Validate the date is actually valid
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return False, "Last_updated contains invalid date"
    
    # Check chronology - last_updated should be >= creation date
    if creation_date:
        try:
            if hasattr(creation_date, 'isoformat'):
                creation_date_str = creation_date.isoformat()
            else:
                creation_date_str = str(creation_date)
            creation_parsed = datetime.strptime(creation_date_str, '%Y-%m-%d').date()
            
            if parsed_date < creation_parsed:
                return False, "Last_updated cannot be before creation date"
        except (ValueError, AttributeError):
            pass  # Skip chronology check if creation date is invalid
    
    return True, "Valid"


def normalize_field(field_value):
    """Normalize last_updated field value"""
    if hasattr(field_value, 'isoformat'):  # datetime.date object
        return field_value.isoformat()
    
    if isinstance(field_value, str):
        # Try to parse and reformat to ensure consistency
        try:
            parsed_date = datetime.strptime(field_value.strip(), '%Y-%m-%d')
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            # Try other common formats
            for fmt in ['%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    parsed_date = datetime.strptime(field_value.strip(), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
    
    return field_value


def generate_field():
    """Generate current date for last_updated field"""
    return datetime.now().strftime('%Y-%m-%d')


def process_adr_file(
    file_path, dry_run=False, backup=False, validate_only=False, force_update=False
):
    """Process single ADR file for last_updated field"""
    print(f"Processing LAST_UPDATED field in {file_path.name}")
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: Could not read file: {e}")
        return False
    
    if not content.startswith("---"):
        print("  SKIP: No YAML frontmatter found")
        return True
    
    try:
        # Split content into frontmatter and body
        parts = content.split("---", 2)
        if len(parts) < 3:
            print("  ERROR: Invalid YAML frontmatter structure")
            return False
        
        yaml_content = parts[1]
        body_content = parts[2]
        frontmatter = yaml.safe_load(yaml_content) or {}
        
    except Exception as e:
        print(f"  ERROR: Could not parse YAML frontmatter: {e}")
        return False
    
    # Check current last_updated value
    current_last_updated = frontmatter.get("last_updated")
    creation_date = frontmatter.get("date")
    today = generate_field()
    
    # Validate current value
    is_valid, validation_msg = validate_field(current_last_updated, creation_date)
    
    if current_last_updated is not None:
        # Handle both string and date object types for comparison
        if hasattr(current_last_updated, 'isoformat'):
            current_date_str = current_last_updated.isoformat()
        else:
            current_date_str = str(current_last_updated)
        
        print(f"  Current LAST_UPDATED: {current_date_str}")
        
        if is_valid:
            if current_date_str == today and not force_update:
                print("  OK: Last_updated is current and valid")
                return True
            elif not force_update:
                print(f"  INFO: Last_updated is valid but not current (today: {today})")
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Last_updated field not found")
    
    # Update to current date
    normalized_last_updated = today
    print(f"  PROPOSED: Set last_updated to '{normalized_last_updated}'")
    
    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid
    
    if dry_run:
        print("  DRY-RUN: Would update last_updated field")
        return True
    
    # Update the frontmatter
    frontmatter["last_updated"] = normalized_last_updated
    
    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.last_updated")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")
    
    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Last_updated field updated")
        return True
    except Exception as e:
        print(f"  ERROR: Could not write updated file: {e}")
        return False


def process_files(file_paths, dry_run, backup, validate_only, force_update=False):
    """Process multiple ADR files"""
    if not file_paths:
        file_paths = sorted(ADR_DIR.glob("ADR-*.md"))
    else:
        file_paths = [Path(p) for p in file_paths]
    
    if not file_paths:
        print("No ADR files found to process")
        return 0
    
    action = "force updating" if force_update else "validation/updates"
    print(f"Processing {len(file_paths)} files for LAST_UPDATED field {action}")
    
    success_count = 0
    error_count = 0
    
    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only, force_update):
            success_count += 1
        else:
            error_count += 1
    
    print("\nSUMMARY - LAST_UPDATED Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")
    
    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process LAST_UPDATED field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="Force update to current date even if already current",
    )
    
    args = parser.parse_args()
    
    return process_files(
        args.files, args.dry_run, args.backup, args.validate_only, args.force_update
    )


if __name__ == "__main__":
    sys.exit(main())