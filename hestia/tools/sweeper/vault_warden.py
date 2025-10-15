#!/usr/bin/env python3
"""
Hestia Vault Retention Manager
Keep N latest per basename with configurable policies

Purpose: Manages vault retention by keeping the latest N backups per basename,
with intelligent file family detection and configurable policies.

Usage:
    python vault_warden.py [--config=/path/to/hestia.toml] [--dry-run] [--index-file=path]

Compliance: ADR-0018, ADR-0024, ADR-0027
"""

import argparse
import hashlib
import json
import logging
import shutil
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import toml
import yaml


@dataclass
class VaultOperation:
    """Represents a vault management operation"""
    file_path: str
    basename_group: str
    operation_type: str
    retention_count: int
    age_rank: int
    size_bytes: int
    destination: str
    status: str
    backup_created: str
    checksum_before: str
    error_message: str
    timestamp: str


class VaultRetentionManager:
    """Configuration-driven vault retention management"""
    
    def __init__(self, config_path: str = "/config/hestia/config/system/hestia.toml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Extract configuration sections first
        self.retention_config = self.config['retention']
        self.vault_config = self.config['paths']['vault']
        self.safety_config = self.config['safety']
        self.sweeper_config = self.config['automation']['sweeper']
        self.setup_logging()
        
        # Vault-specific settings
        self.vault_policy = self.retention_config['vault_backups']
        self.keep_latest_count = self.vault_policy['keep_latest']
        self.vault_location = self.vault_policy['location']
        
        # Initialize operation tracking
        self.operations: list[VaultOperation] = []
        self.basename_groups: dict[str, list[dict]] = defaultdict(list)
        self.stats = {
            'files_processed': 0,
            'basename_groups_found': 0,
            'files_retained': 0,
            'files_removed': 0,
            'bytes_freed': 0,
            'vault_integrity_issues': 0,
            'processing_duration_seconds': 0
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
        log_level = logging.DEBUG if self.sweeper_config['verbose_logging'] else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
            ]
        )
        self.logger = logging.getLogger('hestia.sweeper.vault')

    def load_file_index(self, index_file_path: str) -> dict:
        """Load file index from previous component run"""
        try:
            with open(index_file_path) as f:
                content = f.read()
                if content.startswith('---\n'):
                    end_marker = content.find('\n---\n', 4)
                    if end_marker != -1:
                        json_content = content[end_marker + 5:]
                        return json.loads(json_content)
                
                return json.loads(content)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Cannot load index file {index_file_path}: {e}") from e

    def extract_basename(self, file_path: Path) -> str:
        """Extract logical basename from backup filename"""
        filename = file_path.name
        
        # Handle canonical backup format (*.bk.YYYYMMDDTHHMMSSZ)
        if '.bk.' in filename:
            return filename.split('.bk.')[0]
        
        # Handle legacy formats
        if filename.endswith('.bak'):
            return filename[:-4]
        elif '.bak-' in filename:
            return filename.split('.bak-')[0]
        elif '_backup' in filename:
            return filename.replace('_backup', '')
        elif '_restore' in filename:
            return filename.replace('_restore', '')
        
        # Fallback to stem
        return file_path.stem

    def group_files_by_basename(self, file_registry: list[dict]) -> None:
        """Group vault files by logical basename"""
        vault_files = []
        
        # Filter for vault-eligible files
        for file_record in file_registry:
            if file_record.get('vault_eligible', False):
                vault_files.append(file_record)
        
        # Group by basename
        for file_record in vault_files:
            file_path = Path(file_record['path'])
            
            # Only process files actually in vault location
            if not str(file_path).startswith(self.vault_location):
                continue
            
            basename = self.extract_basename(file_path)
            self.basename_groups[basename].append(file_record)
        
        self.stats['basename_groups_found'] = len(self.basename_groups)
        vault_count = len(vault_files)
        group_count = len(self.basename_groups)
        self.logger.info(f"Found {vault_count} vault files in {group_count} basename groups")

    def should_manage_vault_file(self, file_record: dict) -> bool:
        """Determine if file should be managed by vault retention"""
        return file_record.get('vault_eligible', False)

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()[:16]
        except (OSError, PermissionError):
            return "unavailable"

    def create_backup(self, original_path: Path) -> str | None:
        """Create backup of original file before vault operation"""
        if not self.safety_config['backup_before_modify']:
            return None
        
        try:
            # Generate backup filename
            timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
            backup_name = f"{original_path.name}.vault_backup.{timestamp}"
            backup_path = original_path.parent / backup_name
            
            # Create backup
            shutil.copy2(original_path, backup_path)
            
            # Set permissions
            permissions = int(self.safety_config['backup_file_permissions'], 8)
            backup_path.chmod(permissions)
            
            self.logger.debug(f"Created vault backup: {backup_path}")
            return str(backup_path)
            
        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to create backup for {original_path}: {e}")
            return None

    def remove_vault_file(self, file_path: Path) -> bool:
        """Remove file from vault"""
        try:
            file_path.unlink()
            self.logger.debug(f"Removed from vault: {file_path}")
            return True
            
        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to remove {file_path}: {e}")
            return False

    def sort_files_by_age(self, file_group: list[dict]) -> list[dict]:
        """Sort files by modification time (newest first)"""
        return sorted(
            file_group, 
            key=lambda f: f.get('modified_time', ''), 
            reverse=True
        )

    def manage_basename_group(self, basename: str, file_group: list[dict]) -> list[VaultOperation]:
        """Manage retention for a basename group"""
        operations = []
        
        # Sort files by age (newest first)
        sorted_files = self.sort_files_by_age(file_group)
        
        self.logger.debug(f"Managing {len(sorted_files)} files for basename '{basename}'")
        
        for i, file_record in enumerate(sorted_files):
            file_path = Path(file_record['path'])
            timestamp = datetime.now(UTC).isoformat()
            
            # Initialize operation record
            operation = VaultOperation(
                file_path=str(file_path),
                basename_group=basename,
                operation_type="vault_retention",
                retention_count=self.keep_latest_count,
                age_rank=i + 1,
                size_bytes=file_record.get('size_bytes', 0),
                destination="",
                status="pending",
                backup_created="",
                checksum_before=self.calculate_checksum(file_path),
                error_message="",
                timestamp=timestamp
            )
            
            try:
                if i < self.keep_latest_count:
                    # Keep this file (within retention limit)
                    operation.operation_type = "retain"
                    operation.status = "retained"
                    operation.destination = "vault_kept"
                    self.stats['files_retained'] += 1
                    self.logger.debug(f"Retaining {file_path.name} (rank {i + 1})")
                else:
                    # Remove this file (exceeds retention limit)
                    operation.operation_type = "remove"
                    
                    # Create backup if configured
                    backup_path = self.create_backup(file_path)
                    if backup_path:
                        operation.backup_created = backup_path
                    
                    # Remove file
                    if self.remove_vault_file(file_path):
                        operation.status = "removed"
                        operation.destination = "deleted"
                        self.stats['files_removed'] += 1
                        self.stats['bytes_freed'] += operation.size_bytes
                        self.logger.info(
                            f"Removed excess vault file: {file_path.name} (rank {i + 1})"
                        )
                    else:
                        operation.status = "remove_failed"
                        operation.error_message = "Failed to remove file"
                        self.stats['vault_integrity_issues'] += 1
                
            except Exception as e:
                operation.status = "error"
                operation.error_message = str(e)
                self.stats['vault_integrity_issues'] += 1
                self.logger.error(f"Error managing {file_path}: {e}")
            
            operations.append(operation)
        
        return operations

    def process_vault_retention(self, index_data: dict, dry_run: bool = False) -> None:
        """Process vault retention operations from index data"""
        start_time = datetime.now(UTC)
        file_registry = index_data.get('file_registry', [])
        
        # Group files by basename
        self.group_files_by_basename(file_registry)
        
        group_count = len(self.basename_groups)
        self.logger.info(f"Processing vault retention for {group_count} basename groups")
        
        for basename, file_group in self.basename_groups.items():
            if dry_run:
                sorted_files = self.sort_files_by_age(file_group)
                files_to_remove = len(sorted_files) - self.keep_latest_count
                if files_to_remove > 0:
                    self.logger.info(
                        f"Would remove {files_to_remove} files from group '{basename}'"
                    )
                self.stats['files_processed'] += len(file_group)
            else:
                group_operations = self.manage_basename_group(basename, file_group)
                self.operations.extend(group_operations)
                self.stats['files_processed'] += len(file_group)
        
        self.stats['processing_duration_seconds'] = int((
            datetime.now(UTC) - start_time
        ).total_seconds())
        
        duration = self.stats['processing_duration_seconds']
        self.logger.info(f"Vault retention processing completed in {duration}s")

    def verify_vault_integrity(self) -> dict:
        """Verify vault integrity and structure"""
        integrity_report = {
            'vault_location_exists': False,
            'vault_permissions_correct': False,
            'orphaned_backups': [],
            'naming_violations': [],
            'size_distribution': {},
            'total_vault_size_mb': 0
        }
        
        vault_path = Path(self.vault_location)
        
        # Check vault location exists
        if vault_path.exists() and vault_path.is_dir():
            integrity_report['vault_location_exists'] = True
            
            # Check permissions
            try:
                expected_perms = int(self.config['security']['vault_permissions'], 8)
                actual_perms = oct(vault_path.stat().st_mode)[-3:]
                integrity_report['vault_permissions_correct'] = (
                    int(actual_perms, 8) == expected_perms
                )
            except (OSError, ValueError):
                pass
            
            # Analyze vault contents
            total_size = 0
            for file_path in vault_path.rglob('*'):
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        total_size += size
                        
                        # Check naming compliance
                        if (not file_path.name.endswith('.bk.' + 'Z') and 
                            not any(pattern in file_path.name.lower() 
                                   for pattern in ['bak', 'backup', 'restore'])):
                            integrity_report['orphaned_backups'].append(str(file_path))
                        
                    except OSError:
                        continue
            
            integrity_report['total_vault_size_mb'] = round(total_size / 1024 / 1024, 2)
        
        return integrity_report

    def generate_vault_report(self) -> dict:
        """Generate comprehensive vault management report"""
        timestamp = datetime.now(UTC).isoformat()
        
        # Verify vault integrity
        integrity_report = self.verify_vault_integrity()
        
        report_data = {
            'metadata': {
                'tool': 'hestia.sweeper.vault_warden',
                'script': __file__,
                'created_at': timestamp,
                'batch_id': (
                    f"vault_retention_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
                ),
                'rows_processed': len(self.operations),
                'content_hash': self._calculate_content_hash(),
                'config_version': self.config['meta']['version'],
                'compliance_adrs': self.config['meta']['compliance_adrs']
            },
            'configuration': {
                'keep_latest_count': self.keep_latest_count,
                'vault_location': self.vault_location,
                'vault_policy': dict(self.vault_policy),
                'safety_settings': dict(self.safety_config)
            },
            'statistics': self.stats,
            'integrity_report': integrity_report,
            'operations': [asdict(op) for op in self.operations],
            'summary': {
                'successful_retentions': len([
                    op for op in self.operations if op.status == 'retained'
                ]),
                'successful_removals': len([
                    op for op in self.operations if op.status == 'removed'
                ]),
                'failed_operations': len([
                    op for op in self.operations if 'failed' in op.status or op.status == 'error'
                ]),
                'bytes_freed_mb': round(self.stats['bytes_freed'] / 1024 / 1024, 2),
                'vault_health_score': self._calculate_vault_health_score(integrity_report)
            }
        }
        
        return report_data

    def _calculate_vault_health_score(self, integrity_report: dict) -> float:
        """Calculate vault health score (0-100)"""
        score = 100.0
        
        if not integrity_report['vault_location_exists']:
            score -= 30
        
        if not integrity_report['vault_permissions_correct']:
            score -= 20
        
        orphaned_count = len(integrity_report['orphaned_backups'])
        if orphaned_count > 0:
            score -= min(25, orphaned_count * 5)
        
        if self.stats['vault_integrity_issues'] > 0:
            score -= min(25, self.stats['vault_integrity_issues'] * 10)
        
        return max(0.0, score)

    def _calculate_content_hash(self) -> str:
        """Calculate hash of operations for integrity checking"""
        content = json.dumps([asdict(op) for op in self.operations], sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def update_shared_log(self, log_file_path: str) -> None:
        """Update shared log file with vault operation results"""
        try:
            log_path = Path(log_file_path)
            
            if not log_path.exists():
                self.logger.warning(f"Shared log file not found: {log_file_path}")
                return
            
            # Read existing log
            with open(log_path) as f:
                content = f.read()
            
            # Parse existing data
            if content.startswith('---\n'):
                end_marker = content.find('\n---\n', 4)
                if end_marker != -1:
                    frontmatter_content = content[4:end_marker]
                    json_content = content[end_marker + 5:]
                    
                    # Parse frontmatter and JSON
                    frontmatter = yaml.safe_load(frontmatter_content)
                    existing_data = json.loads(json_content)
                    
                    # Add vault operation results
                    existing_data['vault_operations'] = {
                        'statistics': self.stats,
                        'operations_count': len(self.operations),
                        'basename_groups': len(self.basename_groups),
                        'bytes_freed': self.stats['bytes_freed'],
                        'processing_timestamp': datetime.now(UTC).isoformat()
                    }
                    
                    # Update frontmatter
                    frontmatter['rows_processed'] = (
                        frontmatter.get('rows_processed', 0) + len(self.operations)
                    )
                    frontmatter['content_hash'] = hashlib.sha256(
                        json.dumps(existing_data, sort_keys=True).encode()
                    ).hexdigest()[:16]
                    
                    # Write updated log
                    with open(log_path, 'w') as f:
                        f.write("---\n")
                        yaml.dump(frontmatter, f, default_flow_style=False)
                        f.write("---\n\n")
                        json.dump(existing_data, f, indent=2, sort_keys=True)
                    
                    self.logger.info(f"Updated shared log: {log_file_path}")
                    
        except (OSError, json.JSONDecodeError, yaml.YAMLError) as e:
            self.logger.error(f"Failed to update shared log: {e}")


def main():
    """Main entry point for vault retention manager"""
    parser = argparse.ArgumentParser(description="Hestia Vault Retention Manager")
    parser.add_argument(
        '--config', 
        default='/config/hestia/config/system/hestia.toml',
        help='Path to hestia.toml configuration file'
    )
    parser.add_argument(
        '--index-file',
        required=True,
        help='Path to file index log from previous components'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be managed without making changes'
    )
    parser.add_argument(
        '--update-log',
        help='Path to shared log file to update with results'
    )
    parser.add_argument(
        '--verify-integrity',
        action='store_true',
        help='Run vault integrity verification'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize vault manager
        manager = VaultRetentionManager(args.config)
        
        # Load file index
        index_data = manager.load_file_index(args.index_file)
        
        # Process vault operations
        manager.process_vault_retention(index_data, dry_run=args.dry_run)
        
        # Generate and display results
        if not args.dry_run:
            report = manager.generate_vault_report()
            print("✅ Vault retention completed:")
            print(f"  Files processed: {report['statistics']['files_processed']}")
            print(f"  Basename groups: {report['statistics']['basename_groups_found']}")
            print(f"  Files retained: {report['statistics']['files_retained']}")
            print(f"  Files removed: {report['statistics']['files_removed']}")
            print(f"  Bytes freed: {report['summary']['bytes_freed_mb']} MB")
            print(f"  Vault health score: {report['summary']['vault_health_score']:.1f}/100")
            
            # Update shared log if specified
            if args.update_log:
                manager.update_shared_log(args.update_log)
                
            # Show integrity report if requested
            if args.verify_integrity:
                integrity = report['integrity_report']
                print("\n🔍 Vault Integrity:")
                print(f"  Location exists: {integrity['vault_location_exists']}")
                print(f"  Permissions correct: {integrity['vault_permissions_correct']}")
                print(f"  Total size: {integrity['total_vault_size_mb']} MB")
                if integrity['orphaned_backups']:
                    print(f"  Orphaned backups: {len(integrity['orphaned_backups'])}")
        else:
            print("🔍 Dry-run completed - no changes made")
            print(f"  Files that would be processed: {manager.stats['files_processed']}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Vault retention manager failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())