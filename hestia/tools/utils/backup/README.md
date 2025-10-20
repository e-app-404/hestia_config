# Hestia Backup Tools

This directory contains backup utilities for the Hestia Home Assistant workspace.

## hestia_tarball.sh

Creates compressed tarball backups of the Home Assistant workspace with intelligent exclusions and optional `.storage` backup capability.

### Features

- **ADR-0024 Compliant**: Uses canonical `/config` path resolution
- **ISO Week Organization**: Archives organized by ISO week (e.g., `2025-W41`)
- **Comprehensive Exclusions**: Excludes logs, databases, caches, and large media
- **Optional Storage Backup**: Opt-in `.storage` directory backup
- **Safe Defaults**: Excludes sensitive data by default

### Basic Usage

```bash
# Standard backup (excludes .storage)
./hestia_tarball.sh

# With storage backup (creates two files)
INCLUDE_STORAGE=true ./hestia_tarball.sh
```

### Output Location

Tarballs are created in:
```
/config/hestia/workspace/archive/tarballs/<ISO_WEEK>/
```

### File Naming Convention

- **Main backup**: `ha_hestia_<ISO_WEEK>_<TIMESTAMP>.tar.gz`
- **Storage backup**: `ha_storage_<ISO_WEEK>_<TIMESTAMP>.tar.gz`

Example:
- `ha_hestia_2025-W41_20251006T143000Z.tar.gz`
- `ha_storage_2025-W41_20251006T143000Z.tar.gz`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFIG_ROOT` | `/config` | Workspace root directory |
| `INCLUDE_STORAGE` | `false` | Create separate .storage backup |

### Exclusion Patterns

The script excludes the following to optimize backup size and security:

#### Runtime Files
- `*.log*` - Log files
- `*.db` - Database files
- `*.tar*` - Existing tarballs
- `.storage/` - Home Assistant storage (unless opted-in)
- `.ha_run.lock` - Runtime lock files

#### Development/Cache
- `.git/`, `.github/`, `.githooks/` - Git repositories
- `.vscode/`, `.venv*/` - Development environments
- `.mypy_cache/` - Python cache
- `*.egg-info/` - Python package info
- `deps/` - Dependencies

#### Media/Large Files
- `**/*.mp4`, `**/*.mkv`, `**/*.avi` - Video files
- `**/*.wav`, `**/*.mp3` - Audio files
- `www/` - Web assets
- `tts/` - Text-to-speech cache

#### Workspace Areas
- `.trash/`, `.quarantine/` - Temporary storage
- `hestia/workspace/archive/` - Existing archives
- `hestia/workspace/cache/` - Cache directory
- `reports/checkpoints/` - Checkpoint reports
- `tmp/`, `staging/` - Temporary directories

#### Security
- `secrets.yaml` - Secrets file
- `.ssh/` - SSH keys
- `influx.cookie` - Credentials
- `.ps4-games.*.json` - Gaming credentials

### Makefile Integration

The script integrates with the workspace Makefile for convenient execution:

```bash
# Standard backup (excludes .storage)
make tarball

# Complete backup (includes .storage in separate file)
make storage-tarball
```

### Advanced Examples

```bash
# Custom config root
CONFIG_ROOT=/custom/path ./hestia_tarball.sh

# Both variables
CONFIG_ROOT=/config INCLUDE_STORAGE=true ./hestia_tarball.sh

# Debug mode (see exact tar command)
bash -x ./hestia_tarball.sh
```

### Storage Backup Details

When `INCLUDE_STORAGE=true`:

1. **Main Backup**: Created first, excludes `.storage/`
2. **Storage Backup**: Created second, contains only `.storage/` directory
3. **Separate Files**: Two independent tarballs for different restore scenarios
4. **Error Handling**: Storage backup failure doesn't affect main backup

### Error Handling

The script provides comprehensive error handling:

- **Directory Creation**: Fails if archive directory cannot be created
- **Working Directory**: Fails if cannot change to workspace directory
- **Tar Operations**: Reports exit codes for debugging
- **Storage Validation**: Warns if `.storage` directory missing

### Integration with Workspace Management

This script integrates with the broader Hestia workspace management system:

- **Archive Structure**: Follows ADR-0016 canonical workspace structure
- **ISO Week Organization**: Aligns with workspace archival policies
- **Path Resolution**: Uses ADR-0024 canonical path patterns
- **Exclusion Policies**: Respects workspace hygiene standards (ADR-0018)

### Restoration Notes

To restore from backups:

```bash
# Extract main backup
cd /config
tar xzf hestia/workspace/archive/tarballs/2025-W41/ha_hestia_2025-W41_20251006T143000Z.tar.gz

# Extract storage backup (if created)
tar xzf hestia/workspace/archive/tarballs/2025-W41/ha_storage_2025-W41_20251006T143000Z.tar.gz
```

### Performance Considerations

- **Size Optimization**: Exclusions reduce backup size by ~80-90%
- **Speed**: Excluding large media and logs significantly improves backup speed
- **Storage Separation**: Optional storage backup allows selective restoration
- **Compression**: Uses gzip compression for space efficiency

### Security Notes

- **Default Exclusions**: Sensitive files excluded by default
- **Opt-in Storage**: `.storage` contains sensitive HA data, requires explicit opt-in
- **Secrets Protection**: `secrets.yaml` and credential files excluded
- **Archive Location**: Tarballs stored within workspace for access control

### Troubleshooting

#### Common Issues

1. **Permission Denied**: Ensure script is executable (`chmod +x hestia_tarball.sh`)
2. **Directory Not Found**: Verify `CONFIG_ROOT` points to valid workspace
3. **Disk Space**: Check available space in archive directory
4. **Large Backups**: Review exclusion patterns if backups are unexpectedly large

#### Debug Commands

```bash
# Check exclusion patterns
grep -A 50 "EXCLUDES=" hestia_tarball.sh

# Verify workspace structure
ls -la $CONFIG_ROOT

# Test without creating files
tar czf /dev/null "${EXCLUDES[@]}" . 2>&1 | head -20
```

### Related Tools

- `hestia/tools/workspace_manager.sh` - Workspace cleanup and organization
- `bin/config-health` - Workspace health validation
- `bin/require-config-root` - Path validation utilities

### Changelog

- **v1.0**: Initial implementation with basic exclusions
- **v1.1**: Added ISO week organization and ADR-0024 compliance
- **v1.2**: Added optional `.storage` backup capability
- **v1.3**: Enhanced exclusion patterns and error handling