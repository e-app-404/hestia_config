#!/usr/bin/env python3#!/usr/bin/env python3

"""

ADR Frontmatter Orchestrator"""

ADR Frontmatter Update Orchestrator

Coordinates individual field processors to update ADR frontmatter systematically.

Replaces monolithic approach with modular field-specific processing.Coordinates individual field processors for comprehensive ADR frontmatter management.

Systematically updates all ADR files to include required frontmatter fields:

Usage:- id, title, slug, status, related, supersedes, last_updated, date, decision

    python frontmatter_update.py [files...] [--update-dates-only] [--dry-run]

"""Uses modular field-specific processors defined in the canonical meta-structure.

"""

import argparse

import osimport argparse

import subprocessimport re

import sysimport shutil

from pathlib import Pathimport subprocess

from typing import List, Optionalimport sys

from datetime import datetime

from pathlib import Path

# Default processing order for fields

DEFAULT_FIELD_ORDER = [# Try to import toml, fallback if not available

    "id",try:

    "title",     import toml

    "slug",except ImportError:

    "status",    toml = None

    "related",

    "supersedes", try:

    "last_updated",    import yaml

    "date",except ImportError:

    "decision"    print("ERROR: pyyaml is required.")

]    sys.exit(1)



# Fields that can be empty arrays without errorSCRIPT_DIR = Path(__file__).parent

OPTIONAL_FIELDS = ["related", "supersedes"]ADR_DIR = Path("/config/hestia/library/docs/ADR")

META_CONFIG_PATH = Path("/config/hestia/config/meta/adr.toml")



class FrontmatterOrchestrator:REQUIRED_FIELDS = [

    """Coordinates individual field processors for ADR frontmatter updates."""    "id",

        "title",

    def __init__(self):    "slug",

        self.field_order = DEFAULT_FIELD_ORDER    "status",

        self.script_dir = Path(__file__).parent    "related",

            "supersedes",

    def find_processor(self, field_name: str) -> Optional[Path]:    "last_updated",

        """Find the processor script for a given field."""    "date",

        processor_path = self.script_dir / f"frontmatter-{field_name}.py"    "decision",

        if processor_path.exists():]

            return processor_pathOPTIONAL_FIELDS = ["related", "supersedes"]

        return None

    DEFAULT_FIELD_ORDER = [

    def run_field_processor(self, field_name: str, file_path: str, dry_run: bool = False) -> bool:    "id",

        """Run a specific field processor on a file."""    "title",

        processor = self.find_processor(field_name)    "slug",

        if not processor:    "status",

            print(f"WARNING: No processor found for field '{field_name}'")    "related",

            return True  # Don't fail for missing processors    "supersedes",

            "last_updated",

        cmd = ["python", str(processor), file_path]    "date",

        if dry_run:    "decision",

            cmd.append("--dry-run")]

        

        try:

            result = subprocess.run(cmd, capture_output=True, text=True)def generate_slug(title: str) -> str:

            if result.returncode != 0:    """Generate kebab-case slug from title, removing ADR-XXXX prefix"""

                print(f"ERROR: Processor for '{field_name}' failed:")    slug_base = re.sub(r"^ADR-\d+:\s*", "", title, flags=re.IGNORECASE)

                print(result.stderr)    slug = re.sub(r"[^\w\s-]", "", slug_base.lower())

                return False    slug = re.sub(r"[-\s]+", "-", slug)

            return True    return slug.strip("-")

        except Exception as e:

            print(f"ERROR: Failed to run processor for '{field_name}': {e}")

            return Falsedef extract_decision_summary(content: str) -> str:

        """Extract decision summary from document content"""

    def process_file(self, file_path: str, fields: Optional[List[str]] = None, dry_run: bool = False) -> bool:    decision_patterns = [

        """Process a single ADR file through all field processors."""        r"##\s*(?:\d+\.\s*)?Decision\s*\n\n(.*?)(?=\n##|\n```|\Z)",

        if not os.path.exists(file_path):        r"##\s*(?:\d+\.\s*)?Decision\s*\n(.*?)(?=\n##|\n```|\Z)",

            print(f"ERROR: File not found: {file_path}")    ]

            return False    for pattern in decision_patterns:

                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        # Use specified fields or default order        if match:

        fields_to_process = fields or self.field_order            decision_text = match.group(1).strip()

                    decision_text = re.sub(r"\n+", " ", decision_text)

        print(f"Processing {file_path}...")            decision_text = re.sub(r"\s+", " ", decision_text)

                    if len(decision_text) <= 200:

        success = True                return decision_text

        for field_name in fields_to_process:            sentences = re.split(r"(?<=[.!?])\s+", decision_text)

            if not self.run_field_processor(field_name, file_path, dry_run):            result = sentences[0]

                success = False            for i in range(1, len(sentences)):

                # Continue processing other fields even if one fails                if len(result + " " + sentences[i]) <= 200:

                            result += " " + sentences[i]

        return success                else:

                        break

    def process_files(self, file_paths: List[str], fields: Optional[List[str]] = None, dry_run: bool = False) -> bool:            return result

        """Process multiple ADR files."""    # Fallback: look for bullet points or any content after "Decision"

        all_success = True    decision_match = re.search(r"(?i)decision.*?[-*]\s*(.*?)(?=\n|$)", content)

            if decision_match:

        for file_path in file_paths:        return decision_match.group(1).strip()[:200]

            if not self.process_file(file_path, fields, dry_run):    # Last resort: extract from first paragraph

                all_success = False    first_para = re.search(

                r"(?:##\s*(?:\d+\.\s*)?(?:Context|Decision|Summary).*?\n\n)(.*?)(?=\n##|\n```|\Z)",

        return all_success        content,

        re.DOTALL | re.IGNORECASE,

    )

def find_adr_files(directory: str = "/config/hestia/library/docs/ADR") -> List[str]:    if first_para:

    """Find all ADR files in the specified directory."""        para_text = first_para.group(1).strip()

    adr_files = []        para_text = re.sub(r"\n+", " ", para_text)

    adr_dir = Path(directory)        para_text = re.sub(r"\s+", " ", para_text)

            return para_text[:200] + "..." if len(para_text) > 200 else para_text

    if not adr_dir.exists():    return "Architectural decision documented in this ADR."

        return []

    

    # Find all .md files that look like ADRsclass FrontmatterOrchestrator:

    for md_file in adr_dir.glob("**/*.md"):    def __init__(self):

        if "ADR-" in md_file.name and not md_file.name.startswith("."):        self.field_order = DEFAULT_FIELD_ORDER

            adr_files.append(str(md_file))        self.processors = {}

            self.meta_config = None

    return sorted(adr_files)        self.discover_processors()



    def discover_processors(self):

def main():        """Find available field processor scripts"""

    """Main entry point for the orchestrator."""        for field in self.field_order:

    parser = argparse.ArgumentParser(            processor_path = SCRIPT_DIR / f"frontmatter-{field}.py"

        description="ADR Frontmatter Orchestrator - coordinates field processors"            if processor_path.exists():

    )                self.processors[field] = processor_path

    parser.add_argument(

        "files",    def run_processor(self, field, files, dry_run=False, backup=False, validate_only=False):

        nargs="*",        """Run a single field processor"""

        help="ADR files to process (default: find all ADRs)"        if field not in self.processors:

    )            print(f"ERROR: No processor available for field '{field}'")

    parser.add_argument(            return False

        "--update-dates-only",        processor_path = self.processors[field]

        action="store_true",        cmd = [sys.executable, str(processor_path)]

        help="Only update last_updated field to current date"        if files:

    )            cmd.extend(files)

    parser.add_argument(        if dry_run:

        "--dry-run",            cmd.append("--dry-run")

        action="store_true",        if backup:

        help="Show what would be changed without modifying files"            cmd.append("--backup")

    )        if validate_only:

    parser.add_argument(            cmd.append("--validate-only")

        "--fields",        try:

        nargs="+",            print(f"\n{'=' * 60}")

        help="Specific fields to process (default: all fields)"            print(f"Running processor: {field}")

    )            print(f"{'=' * 60}")

                result = subprocess.run(cmd)

    args = parser.parse_args()            return result.returncode == 0

            except Exception as e:

    # Determine files to process            print(f"ERROR: Failed to run processor for '{field}': {e}")

    files_to_process = args.files            return False

    if not files_to_process:

        files_to_process = find_adr_files()    def process_files(

        if not files_to_process:        self, files, dry_run=False, backup=False, validate_only=False, selected_field=None

            print("No ADR files found to process")    ):

            return 1        """Coordinate processing across fields"""

            # Determine files to process

    # Determine fields to process        if not files:

    fields_to_process = None            file_paths = sorted(ADR_DIR.glob("ADR-*.md"))

    if args.update_dates_only:        else:

        fields_to_process = ["last_updated"]            file_paths = [str(Path(f).resolve()) for f in files]

    elif args.fields:        if not file_paths:

        fields_to_process = args.fields            print("No ADR files found to process")

                return 1

    # Create orchestrator and process files        # Load meta-configuration if available

    orchestrator = FrontmatterOrchestrator()        if toml and META_CONFIG_PATH.exists():

                try:

    if args.dry_run:                self.meta_config = toml.load(META_CONFIG_PATH)

        print("DRY RUN MODE - no files will be modified")                self.field_order = self.meta_config.get("processing", {}).get(

        print()                    "field_order", DEFAULT_FIELD_ORDER

                    )

    success = orchestrator.process_files(files_to_process, fields_to_process, args.dry_run)            except Exception as e:

                    print(f"WARNING: Could not load meta-configuration: {e}")

    if success:        print("ADR Frontmatter Update Orchestrator")

        print("All files processed successfully")        print("=" * 50)

        return 0        print(f"Processing {len(file_paths)} ADR files")

    else:        print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")

        print("Some files failed to process")        fields_to_process = [selected_field] if selected_field else self.field_order

        return 1        success_count = 0

        error_count = 0

        self.discover_processors()

if __name__ == "__main__":        for field in fields_to_process:

    sys.exit(main())            if field not in self.processors:
                print(f"\nSKIPPING: No processor for field '{field}'")
                continue
            success = self.run_processor(field, file_paths, dry_run, backup, validate_only)
            if success:
                success_count += 1
            else:
                error_count += 1
        print("\nORCHESTRATOR SUMMARY:")
        print(f"  Fields processed: {success_count}")
        print(f"  Fields with errors: {error_count}")
        return error_count

    def list_processors(self):
        """List available field processors"""
        print("Available field processors:")
        for field in self.field_order:
            status = "✓" if field in self.processors else "✗"
            processor_path = SCRIPT_DIR / f"frontmatter-{field}.py"
            print(f"  {status} {field:15} -> {processor_path}")

    def validate_dependencies(self):
        """Check that all required processors are available"""
        missing_processors = []
        for field in self.field_order:
            if field not in self.processors:
                missing_processors.append(field)
        if missing_processors:
            print("Missing field processors:")
            for field in missing_processors:
                print(f"  - frontmatter-{field}.py")
            return False
        return True


def update_adr_frontmatter(file_path, dry_run=False, backup=False, dates_only=False):
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
    # Handle dates-only mode
    if dates_only:
        today = datetime.now().strftime("%Y-%m-%d")
        if "last_updated" in frontmatter and frontmatter["last_updated"] != today:
            new_frontmatter = frontmatter.copy()
            new_frontmatter["last_updated"] = today
            print(f"  UPDATE: last_updated -> {today}")
            if dry_run:
                print("  DRY-RUN: Would update file")
                return True
            if backup:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_path = file_path.with_suffix(f".md.bak-{timestamp}")
                shutil.copy2(file_path, backup_path)
                print(f"  BACKUP: Created {backup_path.name}")
            ordered_frontmatter = {
                k: new_frontmatter[k] for k in DEFAULT_FIELD_ORDER if k in new_frontmatter
            }
            for k, v in new_frontmatter.items():
                if k not in ordered_frontmatter:
                    ordered_frontmatter[k] = v
            try:
                new_yaml = yaml.dump(
                    ordered_frontmatter,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
                new_content = f"---\n{new_yaml}---{body_content}"
                file_path.write_text(new_content, encoding="utf-8")
                print("  SUCCESS: File updated")
                return True
            except Exception as e:
                print(f"  ERROR: Could not write updated file: {e}")
                return False
        else:
            print("  OK: last_updated already current")
            return True
    # Check what's missing
    missing_fields = [field for field in REQUIRED_FIELDS if field not in frontmatter]
    updates_needed = []
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
    today = datetime.now().strftime("%Y-%m-%d")
    if "last_updated" in missing_fields or "last_updated" in frontmatter:
        new_frontmatter["last_updated"] = today
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
        if backup:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_path = file_path.with_suffix(f".md.bak-{timestamp}")
            shutil.copy2(file_path, backup_path)
            print(f"  BACKUP: Created {backup_path.name}")
        ordered_frontmatter = {
            k: new_frontmatter[k] for k in DEFAULT_FIELD_ORDER if k in new_frontmatter
        }
        for k, v in new_frontmatter.items():
            if k not in ordered_frontmatter:
                ordered_frontmatter[k] = v
        try:
            new_yaml = yaml.dump(
                ordered_frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
            new_content = f"---\n{new_yaml}---{body_content}"
            file_path.write_text(new_content, encoding="utf-8")
            print("  SUCCESS: File updated")
            return True
        except Exception as e:
            print(f"  ERROR: Could not write updated file: {e}")
            return False
    else:
        print("  OK: All required fields present")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="ADR Frontmatter Standardization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all ADRs with dry-run
  %(prog)s --dry-run

  # Process specific files with backup
  %(prog)s ADR-0001.md ADR-0002.md --backup

  # Validate only the 'slug' field
  %(prog)s --field slug --validate-only

  # List available processors
  %(prog)s --list-processors
""",
    )
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument(
        "--backup", action="store_true", help="Create backups before making changes"
    )
    parser.add_argument("--field", choices=DEFAULT_FIELD_ORDER, help="Process only specific field")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")
    parser.add_argument(
        "--list-processors", action="store_true", help="List available field processors"
    )
    parser.add_argument(
        "--check-dependencies",
        action="store_true",
        help="Check that all required processors are available",
    )
    parser.add_argument(
        "--update-dates-only", action="store_true", help="Only update last_updated field to today"
    )
    args = parser.parse_args()

    print("ADR Frontmatter Standardization Tool")
    print("=" * 50)
    if args.dry_run:
        print("DRY-RUN MODE: No files will be modified")
    if args.update_dates_only:
        print("DATES-ONLY MODE: Only updating last_updated fields")

    if args.list_processors or args.check_dependencies or args.field or args.validate_only:
        orchestrator = FrontmatterOrchestrator()
        if args.list_processors:
            orchestrator.list_processors()
            return 0
        if args.check_dependencies:
            if orchestrator.validate_dependencies():
                print("All required field processors are available")
                return 0
            else:
                print("Some field processors are missing")
                return 1
        return orchestrator.process_files(
            args.files,
            dry_run=args.dry_run,
            backup=args.backup,
            validate_only=args.validate_only,
            selected_field=args.field,
        )

    adr_files = (
        sorted(ADR_DIR.glob("ADR-*.md")) if not args.files else [Path(f) for f in args.files]
    )
    if not adr_files:
        print("No ADR files found!")
        return 1

    print(f"Found {len(adr_files)} ADR files to process")
    success_count = 0
    error_count = 0
    for adr_file in adr_files:
        if update_adr_frontmatter(
            adr_file, dry_run=args.dry_run, backup=args.backup, dates_only=args.update_dates_only
        ):
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
    sys.exit(main())
