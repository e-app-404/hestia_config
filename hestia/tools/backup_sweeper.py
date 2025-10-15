#!/usr/bin/env python3
"""
Hestia Backup Sweeper - Main Orchestrator
Configuration-driven backup cleanup automation with modular components

This is the main entry point that orchestrates all sweeper components:
1. index.py - Workspace scanner and file discovery
2. naming_convention.py - Naming standards enforcement
3. sweeper.py - File lifecycle management with TTL cleanup
4. vault_warden.py - Vault retention management  
5. sweeper_report.py - Comprehensive reporting

Usage:
    python backup_sweeper.py [--config=/path/to/hestia.toml] [--dry-run]

Compliance: ADR-0018, ADR-0024, ADR-0027
"""

import argparse
import logging
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import toml


class BackupSweeperOrchestrator:
    """Main orchestrator for backup sweeper pipeline"""
    
    def __init__(self, config_path: str = "/config/hestia/config/system/hestia.toml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.setup_logging()
        
        # Extract configuration
        self.sweeper_config = self.config['automation']['sweeper']
        self.components_config = self.sweeper_config['components']
        self.base_path = Path(self.components_config['base_path'])
        
        # Component paths
        self.components = {
            'index': self.base_path / self.components_config['index_scanner'],
            'naming': self.base_path / self.components_config['naming_standardizer'],
            'sweeper': self.base_path / self.components_config['file_processor'],
            'vault': self.base_path / self.components_config['vault_manager'],
            'report': self.base_path / self.components_config['report_generator']
        }
        
        # Pipeline state
        self.pipeline_stats = {
            'start_time': None,
            'end_time': None,
            'components_executed': [],
            'components_failed': [],
            'shared_log_path': '',
            'final_report_path': ''
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
        self.logger = logging.getLogger('hestia.sweeper.orchestrator')

    def validate_components(self) -> bool:
        """Validate all component scripts exist and are executable"""
        all_valid = True
        
        for component_name, component_path in self.components.items():
            if not component_path.exists():
                self.logger.error(f"Component missing: {component_name} at {component_path}")
                all_valid = False
            elif not component_path.is_file():
                self.logger.error(f"Component not a file: {component_name} at {component_path}")
                all_valid = False
            else:
                self.logger.debug(f"Component validated: {component_name}")
        
        return all_valid

    def generate_shared_log_path(self) -> str:
        """Generate shared log path for component communication"""
        date_str = datetime.now(UTC).strftime('%Y-%m-%d')
        timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
        
        log_template = self.sweeper_config['log_location']
        log_path = log_template.format(date=date_str, timestamp=timestamp)
        
        # Ensure directory exists
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        
        return log_path

    def run_component(self, component_name: str, component_path: Path, 
                     args: list[str], dry_run: bool = False) -> tuple[bool, str]:
        """Run a single sweeper component"""
        self.logger.info(f"Running component: {component_name}")
        
        # Build command
        cmd = [sys.executable, str(component_path)]
        cmd.extend(args)
        
        if dry_run and '--dry-run' not in args:
            cmd.append('--dry-run')
        
        try:
            # Run component
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False
            )
            
            # Log output
            if result.stdout:
                self.logger.info(f"{component_name} output: {result.stdout.strip()}")
            if result.stderr:
                self.logger.warning(f"{component_name} stderr: {result.stderr.strip()}")
            
            if result.returncode == 0:
                self.pipeline_stats['components_executed'].append(component_name)
                self.logger.info(f"✅ Component {component_name} completed successfully")
                return True, result.stdout
            else:
                self.pipeline_stats['components_failed'].append(component_name)
                error_msg = f"Component {component_name} failed with exit code {result.returncode}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Component {component_name} timed out after 5 minutes"
            self.logger.error(error_msg)
            self.pipeline_stats['components_failed'].append(component_name)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error running component {component_name}: {e}"
            self.logger.error(error_msg)
            self.pipeline_stats['components_failed'].append(component_name)
            return False, error_msg

    def run_pipeline(self, dry_run: bool = False) -> bool:
        """Run the complete backup sweeper pipeline"""
        self.pipeline_stats['start_time'] = datetime.now(UTC)
        self.logger.info("🚀 Starting backup sweeper pipeline")
        
        if dry_run:
            self.logger.info("🔍 Running in DRY-RUN mode - no changes will be made")
        
        # Validate components first
        if not self.validate_components():
            self.logger.error("❌ Component validation failed")
            return False
        
        # Generate shared log path
        shared_log_path = self.generate_shared_log_path()
        self.pipeline_stats['shared_log_path'] = shared_log_path
        
        # Component execution order and arguments
        pipeline_steps = [
            {
                'name': 'index',
                'path': self.components['index'],
                'args': [
                    '--config', str(self.config_path),
                    '--output', shared_log_path
                ]
            },
            {
                'name': 'naming',
                'path': self.components['naming'],
                'args': [
                    '--config', str(self.config_path),
                    '--index-file', shared_log_path,
                    '--update-log', shared_log_path
                ]
            },
            {
                'name': 'sweeper',
                'path': self.components['sweeper'],
                'args': [
                    '--config', str(self.config_path),
                    '--index-file', shared_log_path,
                    '--update-log', shared_log_path
                ]
            },
            {
                'name': 'vault',
                'path': self.components['vault'],
                'args': [
                    '--config', str(self.config_path),
                    '--index-file', shared_log_path,
                    '--update-log', shared_log_path
                ]
            },
            {
                'name': 'report',
                'path': self.components['report'],
                'args': [
                    '--config', str(self.config_path),
                    '--shared-log', shared_log_path,
                    '--update-index'
                ]
            }
        ]
        
        # Execute pipeline steps
        all_successful = True
        
        for step in pipeline_steps:
            success, output = self.run_component(
                step['name'], 
                step['path'], 
                step['args'], 
                dry_run
            )
            
            if not success:
                # Handle error based on configuration
                error_handling = self.config['error_handling']['default_mode']
                
                if error_handling == 'stop':
                    self.logger.error(f"🛑 Pipeline stopped due to {step['name']} failure")
                    all_successful = False
                    break
                elif error_handling == 'continue':
                    self.logger.warning(f"⚠️ Continuing pipeline despite {step['name']} failure")
                    all_successful = False
                else:
                    self.logger.info(f"ℹ️ {step['name']} completed with warnings")
        
        # Pipeline completion
        self.pipeline_stats['end_time'] = datetime.now(UTC)
        duration = (self.pipeline_stats['end_time'] - self.pipeline_stats['start_time']).total_seconds()
        
        if all_successful:
            self.logger.info(f"✅ Backup sweeper pipeline completed successfully in {duration:.2f}s")
        else:
            self.logger.warning(f"⚠️ Backup sweeper pipeline completed with errors in {duration:.2f}s")
        
        # Display summary
        self.display_pipeline_summary()
        
        return all_successful

    def display_pipeline_summary(self) -> None:
        """Display pipeline execution summary"""
        duration = (self.pipeline_stats['end_time'] - self.pipeline_stats['start_time']).total_seconds()
        
        print("\n" + "="*60)
        print("BACKUP SWEEPER PIPELINE SUMMARY")
        print("="*60)
        print(f"Start time: {self.pipeline_stats['start_time'].isoformat()}")
        print(f"End time: {self.pipeline_stats['end_time'].isoformat()}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Components executed: {len(self.pipeline_stats['components_executed'])}")
        print(f"Components failed: {len(self.pipeline_stats['components_failed'])}")
        
        if self.pipeline_stats['components_executed']:
            print(f"\n✅ Successful components:")
            for component in self.pipeline_stats['components_executed']:
                print(f"  - {component}")
        
        if self.pipeline_stats['components_failed']:
            print(f"\n❌ Failed components:")
            for component in self.pipeline_stats['components_failed']:
                print(f"  - {component}")
        
        print(f"\n📄 Shared log: {self.pipeline_stats['shared_log_path']}")
        print("="*60)

    def cleanup_temp_files(self) -> None:
        """Clean up any temporary files created during pipeline execution"""
        # This would clean up any temp files if we created them
        # Currently our pipeline uses persistent logs, so minimal cleanup needed
        pass


def main():
    """Main entry point for backup sweeper orchestrator"""
    parser = argparse.ArgumentParser(
        description="Hestia Backup Sweeper - Configuration-driven backup cleanup automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backup_sweeper.py                    # Run full pipeline
  python backup_sweeper.py --dry-run          # Preview what would be done
  python backup_sweeper.py --config /path    # Use custom config file

Components:
  1. index.py          - Workspace scanner and file discovery
  2. naming_convention.py - Naming standards enforcement  
  3. sweeper.py        - File lifecycle management with TTL cleanup
  4. vault_warden.py   - Vault retention management
  5. sweeper_report.py - Comprehensive reporting

For detailed component options, run each component with --help.
        """
    )
    
    parser.add_argument(
        '--config', 
        default='/config/hestia/config/system/hestia.toml',
        help='Path to hestia.toml configuration file'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Preview operations without making changes'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate components and configuration'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator
        orchestrator = BackupSweeperOrchestrator(args.config)
        
        # Validate-only mode
        if args.validate_only:
            print("🔍 Validating backup sweeper configuration and components...")
            if orchestrator.validate_components():
                print("✅ All components validated successfully")
                return 0
            else:
                print("❌ Component validation failed")
                return 1
        
        # Run pipeline
        success = orchestrator.run_pipeline(dry_run=args.dry_run)
        
        # Cleanup
        orchestrator.cleanup_temp_files()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Pipeline interrupted by user")
        return 130
    except Exception as e:
        logging.error(f"❌ Backup sweeper orchestrator failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())