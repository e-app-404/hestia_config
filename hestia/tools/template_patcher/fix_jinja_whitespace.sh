#!/usr/bin/env bash
# fix_jinja_whitespace.sh
# Dedicated patcher for Jinja macro whitespace control issues (ADR-0020)
# Usage: bash fix_jinja_whitespace.sh [--dry-run] [target_dir]

set -euo pipefail

# Configuration
DRY_RUN=false
TARGET_DIR="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_CONFIG="${ROOT_CONFIG:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# Parse arguments
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=true
    TARGET_DIR="${2:-}"
fi

# Set default target directories
if [ -z "$TARGET_DIR" ]; then
    # Use workspace root directories (go up from hestia/tools/template_patcher to workspace root)
    WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
    TARGET_DIRS=("$WORKSPACE_ROOT/custom_templates" "$WORKSPACE_ROOT/domain" "$WORKSPACE_ROOT/packages")
else
    TARGET_DIRS=("$TARGET_DIR")
fi

echo "[INFO] Jinja Whitespace Control Fixer (ADR-0020)"
echo "[INFO] Mode: $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "APPLY FIXES")"
echo "[INFO] Targets: ${TARGET_DIRS[*]}"

TOTAL_FILES=0
FIXED_FILES=0
ISSUES_FOUND=0

# Function to fix whitespace control in a file
fix_file_whitespace() {
    local file="$1"
    local temp_file="${file}.tmp.$$"
    local changes_made=false
    local file_issues=0
    
    echo "[SCAN] $file"
    
    # Check for macro definitions without whitespace control
    if grep -q "{% macro.*[^-]%}" "$file" 2>/dev/null; then
        echo "  [ISSUE] Macro definitions without whitespace control"
        file_issues=$((file_issues + 1))
        changes_made=true
    fi
    
    # Check for endmacro without whitespace control
    if grep -q "{% endmacro %}" "$file" 2>/dev/null; then
        echo "  [ISSUE] Endmacro tags without whitespace control"
        file_issues=$((file_issues + 1))
        changes_made=true
    fi
    
    ISSUES_FOUND=$((ISSUES_FOUND + file_issues))
    
    if [ "$changes_made" = true ]; then
        if [ "$DRY_RUN" = false ]; then
            # Apply fixes
            sed \
                -e 's/{% macro \([^}]*\) %}/{% macro \1 -%}/g' \
                -e 's/{% endmacro %}/{%- endmacro %}/g' \
                "$file" > "$temp_file"
            
            if [ -s "$temp_file" ]; then
                mv "$temp_file" "$file"
                echo "  [FIXED] Whitespace control applied"
                FIXED_FILES=$((FIXED_FILES + 1))
            else
                rm -f "$temp_file"
                echo "  [ERROR] Fix generated empty file, skipping"
            fi
        else
            echo "  [DRY-RUN] Would fix whitespace control"
        fi
    fi
}

# Process files in target directories
for target_dir in "${TARGET_DIRS[@]}"; do
    if [ ! -d "$target_dir" ]; then
        echo "[WARN] Directory not found: $target_dir"
        continue
    fi
    
    echo "[INFO] Processing directory: $target_dir"
    
    # Find relevant files (Jinja templates and YAML files that might contain templates)
    find "$target_dir" -type f \( -name "*.jinja" -o -name "*.j2" -o -name "*.yaml" -o -name "*.yml" \) \
        -not -path "*/.git/*" \
        -not -path "*/.*" \
        -print0 | while IFS= read -r -d '' file; do
        
        # Only process files that actually contain Jinja macros
        if grep -l "{% macro\|{% endmacro" "$file" >/dev/null 2>&1; then
            fix_file_whitespace "$file"
            TOTAL_FILES=$((TOTAL_FILES + 1))
        fi
    done
done

# Summary
echo ""
echo "[SUMMARY]"
echo "Files processed: $TOTAL_FILES"
echo "Issues found: $ISSUES_FOUND"
if [ "$DRY_RUN" = false ]; then
    echo "Files fixed: $FIXED_FILES"
    if [ $ISSUES_FOUND -gt 0 ] && [ $FIXED_FILES -eq 0 ]; then
        echo "[WARN] Issues were found but no files were fixed. Check file permissions."
    fi
else
    echo "Mode: Dry run (no changes made)"
fi

# Validation
if [ "$DRY_RUN" = false ] && [ $FIXED_FILES -gt 0 ]; then
    echo ""
    echo "[VALIDATION] Checking for remaining issues..."
    remaining_issues=0
    
    for target_dir in "${TARGET_DIRS[@]}"; do
        [ ! -d "$target_dir" ] && continue
        
        if find "$target_dir" -name "*.jinja" -o -name "*.j2" -o -name "*.yaml" -o -name "*.yml" | \
           xargs grep -l "{% macro.*[^-]%}\|{% endmacro %}" 2>/dev/null; then
            remaining_issues=$((remaining_issues + 1))
        fi
    done
    
    if [ $remaining_issues -eq 0 ]; then
        echo "[PASS] All whitespace control issues resolved"
        exit 0
    else
        echo "[FAIL] Some whitespace control issues remain"
        exit 1
    fi
fi

exit 0