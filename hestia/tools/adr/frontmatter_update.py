#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

ADR Frontmatter Update Orchestrator""""""



Coordinates individual field processors for comprehensive ADR frontmatter management.ADR Frontmatter Update OrchestratorADR Frontmatter Standardization Tool

Uses modular field-specific processors defined in the canonical meta-structure.

"""



import argparseCoordinates individual field processors for comprehensive ADR frontmatter management.Systematically updates all ADR files to include required frontmatter fields:

import subprocess

import sysUses modular field-specific processors defined in the canonical meta-structure.- id, title, slug, status, related, supersedes, last_updated, date, decision

from pathlib import Path

"""

SCRIPT_DIR = Path(__file__).parent

ADR_DIR = Path("/config/hestia/library/docs/ADR")Usage: python3 adr_frontmatter_update.py [--dry-run] [--backup]



# Field processing orderimport argparse"""

DEFAULT_FIELD_ORDER = [

    "id", "title", "slug", "status", "related", import subprocess

    "supersedes", "last_updated", "date", "decision"

]import sysimport argparse



class FrontmatterOrchestrator:from datetime import datetimeimport re

    def __init__(self):

        self.field_order = DEFAULT_FIELD_ORDERfrom pathlib import Pathimport shutil

        self.processors = {}

        self.discover_processors()from datetime import datetime

    

    def discover_processors(self):# Try to import toml, fallback if not availablefrom pathlib import Path

        """Find available field processor scripts"""

        for field in self.field_order:try:

            processor_path = SCRIPT_DIR / f"frontmatter-{field}.py"

            if processor_path.exists():    import tomlimport yaml

                self.processors[field] = processor_path

    except ImportError:

    def run_processor(self, field, files, dry_run=False, backup=False, validate_only=False):

        """Run a single field processor"""    print("WARNING: toml module not available, using basic configuration")ADR_DIR = Path("/config/hestia/library/docs/ADR")

        if field not in self.processors:

            print(f"ERROR: No processor available for field '{field}'")    toml = NoneREQUIRED_FIELDS = [

            return False

            "id",

        processor_path = self.processors[field]

        cmd = [sys.executable, str(processor_path)]SCRIPT_DIR = Path(__file__).parent    "title",

        

        # Add files to processMETA_CONFIG_PATH = Path("/config/hestia/config/meta/adr.toml")    "slug",

        if files:

            cmd.extend(files)ADR_DIR = Path("/config/hestia/library/docs/ADR")    "status",

        

        # Add flags    "related",

        if dry_run:

            cmd.append('--dry-run')# Fallback field order if TOML config not available    "supersedes",

        if backup:

            cmd.append('--backup')DEFAULT_FIELD_ORDER = [    "last_updated",

        if validate_only:

            cmd.append('--validate-only')    "id", "title", "slug", "status", "related",     "date",

        

        try:    "supersedes", "last_updated", "date", "decision"    "decision",

            print(f"\n{'='*60}")

            print(f"Running processor: {field}")]]

            print(f"{'='*60}")

            OPTIONAL_FIELDS = ["related", "supersedes"]  # Can be empty arrays

            result = subprocess.run(cmd)

            return result.returncode == 0class FrontmatterOrchestrator:

        

        except Exception as e:    def __init__(self):

            print(f"ERROR: Failed to run processor for '{field}': {e}")

            return False        self.field_order = DEFAULT_FIELD_ORDERdef generate_slug(title):

    

    def process_files(self, files, dry_run=False, backup=False, validate_only=False,         self.processors = {}    """Generate kebab-case slug from title, removing ADR-XXXX prefix"""

                     selected_field=None):

        """Coordinate processing across fields"""        self.meta_config = None    # Remove ADR-XXXX: prefix

        

        # Determine files to process            slug_base = re.sub(r"^ADR-\d+:\s*", "", title, flags=re.IGNORECASE)

        if not files:

            file_paths = sorted(ADR_DIR.glob("ADR-*.md"))        # Load meta-configuration if available    # Convert to lowercase and replace spaces/special chars with hyphens

        else:

            file_paths = [str(Path(f).resolve()) for f in files]        if toml and META_CONFIG_PATH.exists():    slug = re.sub(r"[^\w\s-]", "", slug_base.lower())

        

        if not file_paths:            try:    slug = re.sub(r"[-\s]+", "-", slug)

            print("No ADR files found to process")

            return 1                self.meta_config = toml.load(META_CONFIG_PATH)    return slug.strip("-")

        

        print("ADR Frontmatter Update Orchestrator")                self.field_order = self.meta_config.get('processing', {}).get('field_order', DEFAULT_FIELD_ORDER)

        print("=" * 50)

        print(f"Processing {len(file_paths)} ADR files")            except Exception as e:

        print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")

                        print(f"WARNING: Could not load meta-configuration: {e}")def extract_decision_summary(content):

        # Determine which fields to process

        fields_to_process = [selected_field] if selected_field else self.field_order            """Extract decision summary from document content"""

        

        success_count = 0        # Discover available processors    # Look for Decision section

        error_count = 0

                self.discover_processors()    decision_patterns = [

        # Process each field

        for field in fields_to_process:            r"##\s*(?:\d+\.\s*)?Decision\s*\n\n(.*?)(?=\n##|\n```|\Z)",

            if field not in self.processors:

                print(f"\nSKIPPING: No processor for field '{field}'")    def discover_processors(self):        r"##\s*(?:\d+\.\s*)?Decision\s*\n(.*?)(?=\n##|\n```|\Z)",

                continue

                    """Find available field processor scripts"""    ]

            success = self.run_processor(field, file_paths, dry_run, backup, validate_only)

            if success:        for field in self.field_order:

                success_count += 1

            else:            processor_path = SCRIPT_DIR / f"frontmatter-{field}.py"    for pattern in decision_patterns:

                error_count += 1

                    if processor_path.exists():        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        print(f"\nORCHESTRATOR SUMMARY:")

        print(f"  Fields processed: {success_count}")                self.processors[field] = processor_path        if match:

        print(f"  Fields with errors: {error_count}")

                    else:            decision_text = match.group(1).strip()

        return error_count

                    print(f"WARNING: Processor for field '{field}' not found at {processor_path}")            # Clean up and get first sentence or two

    def list_processors(self):

        """List available field processors"""                decision_text = re.sub(r"\n+", " ", decision_text)

        print("Available field processors:")

        for field in self.field_order:    def run_processor(self, field, files, dry_run=False, backup=False, validate_only=False):            decision_text = re.sub(r"\s+", " ", decision_text)

            status = "✓" if field in self.processors else "✗"

            processor_path = SCRIPT_DIR / f"frontmatter-{field}.py"        """Run a single field processor"""

            print(f"  {status} {field:15} -> {processor_path}")

        if field not in self.processors:            # Get first 200 chars or complete sentences

def main():

    parser = argparse.ArgumentParser(description='ADR Frontmatter Update Orchestrator')            print(f"ERROR: No processor available for field '{field}'")            if len(decision_text) <= 200:

    parser.add_argument('files', nargs='*', help='ADR files to process (default: all)')

    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')            return False                return decision_text

    parser.add_argument('--backup', action='store_true', help='Create backups before changes')

    parser.add_argument('--field', choices=DEFAULT_FIELD_ORDER, help='Process only specific field')        

    parser.add_argument('--validate-only', action='store_true', help='Only validate, no changes')

    parser.add_argument('--list-processors', action='store_true', help='List available processors')        processor_path = self.processors[field]            # Try to break at sentence boundary

    

    args = parser.parse_args()        cmd = [sys.executable, str(processor_path)]            sentences = re.split(r"(?<=[.!?])\s+", decision_text)

    

    orchestrator = FrontmatterOrchestrator()                    result = sentences[0]

    

    if args.list_processors:        # Add files to process            for i in range(1, len(sentences)):

        orchestrator.list_processors()

        return 0        if files:                if len(result + " " + sentences[i]) <= 200:

    

    return orchestrator.process_files(            cmd.extend(files)                    result += " " + sentences[i]

        args.files, 

        dry_run=args.dry_run,                        else:

        backup=args.backup,

        validate_only=args.validate_only,        # Add flags                    break

        selected_field=args.field

    )        if dry_run:            return result



if __name__ == '__main__':            cmd.append('--dry-run')

    sys.exit(main())
        if backup:    # Fallback: look for bullet points or any content after "Decision"

            cmd.append('--backup')    decision_match = re.search(r"(?i)decision.*?[-*]\s*(.*?)(?=\n|$)", content)

        if validate_only:    if decision_match:

            cmd.append('--validate-only')        return decision_match.group(1).strip()[:200]

        

        try:    # Last resort: extract from first paragraph

            print(f"\n{'='*60}")    first_para = re.search(

            print(f"Running processor: {field}")        r"(?:##\s*(?:\d+\.\s*)?(?:Context|Decision|Summary).*?\n\n)(.*?)(?=\n##|\n```|\Z)",

            print(f"{'='*60}")        content,

                    re.DOTALL | re.IGNORECASE,

            result = subprocess.run(cmd, capture_output=False, text=True)    )

            return result.returncode == 0    if first_para:

                para_text = first_para.group(1).strip()

        except Exception as e:        para_text = re.sub(r"\n+", " ", para_text)

            print(f"ERROR: Failed to run processor for '{field}': {e}")        para_text = re.sub(r"\s+", " ", para_text)

            return False        return para_text[:200] + "..." if len(para_text) > 200 else para_text

    

    def process_files(self, files, dry_run=False, backup=False, validate_only=False,     return "Architectural decision documented in this ADR."

                     selected_field=None, parallel=False):

        """Coordinate processing across fields"""

        def update_adr_frontmatter(file_path, dry_run=False, backup=False, dates_only=False):

        # Determine files to process    """Update a single ADR file's frontmatter"""

        if not files:    print(f"\nProcessing {file_path.name}...")

            file_paths = sorted(ADR_DIR.glob("ADR-*.md"))

        else:    try:

            file_paths = [str(Path(f).resolve()) for f in files]        content = file_path.read_text(encoding="utf-8")

            except Exception as e:

        if not file_paths:        print(f"  ERROR: Could not read file: {e}")

            print("No ADR files found to process")        return False

            return 1

            if not content.startswith("---"):

        print(f"ADR Frontmatter Update Orchestrator")        print("  SKIP: No YAML frontmatter found")

        print(f"{'='*50}")        return False

        print(f"Processing {len(file_paths)} ADR files")

        print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")    try:

        print(f"Backup: {'YES' if backup else 'NO'}")        # Split content into frontmatter and body

        print(f"Validate-only: {'YES' if validate_only else 'NO'}")        parts = content.split("---", 2)

                if len(parts) < 3:

        # Determine which fields to process            print("  ERROR: Invalid YAML frontmatter structure")

        fields_to_process = [selected_field] if selected_field else self.field_order            return False

        

        success_count = 0        yaml_content = parts[1]

        error_count = 0        body_content = parts[2]

        

        # Process each field        # Parse existing frontmatter

        for field in fields_to_process:        frontmatter = yaml.safe_load(yaml_content) or {}

            if field not in self.processors:

                print(f"\nSKIPPING: No processor for field '{field}'")    except Exception as e:

                continue        print(f"  ERROR: Could not parse YAML frontmatter: {e}")

                    return False

            success = self.run_processor(field, file_paths, dry_run, backup, validate_only)

            if success:    # Handle dates-only mode

                success_count += 1    if dates_only:

            else:        today = datetime.now().strftime("%Y-%m-%d")

                error_count += 1        if "last_updated" in frontmatter and frontmatter["last_updated"] != today:

                print(f"ERROR: Processing failed for field '{field}'")            new_frontmatter = frontmatter.copy()

                            new_frontmatter["last_updated"] = today

                # Stop on first error unless in validate-only mode            updates_needed = [f"last_updated: {today}"]

                if not validate_only:            print(f"  UPDATE: last_updated -> {today}")

                    break        else:

                    print("  OK: last_updated already current")

        # Final summary            return True

        print(f"\n{'='*60}")    else:

        print(f"ORCHESTRATOR SUMMARY")        # Check what's missing

        print(f"{'='*60}")        missing_fields = []

        print(f"Fields processed successfully: {success_count}")        updates_needed = []

        print(f"Fields with errors: {error_count}")

        print(f"Total fields attempted: {len(fields_to_process)}")        for field in REQUIRED_FIELDS:

                    if field not in frontmatter:

        if not dry_run and not validate_only and success_count > 0:                missing_fields.append(field)

            print(f"\nSUGGESTION: Run 'python3 /config/bin/adr-index.py' to regenerate governance index")

                if not missing_fields:

        return error_count            print("  OK: All required fields present")

                return True

    def validate_dependencies(self):

        """Check that all required processors are available"""        print(f"  MISSING: {', '.join(missing_fields)}")

        missing_processors = []

        for field in self.field_order:        # Generate missing fields

            if field not in self.processors:        new_frontmatter = frontmatter.copy()

                missing_processors.append(field)        updates_needed = []

        

        if missing_processors:        # Generate ID from filename if missing

            print("Missing field processors:")        if "id" in missing_fields:

            for field in missing_processors:            id_match = re.search(r"ADR-(\d+)", file_path.name)

                print(f"  - frontmatter-{field}.py")            if id_match:

            return False                new_frontmatter["id"] = f"ADR-{id_match.group(1)}"

                        updates_needed.append(f"id: {new_frontmatter['id']}")

        return True

            # Generate slug if missing

    def list_processors(self):        if "slug" in missing_fields and "title" in frontmatter:

        """List available field processors"""            new_frontmatter["slug"] = generate_slug(frontmatter["title"])

        print("Available field processors:")            updates_needed.append(f"slug: {new_frontmatter['slug']}")

        for field in self.field_order:

            status = "✓" if field in self.processors else "✗"        # Add empty arrays for related/supersedes if missing

            processor_path = SCRIPT_DIR / f"frontmatter-{field}.py"        if "related" in missing_fields:

            print(f"  {status} {field:15} -> {processor_path}")            new_frontmatter["related"] = []

            updates_needed.append("related: []")

def main():

    parser = argparse.ArgumentParser(        if "supersedes" in missing_fields:

        description='ADR Frontmatter Update Orchestrator',            new_frontmatter["supersedes"] = []

        formatter_class=argparse.RawDescriptionHelpFormatter,            updates_needed.append("supersedes: []")

        epilog="""

Examples:        # Update last_updated to current date

  # Process all ADRs with dry-run        today = datetime.now().strftime("%Y-%m-%d")

  %(prog)s --dry-run        if "last_updated" in missing_fields or "last_updated" in frontmatter:

              new_frontmatter["last_updated"] = today

  # Process specific files with backup            updates_needed.append(f"last_updated: {new_frontmatter['last_updated']}")

  %(prog)s ADR-0001.md ADR-0002.md --backup

          # Generate decision summary if missing

  # Validate only the 'slug' field        if "decision" in missing_fields:

  %(prog)s --field slug --validate-only            decision_summary = extract_decision_summary(body_content)

              new_frontmatter["decision"] = decision_summary

  # List available processors            updates_needed.append(f'decision: "{decision_summary[:50]}..."')

  %(prog)s --list-processors

        """        if updates_needed:

    )            print(f"  UPDATES: {'; '.join(updates_needed)}")

    

    parser.add_argument('files', nargs='*', help='ADR files to process (default: all)')    # Common logic for both modes

    parser.add_argument('--dry-run', action='store_true',     if dry_run:

                       help='Show changes without applying them')        print("  DRY-RUN: Would update file")

    parser.add_argument('--backup', action='store_true',         return True

                       help='Create backups before making changes')

    parser.add_argument('--field', choices=DEFAULT_FIELD_ORDER,    # Create backup if requested

                       help='Process only specific field')    if backup:

    parser.add_argument('--validate-only', action='store_true',        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

                       help='Only validate fields, make no changes')        backup_path = file_path.with_suffix(f".md.bak-{timestamp}")

    parser.add_argument('--list-processors', action='store_true',        shutil.copy2(file_path, backup_path)

                       help='List available field processors and exit')        print(f"  BACKUP: Created {backup_path.name}")

    parser.add_argument('--check-dependencies', action='store_true',

                       help='Check that all required processors are available')    # Rebuild frontmatter in correct order

        ordered_frontmatter = {}

    args = parser.parse_args()    field_order = [

            "id",

    orchestrator = FrontmatterOrchestrator()        "title",

            "slug",

    if args.list_processors:        "status",

        orchestrator.list_processors()        "related",

        return 0        "supersedes",

            "last_updated",

    if args.check_dependencies:        "date",

        if orchestrator.validate_dependencies():        "decision",

            print("All required field processors are available")    ]

            return 0

        else:    # Add required fields in order

            print("Some field processors are missing")    for field in field_order:

            return 1        if field in new_frontmatter:

                ordered_frontmatter[field] = new_frontmatter[field]

    return orchestrator.process_files(

        args.files,     # Add any remaining fields

        dry_run=args.dry_run,    for field, value in new_frontmatter.items():

        backup=args.backup,        if field not in ordered_frontmatter:

        validate_only=args.validate_only,            ordered_frontmatter[field] = value

        selected_field=args.field

    )    # Generate new YAML content

    try:

if __name__ == '__main__':        new_yaml = yaml.dump(

    sys.exit(main())            ordered_frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
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
    elif args.update_dates_only:
        print("DATES-ONLY MODE: Only updating last_updated fields")

    adr_files = sorted(ADR_DIR.glob("ADR-*.md"))
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
    exit(main())
