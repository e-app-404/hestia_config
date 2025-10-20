#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - DATE

Validates, normalizes, and updates the 'date' field in ADR frontmatter.
Manages the immutable creation/decision date in ISO-8601 format.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def extract_date_from_content(content):
    """Extract date from markdown content as fallback"""
    patterns = [
        r"(?i)date\s*:\s*([0-9-/]+)",  # YAML-style date
        r"(?i)\*\*date\*\*[:\s]*([0-9-/]+)",  # Bold date
        r"(?i)created?\s*:\s*([0-9-/]+)",  # Created date
        r"(?i)decision\s+date\s*:\s*([0-9-/]+)",  # Decision date
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None


def validate_field(field_value, last_updated_date=None):
    """Validate date field according to meta-structure rules"""
    if not field_value:
        return False, "Date field is missing"

    # Handle both string and date object types
    date_str = field_value.isoformat() if hasattr(field_value, "isoformat") else str(field_value)

    # Check ISO date format
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return False, "Date must be in YYYY-MM-DD format"

    # Validate the date is actually valid
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Date contains invalid date"

    # Check chronology - creation date should be <= last_updated
    if last_updated_date:
        try:
            if hasattr(last_updated_date, "isoformat"):
                last_updated_str = last_updated_date.isoformat()
            else:
                last_updated_str = str(last_updated_date)
            last_updated_parsed = datetime.strptime(last_updated_str, "%Y-%m-%d").date()

            if parsed_date > last_updated_parsed:
                return False, "Creation date cannot be after last_updated date"
        except (ValueError, AttributeError):
            pass  # Skip chronology check if last_updated is invalid

    return True, "Valid"


def normalize_field(field_value):
    """Normalize date field value"""
    if hasattr(field_value, "isoformat"):  # datetime.date object
        return field_value.isoformat()

    if isinstance(field_value, str):
        # Try to parse and reformat to ensure consistency
        try:
            parsed_date = datetime.strptime(field_value.strip(), "%Y-%m-%d")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            # Try other common formats
            for fmt in ["%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    parsed_date = datetime.strptime(field_value.strip(), fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue

    return field_value


def generate_field(filename, content):
    """Generate date field from content or file metadata"""
    # Try to extract from content first
    content_date = extract_date_from_content(content)
    if content_date:
        normalized = normalize_field(content_date)
        if re.match(r"^\d{4}-\d{2}-\d{2}$", str(normalized)):
            return normalized

    # Fallback to file creation time
    try:
        file_path = Path(filename)
        if isinstance(filename, str):
            file_path = Path(filename)
        elif hasattr(filename, "stat"):
            file_path = filename

        # Use file modification time as creation proxy
        mtime = file_path.stat().st_mtime
        file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        return file_date
    except (OSError, AttributeError):
        pass

    # Last resort: use today's date
    return datetime.now().strftime("%Y-%m-%d")


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for date field"""
    print(f"Processing DATE field in {file_path.name}")

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

    # Check current date value
    current_date = frontmatter.get("date")
    last_updated_date = frontmatter.get("last_updated")

    # Validate current value
    is_valid, validation_msg = validate_field(current_date, last_updated_date)

    if current_date is not None:
        # Handle both string and date object types for display
        current_date_str = (
            current_date.isoformat() if hasattr(current_date, "isoformat") else str(current_date)
        )
        print(f"  Current DATE: {current_date_str}")

        if is_valid:
            normalized_current = normalize_field(current_date)
            if str(normalized_current) == current_date_str:
                print("  OK: Date is valid and normalized")
                return True
            else:
                print(f"  INFO: Date can be normalized to '{normalized_current}'")
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Date field not found")

    # Generate/fix the date field
    if current_date is not None and is_valid:
        normalized_date = normalize_field(current_date)
    else:
        normalized_date = generate_field(file_path, body_content)

    print(f"  PROPOSED: Set date to '{normalized_date}'")

    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid

    if dry_run:
        print("  DRY-RUN: Would update date field")
        return True

    # Update the frontmatter
    frontmatter["date"] = normalized_date

    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.date")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")

    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Date field updated")
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

    print(f"Processing {len(file_paths)} files for DATE field validation/updates")

    success_count = 0
    error_count = 0

    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1

    print("\nSUMMARY - DATE Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")

    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process DATE field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")

    args = parser.parse_args()

    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())
