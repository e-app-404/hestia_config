#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - DECISION

Validates, normalizes, and updates the 'decision' field in ADR frontmatter.
Extracts concise decision summaries from document content.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def extract_decision_from_content(content):
    """Extract decision summary from document content"""
    # Primary patterns for decision sections
    decision_patterns = [
        r"##\s*(?:\d+\.\s*)?Decision\s*\n\n(.*?)(?=\n##|\n```|\Z)",
        r"##\s*(?:\d+\.\s*)?Decision\s*\n(.*?)(?=\n##|\n```|\Z)",
        r"\*\*Decision\*\*[:\s]*(.*?)(?=\n\n|\n##|\Z)",
    ]
    
    for pattern in decision_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            decision_text = match.group(1).strip()
            if decision_text and not decision_text.startswith("(see file)"):
                # Clean up and truncate decision text
                decision_text = " ".join(decision_text.split())  # Normalize whitespace
                if len(decision_text) > 300:
                    # Try to break at sentence boundaries
                    sentences = re.split(r'(?<=[.!?])\s+', decision_text)
                    result = sentences[0]
                    for i in range(1, len(sentences)):
                        if len(result + " " + sentences[i]) <= 300:
                            result += " " + sentences[i]
                        else:
                            break
                    return result
                return decision_text
    
    # Fallback patterns
    fallback_patterns = [
        r"(?i)decision.*?[-*]\s*(.*?)(?=\n|$)",
        r"(?:##\s*(?:\d+\.\s*)?(?:Context|Decision|Summary).*?\n\n)(.*?)(?=\n##|\n```|\Z)",
    ]
    
    for pattern in fallback_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            decision_text = match.group(1).strip()
            decision_text = " ".join(decision_text.split())
            if len(decision_text) > 20:  # Ensure meaningful content
                return decision_text[:300] + ("..." if len(decision_text) > 300 else "")
    
    return None


def validate_field(field_value):
    """Validate decision field according to meta-structure rules"""
    if not field_value:
        return False, "Decision field is missing"
    
    if not isinstance(field_value, str):
        return False, "Decision must be a string"
    
    # Check length constraints
    if len(field_value) < 20:
        return False, "Decision summary must be at least 20 characters long"
    
    if len(field_value) > 300:
        return False, "Decision summary must not exceed 300 characters"
    
    # Check for placeholder content
    if field_value.strip().lower() in ["(see file)", "see file", "tbd", "todo", "placeholder"]:
        return False, "Decision contains placeholder content"
    
    return True, "Valid"


def normalize_field(field_value):
    """Normalize decision field value"""
    if not isinstance(field_value, str):
        return field_value
    
    # Trim whitespace and normalize spacing
    normalized = " ".join(field_value.strip().split())
    
    # Ensure sentence case (capitalize first letter)
    if normalized and not normalized[0].isupper():
        normalized = normalized[0].upper() + normalized[1:]
    
    # Ensure proper ending punctuation
    if normalized and not normalized.endswith(('.', '!', '?', ':')):
        normalized += '.'
    
    return normalized


def generate_field(content):
    """Generate decision field from content"""
    extracted = extract_decision_from_content(content)
    if extracted:
        return normalize_field(extracted)
    
    # Fallback: generic decision text
    return "Architectural decision documented in this ADR."


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for decision field"""
    print(f"Processing DECISION field in {file_path.name}")
    
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
    
    # Check current decision value
    current_decision = frontmatter.get("decision")
    
    # Validate current value
    is_valid, validation_msg = validate_field(current_decision)
    
    if current_decision is not None:
        decision_preview = current_decision[:60] + ('...' if len(current_decision) > 60 else '')
        print(f"  Current DECISION: {decision_preview}")
        if is_valid:
            print("  OK: Decision is valid")
            return True
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Decision field not found")
    
    # Generate/fix the decision field
    if current_decision and is_valid:
        normalized_decision = normalize_field(current_decision)
    else:
        normalized_decision = generate_field(body_content)
    
    proposed_preview = normalized_decision[:60] + ('...' if len(normalized_decision) > 60 else '')
    print(f"  PROPOSED: Set decision to '{proposed_preview}'")
    
    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid
    
    if dry_run:
        print("  DRY-RUN: Would update decision field")
        return True
    
    # Update the frontmatter
    frontmatter["decision"] = normalized_decision
    
    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.decision")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")
    
    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Decision field updated")
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
    
    print(f"Processing {len(file_paths)} files for DECISION field validation/updates")
    
    success_count = 0
    error_count = 0
    
    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1
    
    print("\nSUMMARY - DECISION Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")
    
    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process DECISION field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")
    
    args = parser.parse_args()
    
    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())