# DSM Deployment Scripts - Security Notice

## 🔒 **Security Status**

The scripts in this directory contain **API keys and credentials** that must be configured before use.

## 📁 **Files**

```
hestia/workspace/operations/deploy/dsm/scripts/
├── hardened_worker_check.sh       🔒 Contains Cloudflare API credentials
├── hardened_worker_retry2.sh      🔒 Contains Cloudflare API credentials  
├── add_root_route_and_check.sh    🔒 Contains Cloudflare API credentials
├── install_portal_include_synology.sh  ✅ No credentials
└── README.md                      📝 This documentation
```

## 🛡️ **Protection Measures**

### **Git Ignore Rules**

These script files are **automatically ignored** by git to prevent accidental credential commits:
- `hestia/workspace/operations/deploy/dsm/scripts/*.sh`

The scripts use placeholder values that **must be replaced** before use:
- `CF_ACCOUNT_ID="__REPLACE_ME__"`
- `CF_ZONE_ID="__REPLACE_ME__"`
- `CF_API_TOKEN="__REPLACE_ME__"`

## 🔧 **Setup Instructions**

### **Initial Setup**

1. Copy the template values to your local working copy
2. Replace all `__REPLACE_ME__` placeholders with actual credentials:
   - `CF_ACCOUNT_ID` - Your Cloudflare account ID
   - `CF_ZONE_ID` - Your Cloudflare zone ID
   - `CF_API_TOKEN` - Your Cloudflare API token with Workers permissions

### **Example Configuration**

```bash
# Edit the script file (NOT tracked by git)
# Replace these lines:
CF_ACCOUNT_ID="__REPLACE_ME__"
CF_ZONE_ID="__REPLACE_ME__"
CF_API_TOKEN="__REPLACE_ME__"

# With your actual credentials:
CF_ACCOUNT_ID="your-account-id-here"
CF_ZONE_ID="your-zone-id-here"
CF_API_TOKEN="your-api-token-here"
```

### **Verification**

```bash
# Verify the scripts are ignored by git
git status hestia/workspace/operations/deploy/dsm/scripts/*.sh
# Should show: (no output = files are ignored)

# Verify placeholders are present in tracked files
git diff hestia/workspace/operations/deploy/dsm/scripts/
# Should show: (no output if files aren't tracked)
```

## ⚠️ **Security Notes**

- **Never commit** real API credentials to git
- **Always use placeholders** (`__REPLACE_ME__`) in any shared versions
- **Review commits** carefully to ensure no credentials leak into git history
- **Rotate API tokens** immediately if they are accidentally exposed

## 🔑 **Credential Management**

For production use, consider:
- Using environment variables instead of hardcoded values
- Storing credentials in a secrets manager (e.g., HashiCorp Vault)
- Using Cloudflare API tokens with minimal required permissions
- Rotating API tokens regularly

## 🧹 **If Credentials Were Accidentally Committed**

If credentials were committed to git history:

1. **Immediately rotate** the exposed API token in Cloudflare
2. Contact repository administrator to rewrite git history if needed
3. Verify the new token works before deleting the old one

---

**Last Updated:** 2025-10-01  
**Security Level:** 🔒 **SECRET** - Contains API credentials and access tokens
