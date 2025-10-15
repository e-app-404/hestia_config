#!/usr/bin/env python3
"""
Hestia File Lifecycle Manager
TTL-based cleanup with configurable retention policies

Purpose: Manages file lifecycle with TTL cleanup, atomic operations, and 
configurable error handling based on retention policies.

Usage:
    python sweeper.py [--config=/path/to/hestia.toml] [--dry-run] [--index-file=path]

Compliance: ADR-0018, ADR-0024, ADR-0027
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import toml
import yaml


@dataclass
class CleanupOperation:
    """Represents a file cleanup operation"""
    file_path: str
    operation_type: str
    ttl_days: int
    age_days: int
    size_bytes: int
    destination: str
    status: str
    backup_created: str
    checksum_before: str
    error_message: str
    timestamp: str


class FileLifecycleManager:
    """Configuration-driven file lifecycle management"""
    
    def __init__(self, config_path: str = "/config/hestia/config/system/hestia.toml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.setup_logging()
        
        # Extract configuration sections
        self.retention_config = self.config['retention']
        self.safety_config = self.config['safety']
        self.error_handling = self.config['error_handling']
        self.sweeper_config = self.config['automation']['sweeper']
        self.paths_config = self.config['paths']
        
        # Initialize operation tracking
        self.operations: list[CleanupOperation] = []
        self.stats = {
            'files_processed': 0,
            'files_cleaned': 0,
            'files_moved_to_trash': 0,
            'files_permanently_deleted': 0,
            'bytes_freed': 0,
            'errors_encountered': 0,
            'backup_operations': 0,
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
        self.logger = logging.getLogger('hestia.sweeper.lifecycle')

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

    def get_retention_policy(self, file_path: Path, file_category: str) -> dict:
        """Get applicable retention policy for file"""
        str_path = str(file_path)
        
        # Check each retention category by location
        for _category, policy in self.retention_config.items():
            if 'location' in policy:
                location = policy['location']
                if location == 'same_directory':
                    # In-place backup
                    if file_category in ['legacy_backup', 'canonical_backup']:
                        return policy
                elif str_path.startswith(location):
                    return policy
        
        # Default to in-place backup policy
        return self.retention_config.get('in_place_backups', {
            'ttl_days': 7,
            'auto_prune': True,
            'location': 'same_directory'
        })

    def should_cleanup_file(self, file_record: dict) -> bool:
        """Determine if file should be cleaned up based on TTL"""
        # Only cleanup files that are expired
        action_required = file_record.get('action_required', 'no_action')
        return action_required == 'cleanup_expired'

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
        """Create backup of original file before cleanup"""
        if not self.sweeper_config['backup_before_deletion']:
            return None
        
        try:
            # Generate backup filename
            timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
            backup_name = f"{original_path.name}.cleanup_backup.{timestamp}"
            backup_path = original_path.parent / backup_name
            
            # Create backup
            shutil.copy2(original_path, backup_path)
            
            # Set permissions
            permissions = int(self.safety_config['backup_file_permissions'], 8)
            backup_path.chmod(permissions)
            
            self.stats['backup_operations'] += 1
            self.logger.debug(f"Created cleanup backup: {backup_path}")
            
            return str(backup_path)
            
        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to create backup for {original_path}: {e}")
            return None

    def move_to_trash(self, file_path: Path) -> str | None:
        """Move file to trash directory"""
        try:
            trash_dir = Path(self.paths_config['workspace']['trash'])
            trash_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique trash filename
            timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
            trash_name = f"{timestamp}_{file_path.name}"
            trash_path = trash_dir / trash_name
            
            # Move file atomically
            if self.safety_config['atomic_writes']:
                os.replace(str(file_path), str(trash_path))
            else:
                shutil.move(str(file_path), str(trash_path))
            
            self.logger.debug(f"Moved to trash: {file_path} → {trash_path}")
            return str(trash_path)
            
        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to move {file_path} to trash: {e}")
            return None

    def delete_permanently(self, file_path: Path) -> bool:
        """Permanently delete file"""
        try:
            file_path.unlink()
            self.logger.debug(f"Permanently deleted: {file_path}")
            return True
            
        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to delete {file_path}: {e}")
            return False

    def handle_cleanup_error(self, file_path: Path, error: Exception) -> str:
        """Handle cleanup errors according to configuration"""
        error_category = self._categorize_error(error)
        error_config = self.error_handling['categories'].get(
            error_category, 
            {'mode': 'warn', 'continue': True}
        )
        
        mode = error_config.get('mode', 'warn')
        
        if mode == 'quarantine':
            return self._quarantine_file(file_path, str(error))
        elif mode == 'stop':
            raise error
        elif mode == 'warn':
            self.logger.warning(f"Cleanup warning for {file_path}: {error}")
            return f"warning: {error}"
        else:
            self.logger.error(f"Cleanup error for {file_path}: {error}")
            return f"error: {error}"

    def _categorize_error(self, error: Exception) -> str:
        """Categorize error type for handling"""
        if isinstance(error, FileNotFoundError):
            return 'file_not_found'
        elif isinstance(error, PermissionError):
            return 'permission_denied'
        elif isinstance(error, OSError) and 'No space left on device' in str(error):
            return 'disk_full'
        else:
            return 'unknown_error'

    def _quarantine_file(self, file_path: Path, reason: str) -> str:
        """Move file to quarantine directory"""
        try:
            quarantine_dir = Path(self.paths_config['workspace']['quarantine'])
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate quarantine filename
            timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
            quarantine_name = f"cleanup_error__{timestamp}__{file_path.name}"
            quarantine_path = quarantine_dir / quarantine_name
            
            # Move to quarantine
            shutil.move(str(file_path), str(quarantine_path))
            
            # Set quarantine permissions
            permissions = int(self.config['security']['quarantine_permissions'], 8)
            quarantine_path.chmod(permissions)
            
            self.logger.warning(f"Quarantined file: {file_path} → {quarantine_path}")
            return f"quarantined: {quarantine_path}"
            
        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to quarantine {file_path}: {e}")
            return f"quarantine_failed: {e}"

    def cleanup_file(self, file_record: dict) -> CleanupOperation:
        """Perform cleanup operation on a single file"""
        file_path = Path(file_record['path'])
        timestamp = datetime.now(UTC).isoformat()
        
        # Initialize operation record
        operation = CleanupOperation(
            file_path=str(file_path),
            operation_type="cleanup",
            ttl_days=file_record.get('estimated_age_days', 0),
            age_days=file_record.get('estimated_age_days', 0),
            size_bytes=file_record.get('size_bytes', 0),
            destination="",
            status="pending",
            backup_created="",
            checksum_before=self.calculate_checksum(file_path),
            error_message="",
            timestamp=timestamp
        )
        
        try:
            # Get retention policy
            retention_policy = self.get_retention_policy(
                file_path, 
                file_record.get('category', 'other')
            )
            operation.ttl_days = retention_policy.get('ttl_days', -1)
            
            # Create backup if configured
            backup_path = self.create_backup(file_path)
            if backup_path:
                operation.backup_created = backup_path
            
            # Determine cleanup action
            ttl_days = retention_policy.get('ttl_days', -1)
            
            if ttl_days == -1:
                # No TTL - skip cleanup
                operation.status = "skipped_no_ttl"
                operation.destination = "no_action"
            elif retention_policy.get('location') == self.paths_config['workspace']['trash']:
                # Already in trash - delete permanently
                if self.delete_permanently(file_path):
                    operation.status = "deleted_permanently"
                    operation.destination = "deleted"
                    operation.operation_type = "permanent_delete"
                    self.stats['files_permanently_deleted'] += 1
                    self.stats['bytes_freed'] += operation.size_bytes
                else:
                    operation.status = "delete_failed"
                    operation.error_message = "Failed to delete file"
            else:
                # Move to trash
                trash_path = self.move_to_trash(file_path)
                if trash_path:
                    operation.status = "moved_to_trash"
                    operation.destination = trash_path
                    operation.operation_type = "move_to_trash"
                    self.stats['files_moved_to_trash'] += 1
                else:
                    operation.status = "move_failed"
                    operation.error_message = "Failed to move to trash"
            
            if operation.status.endswith('_failed'):
                self.stats['errors_encountered'] += 1
            else:
                self.stats['files_cleaned'] += 1
            
        except Exception as e:
            error_result = self.handle_cleanup_error(file_path, e)
            operation.status = "error_handled"
            operation.error_message = error_result
            self.stats['errors_encountered'] += 1
        
        self.stats['files_processed'] += 1
        return operation

    def process_file_index(self, index_data: dict, dry_run: bool = False) -> None:
        """Process cleanup operations from index data"""
        start_time = datetime.now(UTC)
        file_registry = index_data.get('file_registry', [])
        
        self.logger.info(f"Processing {len(file_registry)} files for cleanup")
        
        for file_record in file_registry:
            if self.should_cleanup_file(file_record):
                if dry_run:
                    self.logger.info(f"Would cleanup: {file_record['path']}")
                    self.stats['files_processed'] += 1
                else:
                    operation = self.cleanup_file(file_record)
                    self.operations.append(operation)
        
        self.stats['processing_duration_seconds'] = int((
            datetime.now(UTC) - start_time
        ).total_seconds())
        
        duration = self.stats['processing_duration_seconds']
        self.logger.info(f"Cleanup processing completed in {duration}s")

    def generate_cleanup_report(self) -> dict:
        """Generate comprehensive cleanup operation report"""
        timestamp = datetime.now(UTC).isoformat()
        
        report_data = {
            'metadata': {
                'tool': 'hestia.sweeper.lifecycle',
                'script': __file__,
                'created_at': timestamp,
                'batch_id': (
                    f"cleanup_operations_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
                ),
                'rows_processed': len(self.operations),
                'content_hash': self._calculate_content_hash(),
                'config_version': self.config['meta']['version'],
                'compliance_adrs': self.config['meta']['compliance_adrs']
            },
            'configuration': {
                'retention_policies': dict(self.retention_config),
                'safety_settings': dict(self.safety_config),
                'error_handling': dict(self.error_handling),
                'backup_before_deletion': self.sweeper_config['backup_before_deletion']
            },
            'statistics': self.stats,
            'operations': [asdict(op) for op in self.operations],
            'summary': {
                'successful_cleanups': len([
                    op for op in self.operations 
                    if op.status in ['moved_to_trash', 'deleted_permanently']
                ]),
                'failed_operations': len([
                    op for op in self.operations if 'failed' in op.status
                ]),
                'bytes_freed_mb': round(self.stats['bytes_freed'] / 1024 / 1024, 2),
                'error_rate_percent': round(
                    (self.stats['errors_encountered'] / 
                     max(self.stats['files_processed'], 1)) * 100, 
                    2
                )
            }
        }
        
        return report_data

    def _calculate_content_hash(self) -> str:
        """Calculate hash of operations for integrity checking"""
        content = json.dumps([asdict(op) for op in self.operations], sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def update_shared_log(self, log_file_path: str) -> None:
        """Update shared log file with cleanup operation results"""
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
                    
                    # Add cleanup operation results
                    existing_data['cleanup_operations'] = {
                        'statistics': self.stats,
                        'operations_count': len(self.operations),
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
    """Main entry point for file lifecycle manager"""
    parser = argparse.ArgumentParser(description="Hestia File Lifecycle Manager")
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
        help='Show what would be cleaned up without making changes'
    )
    parser.add_argument(
        '--update-log',
        help='Path to shared log file to update with results'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize lifecycle manager
        manager = FileLifecycleManager(args.config)
        
        # Load file index
        index_data = manager.load_file_index(args.index_file)
        
        # Process cleanup operations
        manager.process_file_index(index_data, dry_run=args.dry_run)
        
        # Generate and display results
        if not args.dry_run:
            report = manager.generate_cleanup_report()
            print("✅ File cleanup completed:")
            print(f"  Files processed: {report['statistics']['files_processed']}")
            print(f"  Files cleaned: {report['statistics']['files_cleaned']}")
            print(f"  Moved to trash: {report['statistics']['files_moved_to_trash']}")
            print(f"  Permanently deleted: {report['statistics']['files_permanently_deleted']}")
            print(f"  Bytes freed: {report['summary']['bytes_freed_mb']} MB")
            print(f"  Errors: {report['statistics']['errors_encountered']}")
            
            # Update shared log if specified
            if args.update_log:
                manager.update_shared_log(args.update_log)
        else:
            print("🔍 Dry-run completed - no changes made")
            print(f"  Files that would be processed: {manager.stats['files_processed']}")
        
        return 0
        
    except Exception as e:
        logging.error(f"File lifecycle manager failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())