#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - TITLE

Validates, normalizes, and updates the 'title' field in ADR frontmatter.
Ensures proper ADR-XXXX prefix format and length constraints.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def extract_id_from_filename(filename):
    """Extract ADR ID from filename"""
    match = re.search(r"ADR-(\d+)", filename)
    if match:
        return f"ADR-{match.group(1).zfill(4)}"
    return None


def extract_title_from_content(content):
    """Extract title from markdown content as fallback"""
    patterns = [
        r"^\s*#\s+(ADR-\d{3,4}[:\-]\s*[^#]+)",  # ADR-prefixed headers
        r"^\s*#\s+([^#\n]+)",  # Any top-level header
        r"^##\s*([^#\n]+)",  # Second-level header as fallback
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            if not title.startswith(("1.", "2.", "on NAS host")):
                return title
    return None


def validate_field(field_value, expected_id=None):
    """Validate title field according to meta-structure rules"""
    if not field_value:
        return False, "Title field is missing"
    
    if not isinstance(field_value, str):
        return False, "Title must be a string"
    
    # Check length constraints
    if len(field_value) < 15:
        return False, "Title must be at least 15 characters long"
    
    if len(field_value) > 200:
        return False, "Title must not exceed 200 characters"
    
    # Check ADR-XXXX prefix if expected_id provided
    if expected_id and not field_value.startswith(f"{expected_id}:"):
        return False, f"Title should start with '{expected_id}:' prefix"
    
    return True, "Valid"


def normalize_field(field_value):
    """Normalize title field value"""
    if not isinstance(field_value, str):
        return field_value
    
    # Trim whitespace and normalize spacing
    normalized = re.sub(r'\s+', ' ', field_value.strip())
    return normalized


def generate_field(filename, content):
    """Generate title field from filename and content"""
    adr_id = extract_id_from_filename(filename)
    if not adr_id:
        return None
    
    # Try to extract from content first
    content_title = extract_title_from_content(content)
    if content_title:
        # If content title doesn't have ADR prefix, add it
        if not content_title.startswith(adr_id):
            return f"{adr_id}: {content_title}"
        return content_title
    
    # Fallback: generate from filename
    stem = Path(filename).stem
    if stem.startswith("ADR-"):
        title_part = (
            stem.replace(adr_id.replace(":", ""), "")
            .strip("-")
            .replace("-", " ")
            .replace("_", " ")
        )
        return f"{adr_id}: {title_part.title()}"
    
    return f"{adr_id}: Untitled ADR"


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for title field"""
    print(f"Processing TITLE field in {file_path.name}")
    
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
    
    # Check current title value
    current_title = frontmatter.get("title")
    expected_id = extract_id_from_filename(file_path.name)
    
    # Validate current value
    is_valid, validation_msg = validate_field(current_title, expected_id)
    
    if current_title:
        print(f"  Current TITLE: {current_title}")
        if is_valid:
            print("  OK: Title is valid")
            return True
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Title field not found")
    
    # Generate/fix the title
    generated_title = generate_field(file_path.name, body_content)
    if not generated_title:
        print("  ERROR: Could not generate title")
        return False
    
    normalized_title = normalize_field(generated_title)
    print(f"  PROPOSED: Set title to '{normalized_title}'")
    
    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid
    
    if dry_run:
        print("  DRY-RUN: Would update title field")
        return True
    
    # Update the frontmatter
    frontmatter["title"] = normalized_title
    
    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.title")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")
    
    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Title field updated")
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
    
    print(f"Processing {len(file_paths)} files for TITLE field validation/updates")
    
    success_count = 0
    error_count = 0
    
    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1
    
    print("\nSUMMARY - TITLE Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")
    
    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process TITLE field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")
    
    args = parser.parse_args()
    
    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())