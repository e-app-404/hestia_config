#!/usr/bin/env python3
"""
ADR Frontmatter Standardization Tool

Systematically updates all ADR files to include required frontmatter fields:
- id, title, slug, status, related, supersedes, last_updated, date, decision

Usage: python3 adr_frontmatter_update.py [--dry-run] [--backup]
"""

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path

import yaml

ADR_DIR = Path("/config/hestia/library/docs/ADR")
REQUIRED_FIELDS = [
    "id",
    "title",
    "slug",
    "status",
    "related",
    "supersedes",
    "last_updated",
    "date",
    "decision",
]
OPTIONAL_FIELDS = ["related", "supersedes"]  # Can be empty arrays


def generate_slug(title):
    """Generate kebab-case slug from title, removing ADR-XXXX prefix"""
    # Remove ADR-XXXX: prefix
    slug_base = re.sub(r"^ADR-\d+:\s*", "", title, flags=re.IGNORECASE)
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r"[^\w\s-]", "", slug_base.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")


def extract_decision_summary(content):
    """Extract decision summary from document content"""
    # Look for Decision section
    decision_patterns = [
        r"##\s*(?:\d+\.\s*)?Decision\s*\n\n(.*?)(?=\n##|\n```|\Z)",
        r"##\s*(?:\d+\.\s*)?Decision\s*\n(.*?)(?=\n##|\n```|\Z)",
    ]

    for pattern in decision_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            decision_text = match.group(1).strip()
            # Clean up and get first sentence or two
            decision_text = re.sub(r"\n+", " ", decision_text)
            decision_text = re.sub(r"\s+", " ", decision_text)

            # Get first 200 chars or complete sentences
            if len(decision_text) <= 200:
                return decision_text

            # Try to break at sentence boundary
            sentences = re.split(r"(?<=[.!?])\s+", decision_text)
            result = sentences[0]
            for i in range(1, len(sentences)):
                if len(result + " " + sentences[i]) <= 200:
                    result += " " + sentences[i]
                else:
                    break
            return result

    # Fallback: look for bullet points or any content after "Decision"
    decision_match = re.search(r"(?i)decision.*?[-*]\s*(.*?)(?=\n|$)", content)
    if decision_match:
        return decision_match.group(1).strip()[:200]

    # Last resort: extract from first paragraph
    first_para = re.search(
        r"(?:##\s*(?:\d+\.\s*)?(?:Context|Decision|Summary).*?\n\n)(.*?)(?=\n##|\n```|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if first_para:
        para_text = first_para.group(1).strip()
        para_text = re.sub(r"\n+", " ", para_text)
        para_text = re.sub(r"\s+", " ", para_text)
        return para_text[:200] + "..." if len(para_text) > 200 else para_text

    return "Architectural decision documented in this ADR."


def update_adr_frontmatter(file_path, dry_run=False, backup=False):
    """Update a single ADR file's frontmatter"""
    print(f"\nProcessing {file_path.name}...")

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: Could not read file: {e}")
        return False

    if not content.startswith("---"):
        print("  SKIP: No YAML frontmatter found")
        return False

    try:
        # Split content into frontmatter and body
        parts = content.split("---", 2)
        if len(parts) < 3:
            print("  ERROR: Invalid YAML frontmatter structure")
            return False

        yaml_content = parts[1]
        body_content = parts[2]

        # Parse existing frontmatter
        frontmatter = yaml.safe_load(yaml_content) or {}

    except Exception as e:
        print(f"  ERROR: Could not parse YAML frontmatter: {e}")
        return False

    # Check what's missing
    missing_fields = []
    updates_needed = []

    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            missing_fields.append(field)

    if not missing_fields:
        print("  OK: All required fields present")
        return True

    print(f"  MISSING: {', '.join(missing_fields)}")

    # Generate missing fields
    new_frontmatter = frontmatter.copy()

    # Generate ID from filename if missing
    if "id" in missing_fields:
        id_match = re.search(r"ADR-(\d+)", file_path.name)
        if id_match:
            new_frontmatter["id"] = f"ADR-{id_match.group(1)}"
            updates_needed.append(f"id: {new_frontmatter['id']}")

    # Generate slug if missing
    if "slug" in missing_fields and "title" in frontmatter:
        new_frontmatter["slug"] = generate_slug(frontmatter["title"])
        updates_needed.append(f"slug: {new_frontmatter['slug']}")

    # Add empty arrays for related/supersedes if missing
    if "related" in missing_fields:
        new_frontmatter["related"] = []
        updates_needed.append("related: []")

    if "supersedes" in missing_fields:
        new_frontmatter["supersedes"] = []
        updates_needed.append("supersedes: []")

    # Update last_updated to current date
    if "last_updated" in missing_fields or "last_updated" in frontmatter:
        new_frontmatter["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        updates_needed.append(f"last_updated: {new_frontmatter['last_updated']}")

    # Generate decision summary if missing
    if "decision" in missing_fields:
        decision_summary = extract_decision_summary(body_content)
        new_frontmatter["decision"] = decision_summary
        updates_needed.append(f'decision: "{decision_summary[:50]}..."')

    if updates_needed:
        print(f"  UPDATES: {'; '.join(updates_needed)}")

    if dry_run:
        print("  DRY-RUN: Would update file")
        return True

    # Create backup if requested
    if backup:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = file_path.with_suffix(f".md.bak-{timestamp}")
        shutil.copy2(file_path, backup_path)
        print(f"  BACKUP: Created {backup_path.name}")

    # Rebuild frontmatter in correct order
    ordered_frontmatter = {}
    field_order = [
        "id",
        "title",
        "slug",
        "status",
        "related",
        "supersedes",
        "last_updated",
        "date",
        "decision",
    ]

    # Add required fields in order
    for field in field_order:
        if field in new_frontmatter:
            ordered_frontmatter[field] = new_frontmatter[field]

    # Add any remaining fields
    for field, value in new_frontmatter.items():
        if field not in ordered_frontmatter:
            ordered_frontmatter[field] = value

    # Generate new YAML content
    try:
        new_yaml = yaml.dump(
            ordered_frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"

        # Write updated content
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: File updated")
        return True

    except Exception as e:
        print(f"  ERROR: Could not write updated file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Update ADR frontmatter with required fields")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup files before modification"
    )
    parser.add_argument(
        "--update-dates-only", action="store_true", help="Only update last_updated field to today"
    )
    args = parser.parse_args()

    print("ADR Frontmatter Standardization Tool")
    print("=" * 50)

    if args.dry_run:
        print("DRY-RUN MODE: No files will be modified")

    adr_files = sorted(ADR_DIR.glob("ADR-*.md"))
    if not adr_files:
        print("No ADR files found!")
        return 1

    print(f"Found {len(adr_files)} ADR files to process")

    success_count = 0
    error_count = 0

    for adr_file in adr_files:
        if update_adr_frontmatter(adr_file, dry_run=args.dry_run, backup=args.backup):
            success_count += 1
        else:
            error_count += 1

    print("\nSUMMARY:")
    print(f"  Processed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(adr_files)}")

    if not args.dry_run and success_count > 0:
        print("\nRun '/config/bin/adr-index' to regenerate the governance index")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    exit(main())
