#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - SLUG

Validates, normalizes, and updates the 'slug' field in ADR frontmatter.
Generates kebab-case slugs from titles and ensures uniqueness.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def generate_slug_from_title(title):
    """Generate kebab-case slug from ADR title"""
    if not title:
        return None

    # Remove ADR-XXXX: prefix
    slug_base = re.sub(r"^ADR-\d+:\s*", "", title, flags=re.IGNORECASE)

    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r"[^\w\s-]", "", slug_base.lower())
    slug = re.sub(r"[-\s]+", "-", slug)

    return slug.strip("-")


def validate_field(field_value, existing_slugs=None):
    """Validate slug field according to meta-structure rules"""
    if not field_value:
        return False, "Slug field is missing"

    if not isinstance(field_value, str):
        return False, "Slug must be a string"

    # Check kebab-case pattern
    if not re.match(r"^[a-z0-9-]+$", field_value):
        return False, "Slug must be kebab-case (lowercase letters, numbers, hyphens only)"

    # Check length constraints
    if len(field_value) < 5:
        return False, "Slug must be at least 5 characters long"

    if len(field_value) > 100:
        return False, "Slug must not exceed 100 characters"

    # Check uniqueness if provided
    if existing_slugs and field_value in existing_slugs:
        return False, f"Slug '{field_value}' is not unique"

    return True, "Valid"


def normalize_field(field_value):
    """Normalize slug field value"""
    if not isinstance(field_value, str):
        return field_value

    # Ensure proper kebab-case normalization
    normalized = re.sub(r"[^\w\s-]", "", field_value.lower())
    normalized = re.sub(r"[-\s]+", "-", normalized)
    return normalized.strip("-")


def collect_existing_slugs(exclude_file=None):
    """Collect all existing slugs for uniqueness checking"""
    existing_slugs = set()

    for adr_file in ADR_DIR.glob("ADR-*.md"):
        if exclude_file and adr_file.samefile(exclude_file):
            continue

        try:
            content = adr_file.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    slug = frontmatter.get("slug")
                    if slug:
                        existing_slugs.add(slug)
        except Exception:
            continue  # Skip files that can't be parsed

    return existing_slugs


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for slug field"""
    print(f"Processing SLUG field in {file_path.name}")

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

    # Get existing slugs for uniqueness check
    existing_slugs = collect_existing_slugs(exclude_file=file_path)

    # Check current slug value
    current_slug = frontmatter.get("slug")
    title = frontmatter.get("title", "")

    # Generate expected slug from title
    expected_slug = generate_slug_from_title(title) if title else None

    if not expected_slug:
        print("  ERROR: Cannot generate slug - title field missing or invalid")
        return False

    # Validate current value
    is_valid, validation_msg = validate_field(current_slug, existing_slugs)

    if current_slug:
        print(f"  Current SLUG: {current_slug}")
        if is_valid and current_slug == expected_slug:
            print("  OK: Slug is valid and matches title")
            return True
        elif current_slug != expected_slug:
            print("  INFO: Slug differs from title-generated slug")
            print(f"        Expected: {expected_slug}")
            if is_valid:
                print("  OK: Current slug is valid, keeping as-is")
                return True
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Slug field not found")

    # Generate/fix the slug
    normalized_slug = normalize_field(expected_slug)

    # Check if normalized slug is unique
    if normalized_slug in existing_slugs:
        # Try to make it unique by appending a number
        counter = 1
        while f"{normalized_slug}-{counter}" in existing_slugs:
            counter += 1
        normalized_slug = f"{normalized_slug}-{counter}"
        print(f"  INFO: Made slug unique: {normalized_slug}")

    print(f"  PROPOSED: Set slug to '{normalized_slug}'")

    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid

    if dry_run:
        print("  DRY-RUN: Would update slug field")
        return True

    # Update the frontmatter
    frontmatter["slug"] = normalized_slug

    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.slug")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")

    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Slug field updated")
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

    print(f"Processing {len(file_paths)} files for SLUG field validation/updates")

    success_count = 0
    error_count = 0

    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1

    print("\nSUMMARY - SLUG Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")

    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process SLUG field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")

    args = parser.parse_args()

    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())
