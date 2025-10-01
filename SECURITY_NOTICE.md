# Security Notice - API Key Exposure Resolution

## Issue Summary

On October 1, 2025, an automated security scan identified exposed Cloudflare API credentials in the repository.

**Affected Files:**
- `hestia/workspace/operations/deploy/dsm/scripts/hardened_worker_check.sh`
- `hestia/workspace/operations/deploy/dsm/scripts/hardened_worker_retry2.sh`
- `hestia/workspace/operations/deploy/dsm/scripts/add_root_route_and_check.sh`

**Exposed Credentials:**
- Cloudflare API Token (redacted: `x2************************************bz`)
- Cloudflare Account ID: `e37605142353eb163ea86636c4027134`
- Cloudflare Zone ID: `0855d7797c8126d39b6653952f1fed61`

## Immediate Actions Taken

### 1. Credentials Replaced with Placeholders ✅

All hardcoded credentials have been replaced with `__REPLACE_ME__` placeholders in the affected scripts:

```bash
CF_ACCOUNT_ID="__REPLACE_ME__"
CF_ZONE_ID="__REPLACE_ME__"
CF_API_TOKEN="__REPLACE_ME__"
```

### 2. Git Ignore Rules Added ✅

Added pattern to `.gitignore` to prevent future commits of these credential-containing scripts:

```gitignore
# Deployment scripts containing API keys and credentials (use templates with __REPLACE_ME__)
hestia/workspace/operations/deploy/dsm/scripts/*.sh
```

### 3. Files Removed from Git Tracking ✅

The three affected files have been removed from git tracking (but preserved on disk with placeholders):

```bash
git rm --cached hestia/workspace/operations/deploy/dsm/scripts/hardened_worker_check.sh
git rm --cached hestia/workspace/operations/deploy/dsm/scripts/hardened_worker_retry2.sh
git rm --cached hestia/workspace/operations/deploy/dsm/scripts/add_root_route_and_check.sh
```

### 4. Documentation Created ✅

Created comprehensive README at `hestia/workspace/operations/deploy/dsm/scripts/README.md` documenting:
- Security requirements
- Setup instructions
- Credential management best practices
- What to do if credentials are exposed

## Required Actions by Repository Owner

### ⚠️ CRITICAL: Rotate Exposed Credentials

The exposed Cloudflare API token **MUST** be rotated immediately:

1. **Log into Cloudflare Dashboard**
2. **Navigate to:** My Profile → API Tokens
3. **Locate the token** that matches the exposed token (check permissions and creation date)
4. **Delete/Revoke** the exposed token
5. **Create a new token** with the same permissions:
   - Account: Workers Scripts Edit
   - Zone: Workers Routes Edit
   - Minimum required permissions only
6. **Update local scripts** with the new token (in files ignored by git)

### 🔍 Verify No Other Exposures

```bash
# Check for any other potential credential leaks
git log --all --full-history -p | grep -i "token\|key\|password\|secret" | less

# Check current working files
grep -r "CF_API_TOKEN\|CF_ACCOUNT_ID\|CF_ZONE_ID" --include="*.sh" --include="*.yaml"
```

### 📋 Update Configuration

After rotating credentials, update your local working copies:

```bash
cd hestia/workspace/operations/deploy/dsm/scripts/

# Edit each script and replace placeholders with new credentials
# These files are now ignored by git
nano hardened_worker_check.sh
nano hardened_worker_retry2.sh
nano add_root_route_and_check.sh
```

## Git History Cleanup (Optional but Recommended)

The exposed credentials are still in git history. To completely remove them:

### Option 1: Using git-filter-repo (Recommended)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Create backup
git clone . ../hestia_config_backup

# Filter out the sensitive content
git-filter-repo --path hestia/workspace/operations/deploy/dsm/scripts/ --invert-paths

# Force push (WARNING: Rewrites history, coordinate with team)
git push --force --all
```

### Option 2: Using BFG Repo-Cleaner

```bash
# Download BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# Create backup
git clone --mirror . ../hestia_config.git

# Remove sensitive data
java -jar bfg.jar --delete-files '*.sh' --no-blob-protection

# Clean up and push
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

⚠️ **Warning:** History rewriting is **DESTRUCTIVE** and will affect all users. Coordinate with all repository collaborators before proceeding.

## Prevention Measures Now in Place

1. ✅ **Gitignore rules** prevent committing credential-containing scripts
2. ✅ **Template system** with `__REPLACE_ME__` placeholders
3. ✅ **Documentation** for proper credential management
4. ✅ **File tracking removed** for sensitive deployment scripts

## Recommended Long-term Improvements

### 1. Environment Variables

Replace hardcoded credentials with environment variables:

```bash
#!/usr/bin/env bash
CF_ACCOUNT_ID="${CF_ACCOUNT_ID:?CF_ACCOUNT_ID must be set}"
CF_ZONE_ID="${CF_ZONE_ID:?CF_ZONE_ID must be set}"
CF_API_TOKEN="${CF_API_TOKEN:?CF_API_TOKEN must be set}"
```

### 2. Secrets Management

Use a proper secrets manager:
- HashiCorp Vault (already referenced in repo structure)
- 1Password CLI
- AWS Secrets Manager
- Azure Key Vault
- Environment-based configuration

### 3. CI/CD Integration

- Store secrets in GitHub Secrets (for Actions)
- Use workflow environment variables
- Never log or echo credential values

### 4. Pre-commit Hooks

Add pre-commit hooks to scan for credentials:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
```

## Contact Information

For questions or assistance with this security issue:
- Create an issue in this repository
- Tag: @e-app-404
- Security Level: 🔒 CRITICAL

---

**Last Updated:** 2025-10-01  
**Issue Reported By:** Automated security scanner (@sxyrxyy)  
**Resolution Status:** ✅ Immediate threat mitigated, credential rotation required
