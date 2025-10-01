# Zone Configuration Security

## 🔒 **Security Status**

The zone configuration files in this directory contain sensitive geographical information including:
- **Home coordinates** (exact latitude/longitude)
- **Work locations** 
- **Frequently visited places**
- **Personal location patterns**

## 📁 **File Structure**

```
domain/zones/
├── key_zones.yaml.template    ✅ Safe template (tracked in git)
├── key_zones.yaml             🔒 SECRET (ignored by git)
└── README.md                  📝 This documentation
```

## 🛡️ **Protection Measures**

### **Git Ignore Rules**
The following patterns are automatically ignored by git:
- `domain/zones/key_zones.yaml` - Your actual coordinates
- `domain/zones/*_zones.yaml` - Any other zone files
- `!domain/zones/*.yaml.template` - Template files are allowed

### **Template System**
1. **Template file**: `key_zones.yaml.template` - Safe placeholder version
2. **Live file**: `key_zones.yaml` - Contains your real coordinates (secret)

## 🔧 **Setup Instructions**

### **Initial Setup**
```bash
# Copy template to create your zone file
cp domain/zones/key_zones.yaml.template domain/zones/key_zones.yaml

# Edit with your actual coordinates
# Replace all __REPLACE_WITH_*__ placeholders
```

### **Verification**
```bash
# Verify the secret file is ignored
git status domain/zones/key_zones.yaml
# Should show: (no output = file is ignored)

# Verify template is tracked
git status domain/zones/key_zones.yaml.template
# Should show the file if modified
```

## ⚠️ **Security Notes**

- **Never commit** the actual `key_zones.yaml` file
- **Always use placeholders** in template files
- **Review commits** to ensure no coordinates leak into git history
- **Backup your zones** separately from the git repository

## 🧹 **If Coordinates Were Accidentally Committed**

If coordinates were previously committed to git history:

```bash
# Remove from git history (DESTRUCTIVE - use carefully)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch domain/zones/key_zones.yaml' \
  --prune-empty --tag-name-filter cat -- --all

# Force push to update remote (if applicable)
git push --force --all
```

---
**Last Updated:** 2025-09-30  
**Security Level:** 🔒 **SECRET** - Contains personal location data