#!/usr/bin/env python3
"""
Hestia Naming Convention Standardizer
Applies canonical naming with configurable guardrails

Purpose: Enforces naming standards with before/after patterns, regex validation,
and scope-based guardrails to prevent accidental file renames.

Usage:
    python naming_convention.py [--config=/path/to/hestia.toml] [--dry-run] [--index-file=path]

Compliance: ADR-0018, ADR-0024, ADR-0027
"""

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import toml
import yaml


@dataclass
class NamingOperation:
    """Represents a file naming operation"""

    original_path: str
    target_path: str
    operation_type: str
    validation_status: str
    backup_created: str
    size_bytes: int
    checksum_before: str
    checksum_after: str
    timestamp: str


class NamingStandardizer:
    """Configuration-driven naming standards enforcement"""

    def __init__(self, config_path: str = "/config/hestia/config/system/hestia.toml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Extract configuration sections first
        self.sweeper_config = self.config["automation"]["sweeper"]
        self.setup_logging()
        self.naming_rules = self.sweeper_config["naming_rules"]
        self.backup_config = self.config["backup"]
        self.safety_config = self.config["safety"]

        # Naming rules parameters
        self.scope_validation_required = self.naming_rules["scope_validation_required"]
        self.before_patterns = self.naming_rules["before_patterns"]
        self.after_pattern = self.naming_rules["after_pattern"]
        self.guardrail_regex = re.compile(self.naming_rules["guardrail_regex"])
        self.recursive_folder_paths = self.naming_rules["recursive_folder_paths"]

        # Initialize operation tracking
        self.operations: list[NamingOperation] = []
        self.stats = {
            "files_processed": 0,
            "files_renamed": 0,
            "files_skipped": 0,
            "validation_failures": 0,
            "backup_operations": 0,
            "processing_duration_seconds": 0,
        }

    def _load_config(self) -> dict:
        """Load configuration from hestia.toml"""
        try:
            with open(self.config_path) as f:
                return toml.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}") from None
        except toml.TomlDecodeError as e:
            raise ValueError(f"Invalid TOML configuration: {e}") from e

    def setup_logging(self) -> None:
        """Configure logging based on configuration"""
        log_level = logging.DEBUG if self.sweeper_config["verbose_logging"] else logging.INFO

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger("hestia.sweeper.naming")

    def load_file_index(self, index_file_path: str) -> dict:
        """Load file index from previous indexer run"""
        try:
            with open(index_file_path) as f:
                # Skip YAML frontmatter
                content = f.read()
                if content.startswith("---\n"):
                    # Find end of frontmatter
                    end_marker = content.find("\n---\n", 4)
                    if end_marker != -1:
                        json_content = content[end_marker + 5 :]
                        return json.loads(json_content)

                # Fallback to pure JSON
                return json.loads(content)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Cannot load index file {index_file_path}: {e}") from e

    def validate_file_scope(self, file_path: Path) -> bool:
        """Validate file is within allowed scope for processing"""
        if not self.scope_validation_required:
            return True

        str_path = str(file_path.resolve())

        # Check if file is within any of the recursive folder paths
        for scope_path in self.recursive_folder_paths:
            if str_path.startswith(scope_path):
                return True

        self.logger.warning(f"File outside allowed scope: {file_path}")
        return False

    def validate_naming_pattern(self, file_path: Path) -> bool:
        """Validate file matches guardrail regex pattern"""
        filename = file_path.name

        # Check if file matches the guardrail pattern
        if not self.guardrail_regex.match(filename):
            self.logger.warning(f"File does not match guardrail pattern: {filename}")
            return False

        return True

    def should_rename_file(self, file_record: dict) -> bool:
        """Determine if file should be renamed based on index data"""
        # Only rename files that are not naming compliant
        if file_record.get("naming_compliant", True):
            return False

        # Only rename backup files
        if file_record.get("category") not in ["legacy_backup"]:
            return False

        # Check if action is required
        return file_record.get("action_required") == "rename_to_canonical"

    def generate_canonical_name(self, original_path: Path) -> str:
        """Generate canonical backup filename"""
        # Extract basename without backup extensions
        name = original_path.name

        # Remove common backup extensions
        for pattern in self.before_patterns:
            pattern_regex = pattern.replace("*", ".*").replace("?", ".")
            if re.match(f"^{pattern_regex}$", name):
                # Try to extract original basename
                if name.endswith(".bak"):
                    basename = name[:-4]
                elif ".bak-" in name:
                    basename = name.split(".bak-")[0]
                elif "_backup" in name:
                    basename = name.replace("_backup", "")
                elif "_restore" in name:
                    basename = name.replace("_restore", "")
                else:
                    basename = name
                break
        else:
            basename = original_path.stem

        # Generate timestamp
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

        # Apply canonical format
        canonical_name = self.after_pattern.format(basename=basename, utc_timestamp=timestamp)

        return canonical_name

    def create_backup(self, original_path: Path) -> str | None:
        """Create backup of original file before rename"""
        if not self.safety_config["backup_before_modify"]:
            return None

        try:
            # Generate backup filename
            timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            backup_name = f"{original_path.name}.backup.{timestamp}"
            backup_path = original_path.parent / backup_name

            # Create backup
            shutil.copy2(original_path, backup_path)

            # Set permissions
            permissions = int(self.safety_config["backup_file_permissions"], 8)
            backup_path.chmod(permissions)

            self.stats["backup_operations"] += 1
            self.logger.debug(f"Created backup: {backup_path}")

            return str(backup_path)

        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to create backup for {original_path}: {e}")
            return None

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()[:16]
        except (OSError, PermissionError):
            return "unavailable"

    def rename_file_atomically(self, original_path: Path, target_path: Path) -> bool:
        """Perform atomic file rename with safety checks"""
        try:
            # Check if target already exists
            if target_path.exists():
                self.logger.warning(f"Target path already exists: {target_path}")
                return False

            # Perform atomic rename
            if self.safety_config["atomic_writes"]:
                # Use os.replace for atomic operation
                os.replace(str(original_path), str(target_path))
            else:
                # Use shutil.move as fallback
                shutil.move(str(original_path), str(target_path))

            # Set proper permissions
            permissions = int(self.backup_config["file_permissions"], 8)
            target_path.chmod(permissions)

            return True

        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to rename {original_path} to {target_path}: {e}")
            return False

    def process_file_naming(self, file_record: dict) -> NamingOperation:
        """Process naming standardization for a single file"""
        original_path = Path(file_record["path"])
        timestamp = datetime.now(UTC).isoformat()

        # Initialize operation record
        operation = NamingOperation(
            original_path=str(original_path),
            target_path="",
            operation_type="rename",
            validation_status="pending",
            backup_created="",
            size_bytes=file_record.get("size_bytes", 0),
            checksum_before=self.calculate_checksum(original_path),
            checksum_after="",
            timestamp=timestamp,
        )

        try:
            # Validate scope
            if not self.validate_file_scope(original_path):
                operation.validation_status = "scope_violation"
                self.stats["validation_failures"] += 1
                return operation

            # Validate naming pattern
            if not self.validate_naming_pattern(original_path):
                operation.validation_status = "pattern_violation"
                self.stats["validation_failures"] += 1
                return operation

            # Generate canonical name
            canonical_name = self.generate_canonical_name(original_path)
            target_path = original_path.parent / canonical_name
            operation.target_path = str(target_path)

            # Create backup if required
            backup_path = self.create_backup(original_path)
            if backup_path:
                operation.backup_created = backup_path

            # Perform rename
            if self.rename_file_atomically(original_path, target_path):
                operation.validation_status = "success"
                operation.checksum_after = self.calculate_checksum(target_path)
                self.stats["files_renamed"] += 1
                self.logger.info(f"Renamed: {original_path.name} → {canonical_name}")
            else:
                operation.validation_status = "rename_failed"
                # Restore from backup if rename failed
                if backup_path and Path(backup_path).exists():
                    try:
                        shutil.move(backup_path, str(original_path))
                        self.logger.info(f"Restored from backup: {original_path}")
                    except (OSError, PermissionError) as e:
                        self.logger.error(f"Failed to restore from backup: {e}")

        except Exception as e:
            operation.validation_status = f"error: {e}"
            self.logger.error(f"Error processing {original_path}: {e}")

        self.stats["files_processed"] += 1
        return operation

    def process_file_index(self, index_data: dict, dry_run: bool = False) -> None:
        """Process files from index data"""
        start_time = datetime.now(UTC)
        file_registry = index_data.get("file_registry", [])

        self.logger.info(f"Processing {len(file_registry)} files from index")

        for file_record in file_registry:
            if self.should_rename_file(file_record):
                if dry_run:
                    self.logger.info(f"Would rename: {file_record['path']}")
                    self.stats["files_processed"] += 1
                else:
                    operation = self.process_file_naming(file_record)
                    self.operations.append(operation)
            else:
                self.stats["files_skipped"] += 1

        self.stats["processing_duration_seconds"] = int(
            (datetime.now(UTC) - start_time).total_seconds()
        )

        duration = self.stats["processing_duration_seconds"]
        self.logger.info(f"Naming processing completed in {duration:.2f}s")

    def generate_naming_report(self) -> dict:
        """Generate comprehensive naming operation report"""
        timestamp = datetime.now(UTC).isoformat()

        report_data = {
            "metadata": {
                "tool": "hestia.sweeper.naming_convention",
                "script": __file__,
                "created_at": timestamp,
                "batch_id": (
                    f"naming_standardization_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
                ),
                "rows_processed": len(self.operations),
                "content_hash": self._calculate_content_hash(),
                "config_version": self.config["meta"]["version"],
                "compliance_adrs": self.config["meta"]["compliance_adrs"],
            },
            "configuration": {
                "scope_validation_required": self.scope_validation_required,
                "before_patterns": self.before_patterns,
                "after_pattern": self.after_pattern,
                "guardrail_regex": self.naming_rules["guardrail_regex"],
                "recursive_folder_paths": self.recursive_folder_paths,
                "safety_settings": dict(self.safety_config),
            },
            "statistics": self.stats,
            "operations": [asdict(op) for op in self.operations],
            "summary": {
                "successful_renames": len(
                    [op for op in self.operations if op.validation_status == "success"]
                ),
                "failed_operations": len(
                    [op for op in self.operations if "error" in op.validation_status]
                ),
                "scope_violations": len(
                    [op for op in self.operations if op.validation_status == "scope_violation"]
                ),
                "pattern_violations": len(
                    [op for op in self.operations if op.validation_status == "pattern_violation"]
                ),
            },
        }

        return report_data

    def _calculate_content_hash(self) -> str:
        """Calculate hash of operations for integrity checking"""
        content = json.dumps([asdict(op) for op in self.operations], sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def update_shared_log(self, log_file_path: str) -> None:
        """Update shared log file with naming operation results"""
        try:
            log_path = Path(log_file_path)

            if not log_path.exists():
                self.logger.warning(f"Shared log file not found: {log_file_path}")
                return

            # Read existing log
            with open(log_path) as f:
                content = f.read()

            # Parse existing data
            if content.startswith("---\n"):
                end_marker = content.find("\n---\n", 4)
                if end_marker != -1:
                    frontmatter_content = content[4:end_marker]
                    json_content = content[end_marker + 5 :]

                    # Parse frontmatter and JSON
                    frontmatter = yaml.safe_load(frontmatter_content)
                    existing_data = json.loads(json_content)

                    # Add naming operation results
                    existing_data["naming_operations"] = {
                        "statistics": self.stats,
                        "operations_count": len(self.operations),
                        "successful_renames": len(
                            [op for op in self.operations if op.validation_status == "success"]
                        ),
                        "processing_timestamp": datetime.now(UTC).isoformat(),
                    }

                    # Update frontmatter
                    frontmatter["rows_processed"] = frontmatter.get("rows_processed", 0) + len(
                        self.operations
                    )
                    frontmatter["content_hash"] = hashlib.sha256(
                        json.dumps(existing_data, sort_keys=True).encode()
                    ).hexdigest()[:16]

                    # Write updated log
                    with open(log_path, "w") as f:
                        f.write("---\n")
                        yaml.dump(frontmatter, f, default_flow_style=False)
                        f.write("---\n\n")
                        json.dump(existing_data, f, indent=2, sort_keys=True)

                    self.logger.info(f"Updated shared log: {log_file_path}")

        except (OSError, json.JSONDecodeError, yaml.YAMLError) as e:
            self.logger.error(f"Failed to update shared log: {e}")


def main():
    """Main entry point for naming standardizer"""
    parser = argparse.ArgumentParser(description="Hestia Naming Convention Standardizer")
    parser.add_argument(
        "--config",
        default="/config/hestia/config/system/hestia.toml",
        help="Path to hestia.toml configuration file",
    )
    parser.add_argument("--index-file", required=True, help="Path to file index log from indexer")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be renamed without making changes"
    )
    parser.add_argument("--update-log", help="Path to shared log file to update with results")

    args = parser.parse_args()

    try:
        # Initialize standardizer
        standardizer = NamingStandardizer(args.config)

        # Load file index
        index_data = standardizer.load_file_index(args.index_file)

        # Process naming operations
        standardizer.process_file_index(index_data, dry_run=args.dry_run)

        # Generate and display results
        if not args.dry_run:
            report = standardizer.generate_naming_report()
            print("✅ Naming standardization completed:")
            print(f"  Files processed: {report['statistics']['files_processed']}")
            print(f"  Files renamed: {report['statistics']['files_renamed']}")
            print(f"  Files skipped: {report['statistics']['files_skipped']}")
            print(f"  Validation failures: {report['statistics']['validation_failures']}")

            # Update shared log if specified
            if args.update_log:
                standardizer.update_shared_log(args.update_log)
        else:
            print("🔍 Dry-run completed - no changes made")
            print(f"  Files that would be processed: {standardizer.stats['files_processed']}")

        return 0

    except Exception as e:
        logging.error(f"Naming standardizer failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
