"""
Hestia Backup Sweeper System
Configuration-driven workspace lifecycle management for backup files

Components:
- index.py: Workspace scanner and file discovery
- naming_convention.py: Naming standards enforcement  
- sweeper.py: File lifecycle management with TTL cleanup
- vault_warden.py: Vault retention management
- sweeper_report.py: Comprehensive reporting system

Compliance: ADR-0018, ADR-0024, ADR-0027
"""

__version__ = "1.0.0"
__author__ = "hestia-core"
__compliance__ = ["ADR-0018", "ADR-0024", "ADR-0027"]