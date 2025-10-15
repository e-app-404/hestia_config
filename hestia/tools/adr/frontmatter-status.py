#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - STATUS

Validates, normalizes, and updates the 'status' field in ADR frontmatter.
Ensures proper lifecycle status values according to ADR-0009.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")

# Canonical status values from meta-structure
ALLOWED_STATUS_VALUES = [
    "Draft",
    "Proposed", 
    "Accepted",
    "Implemented",
    "Amended",
    "Deprecated",
    "Superseded",
    "Rejected",
    "Withdrawn"
]

# Status aliases for normalization
STATUS_ALIASES = {
    "Approved": "Accepted",
    "Executed": "Accepted",
    "Proposed (Ready to adopt)": "Proposed",
    "Pending Validation": "Pending",
}


def extract_status_from_content(content):
    """Extract status from markdown content as fallback"""
    patterns = [
        r"^\s*status\s*:\s*([^\n]+)",  # YAML-style status
        r"(?i)\*\*status\*\*[:\s]*([^\n]+)",  # Bold status
        r"(?i)status:\s*([^\n]+)",  # Simple status line
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.group(1).strip().strip("\"'")
    return None


def validate_field(field_value):
    """Validate status field according to meta-structure rules"""
    if not field_value:
        return False, "Status field is missing"
    
    if not isinstance(field_value, str):
        return False, "Status must be a string"
    
    # Check if it's a valid status value (including aliases)
    normalized_status = normalize_field(field_value)
    if normalized_status not in ALLOWED_STATUS_VALUES:
        return False, f"Status must be one of: {', '.join(ALLOWED_STATUS_VALUES)}"
    
    return True, "Valid"


def normalize_field(field_value):
    """Normalize status field value"""
    if not isinstance(field_value, str):
        return field_value
    
    # Trim and title case
    normalized = field_value.strip().title()
    
    # Apply aliases
    return STATUS_ALIASES.get(normalized, normalized)


def generate_field(filename, content):
    """Generate status field from content or filename analysis"""
    # Try to extract from content first
    content_status = extract_status_from_content(content)
    if content_status:
        return normalize_field(content_status)
    
    # Analyze file location for default status
    if "/deprecated/" in str(filename):
        return "Superseded"
    
    # Check content for decision indicators
    if re.search(r"(?i)we\s+(will|shall|decide|adopt)", content):
        return "Accepted"
    elif re.search(r"(?i)(proposed|proposal|should|consider)", content):
        return "Proposed"
    
    # Default to Draft
    return "Draft"


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for status field"""
    print(f"Processing STATUS field in {file_path.name}")
    
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
    
    # Check current status value
    current_status = frontmatter.get("status")
    
    # Validate current value
    is_valid, validation_msg = validate_field(current_status)
    
    if current_status:
        print(f"  Current STATUS: {current_status}")
        if is_valid:
            normalized_current = normalize_field(current_status)
            if normalized_current == current_status:
                print("  OK: Status is valid and normalized")
                return True
            else:
                print(f"  INFO: Status can be normalized to '{normalized_current}'")
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Status field not found")
    
    # Generate/fix the status
    if current_status and is_valid:
        normalized_status = normalize_field(current_status)
    else:
        normalized_status = generate_field(file_path, body_content)
    
    print(f"  PROPOSED: Set status to '{normalized_status}'")
    
    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid
    
    if dry_run:
        print("  DRY-RUN: Would update status field")
        return True
    
    # Update the frontmatter
    frontmatter["status"] = normalized_status
    
    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.status")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")
    
    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Status field updated")
        return True
    except Exception as e:
        print(f"  ERROR: Could not write updated file: {e}")
        return False


def process_files(file_paths, dry_run, backup, validate_only):
    """Process multiple ADR files"""
    if not file_paths:
        file_paths = sorted(ADR_DIR.glob("ADR-*.md"))
    else:
        file_paths = [Path(p) for p in file_paths]
    
    if not file_paths:
        print("No ADR files found to process")
        return 0
    
    print(f"Processing {len(file_paths)} files for STATUS field validation/updates")
    
    success_count = 0
    error_count = 0
    
    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1
    
    print("\nSUMMARY - STATUS Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")
    
    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process STATUS field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")
    
    args = parser.parse_args()
    
    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())