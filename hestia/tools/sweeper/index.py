#!/usr/bin/env python3
"""
Hestia Workspace Scanner & File Discovery
Configuration-driven workspace scanning with intelligent file classification

Purpose: Scans workspace for files matching configurable patterns and maintains
rotating log of workspace files requiring action.

Usage:
    python index.py [--config=/path/to/hestia.toml] [--dry-run]

Compliance: ADR-0018, ADR-0024, ADR-0027
"""

import os
import sys
import json
import toml
import argparse
import logging
from pathlib import Path
from datetime import datetime, UTC
from dataclasses import dataclass, asdict
from glob import glob
import re
import hashlib


@dataclass
class FileRecord:
    """Represents a discovered file with metadata"""
    path: str
    basename: str
    size_bytes: int
    modified_time: str
    file_type: str
    category: str
    naming_compliant: bool
    estimated_age_days: int
    action_required: str
    vault_eligible: bool


class WorkspaceIndexer:
    """Configuration-driven workspace scanner"""
    
    def __init__(self, config_path: str = "/config/hestia/config/system/hestia.toml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.setup_logging()
        
        # Extract configuration sections
        self.sweeper_config = self.config['automation']['sweeper']
        self.retention_config = self.config['retention']
        self.backup_config = self.config['backup']
        self.naming_config = self.config['naming']
        
        # File discovery parameters
        self.scope_patterns = self.sweeper_config['scope_patterns']
        self.recursive = self.sweeper_config['workspace_scan_recursive']
        self.log_rotation_count = self.sweeper_config['log_rotation_count']
        
        # Initialize file registry
        self.file_registry: list[FileRecord] = []
        self.stats = {
            'total_files': 0,
            'legacy_backups': 0,
            'canonical_backups': 0,
            'expired_files': 0,
            'vault_candidates': 0,
            'scan_duration_seconds': 0
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
        self.logger = logging.getLogger('hestia.sweeper.index')

    def discover_workspace_files(self) -> None:
        """Scan workspace using configurable scope patterns"""
        start_time = datetime.now(UTC)
        self.logger.info(f"Starting workspace scan with {len(self.scope_patterns)} patterns")
        
        discovered_files: set[str] = set()
        
        for pattern in self.scope_patterns:
            self.logger.debug(f"Scanning pattern: {pattern}")
            
            # Handle recursive patterns with **
            if self.recursive and '**' in pattern:
                matches = glob(pattern, recursive=True)
            else:
                matches = glob(pattern)
            
            for match in matches:
                file_path = Path(match)
                if file_path.is_file() and str(file_path) not in discovered_files:
                    discovered_files.add(str(file_path))
                    self._classify_file(file_path)
        
        self.stats['total_files'] = len(discovered_files)
        self.stats['scan_duration_seconds'] = (datetime.now(UTC) - start_time).total_seconds()
        
        self.logger.info(f"Discovered {self.stats['total_files']} files in {self.stats['scan_duration_seconds']:.2f}s")

    def _classify_file(self, file_path: Path) -> None:
        """Classify a discovered file and add to registry"""
        try:
            stat_info = file_path.stat()
            modified_time = datetime.fromtimestamp(stat_info.st_mtime, UTC)
            age_days = (datetime.now(UTC) - modified_time).days
            
            # Determine file category and compliance
            file_category, file_type = self._categorize_file(file_path)
            naming_compliant = self._check_naming_compliance(file_path)
            action_required = self._determine_action(file_path, age_days, naming_compliant)
            vault_eligible = self._check_vault_eligibility(file_path, file_category)
            
            # Update statistics
            if file_category == 'legacy_backup':
                self.stats['legacy_backups'] += 1
            elif file_category == 'canonical_backup':
                self.stats['canonical_backups'] += 1
            
            if age_days > self._get_ttl_for_file(file_path):
                self.stats['expired_files'] += 1
            
            if vault_eligible:
                self.stats['vault_candidates'] += 1
            
            # Create file record
            record = FileRecord(
                path=str(file_path),
                basename=file_path.name,
                size_bytes=stat_info.st_size,
                modified_time=modified_time.isoformat(),
                file_type=file_type,
                category=file_category,
                naming_compliant=naming_compliant,
                estimated_age_days=age_days,
                action_required=action_required,
                vault_eligible=vault_eligible
            )
            
            self.file_registry.append(record)
            
        except (OSError, PermissionError) as e:
            self.logger.warning(f"Cannot access file {file_path}: {e}")

    def _categorize_file(self, file_path: Path) -> tuple[str, str]:
        """Categorize file by type and naming pattern"""
        name = file_path.name.lower()
        
        # Check legacy backup patterns
        legacy_patterns = self.backup_config['legacy_patterns']['patterns']
        for pattern in legacy_patterns:
            if self._match_pattern(name, pattern):
                return 'legacy_backup', 'backup_file'
        
        # Check canonical backup format
        if re.match(r'.*\.bk\.\d{8}T\d{6}Z$', name):
            return 'canonical_backup', 'backup_file'
        
        # Check other categories
        if any(name.endswith(ext) for ext in ['.yaml', '.yml', '.json', '.toml']):
            return 'config_file', 'configuration'
        
        if any(name.endswith(ext) for ext in ['.md', '.rst', '.txt']):
            return 'documentation', 'document'
        
        if any(name.endswith(ext) for ext in ['.tar.gz', '.tgz', '.zip']):
            return 'archive_blob', 'archive'
        
        return 'other', 'unknown'

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Match filename against glob-like pattern"""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return re.match(f'^{regex_pattern}$', filename) is not None

    def _check_naming_compliance(self, file_path: Path) -> bool:
        """Check if file follows canonical naming convention"""
        name = file_path.name
        
        # Check if it's a backup file
        if not any(self._match_pattern(name.lower(), pattern) 
                  for pattern in self.backup_config['legacy_patterns']['patterns']):
            return True  # Non-backup files are compliant by default
        
        # Check canonical backup format
        canonical_pattern = r'^.*\.bk\.\d{8}T\d{6}Z$'
        return re.match(canonical_pattern, name) is not None

    def _determine_action(self, file_path: Path, age_days: int, naming_compliant: bool) -> str:
        """Determine what action is needed for this file"""
        ttl_days = self._get_ttl_for_file(file_path)
        
        if not naming_compliant:
            return 'rename_to_canonical'
        elif age_days > ttl_days and ttl_days > 0:
            return 'cleanup_expired'
        elif self._check_vault_eligibility(file_path, self._categorize_file(file_path)[0]):
            return 'vault_management'
        else:
            return 'no_action'

    def _get_ttl_for_file(self, file_path: Path) -> int:
        """Get TTL days for file based on its location and type"""
        str_path = str(file_path)
        
        # Check each retention category
        for category, policy in self.retention_config.items():
            if 'location' in policy and policy['location'] in str_path:
                return policy.get('ttl_days', -1)
        
        # Default to in-place backup TTL
        return self.backup_config['retention']['in_place_ttl_days']

    def _check_vault_eligibility(self, file_path: Path, category: str) -> bool:
        """Check if file is eligible for vault management"""
        if category not in ['legacy_backup', 'canonical_backup']:
            return False
        
        # Check if file is in vault location
        vault_path = self.config['paths']['vault']['backups']
        return str(file_path).startswith(vault_path)

    def generate_file_index(self) -> dict:
        """Generate comprehensive file index with metadata"""
        timestamp = datetime.now(UTC).isoformat()
        
        index_data = {
            'metadata': {
                'tool': 'hestia.sweeper.index',
                'script': __file__,
                'created_at': timestamp,
                'batch_id': self._generate_batch_id(),
                'input_path': str(self.config_path),
                'rows_processed': len(self.file_registry),
                'content_hash': self._calculate_content_hash(),
                'config_version': self.config['meta']['version'],
                'compliance_adrs': self.config['meta']['compliance_adrs']
            },
            'configuration': {
                'scope_patterns': self.scope_patterns,
                'recursive_scan': self.recursive,
                'retention_policies': dict(self.retention_config),
                'backup_settings': dict(self.backup_config)
            },
            'statistics': self.stats,
            'file_registry': [asdict(record) for record in self.file_registry],
            'summary': {
                'files_requiring_action': len([
                    r for r in self.file_registry if r.action_required != 'no_action'
                ]),
                'naming_violations': len([
                    r for r in self.file_registry if not r.naming_compliant
                ]),
                'expired_candidates': len([
                    r for r in self.file_registry if r.action_required == 'cleanup_expired'
                ]),
                'vault_management_needed': len([
                    r for r in self.file_registry if r.vault_eligible
                ])
            }
        }
        
        return index_data

    def _generate_batch_id(self) -> str:
        """Generate unique batch ID for this scan"""
        timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
        return f"index_scan_{timestamp}"

    def _calculate_content_hash(self) -> str:
        """Calculate hash of file registry for integrity checking"""
        content = json.dumps([asdict(r) for r in self.file_registry], sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def save_index_log(self, output_path: str | None = None) -> str:
        """Save file index to structured log file"""
        if not output_path:
            # Use configured log location with date substitution
            date_str = datetime.now(UTC).strftime('%Y-%m-%d')
            timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
            
            log_template = self.sweeper_config['log_location']
            output_path = log_template.format(date=date_str, timestamp=timestamp)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate index data
        index_data = self.generate_file_index()
        
        # Write with frontmatter format
        with open(output_file, 'w') as f:
            f.write("---\n")
            # Write metadata as YAML frontmatter
            import yaml
            yaml.dump(index_data['metadata'], f, default_flow_style=False)
            f.write("---\n\n")
            
            # Write full data as JSON
            json.dump(index_data, f, indent=2, sort_keys=True)
        
        self.logger.info(f"File index saved to: {output_path}")
        
        # Manage log rotation
        self._rotate_logs(output_file.parent)
        
        return str(output_file)

    def _rotate_logs(self, log_dir: Path) -> None:
        """Rotate logs to maintain configured count"""
        if not log_dir.exists():
            return
        
        # Find all sweeper log files
        log_pattern = "sweeper_*__cleanup.log"
        log_files = list(log_dir.glob(log_pattern))
        
        if len(log_files) <= self.log_rotation_count:
            return
        
        # Sort by modification time (oldest first)
        log_files.sort(key=lambda f: f.stat().st_mtime)
        
        # Remove oldest files
        files_to_remove = log_files[:-self.log_rotation_count]
        for log_file in files_to_remove:
            try:
                log_file.unlink()
                self.logger.debug(f"Rotated old log: {log_file}")
            except OSError as e:
                self.logger.warning(f"Could not rotate log {log_file}: {e}")


def main():
    """Main entry point for workspace indexer"""
    parser = argparse.ArgumentParser(description="Hestia Workspace File Indexer")
    parser.add_argument(
        '--config', 
        default='/config/hestia/config/system/hestia.toml',
        help='Path to hestia.toml configuration file'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Perform scan without creating log files'
    )
    parser.add_argument(
        '--output',
        help='Custom output path for index log'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize indexer
        indexer = WorkspaceIndexer(args.config)
        
        # Perform workspace scan
        indexer.discover_workspace_files()
        
        # Generate and save results
        if not args.dry_run:
            log_path = indexer.save_index_log(args.output)
            print(f"✅ Index completed: {log_path}")
        else:
            index_data = indexer.generate_file_index()
            print("🔍 Dry-run results:")
            print(f"  Total files: {index_data['statistics']['total_files']}")
            print(f"  Legacy backups: {index_data['statistics']['legacy_backups']}")
            print(f"  Canonical backups: {index_data['statistics']['canonical_backups']}")
            print(f"  Files requiring action: {index_data['summary']['files_requiring_action']}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Indexer failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())