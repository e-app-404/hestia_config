#!/usr/bin/env bash
# ADR-0016 Path Expansion Validator
# Ensures all Python Path() instances with tilde use .expanduser()

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

echo "🔍 ADR-0016 Path Expansion Compliance Check"
echo "============================================="

# Check Python files for Path() with tilde that don't use .expanduser()
VIOLATIONS=0

echo "Checking Python files for non-expanded tilde paths..."

# Single quotes check
SINGLE_QUOTE_VIOLATIONS=$(find hestia -name "*.py" -exec grep -Hn "Path('~[^']*')" {} \; | grep -v "\.expanduser()" || true)
if [ -n "$SINGLE_QUOTE_VIOLATIONS" ]; then
    echo "❌ VIOLATIONS: Path() with single quotes missing .expanduser():"
    echo "$SINGLE_QUOTE_VIOLATIONS"
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# Double quotes check  
DOUBLE_QUOTE_VIOLATIONS=$(find hestia -name "*.py" -exec grep -Hn 'Path("~[^"]*")' {} \; | grep -v "\.expanduser()" || true)
if [ -n "$DOUBLE_QUOTE_VIOLATIONS" ]; then
    echo "❌ VIOLATIONS: Path() with double quotes missing .expanduser():"
    echo "$DOUBLE_QUOTE_VIOLATIONS"
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# Check for proper usage patterns
echo ""
echo "✅ Checking examples of correct usage..."
CORRECT_USAGE=$(find hestia -name "*.py" -exec grep -Hn "Path('~.*').expanduser()" {} \; || true)
if [ -n "$CORRECT_USAGE" ]; then
    echo "Good examples found:"
    echo "$CORRECT_USAGE" | head -5
else
    echo "ℹ️  No Path().expanduser() patterns found (may be using os.path.expanduser instead)"
fi

# Summary
echo ""
echo "============================================="
if [ $VIOLATIONS -eq 0 ]; then
    echo "✅ PASS: All Python tilde paths properly use .expanduser()"
    exit 0
else
    echo "❌ FAIL: Found $VIOLATIONS violation(s)"
    echo ""
    echo "💡 Fix by adding .expanduser() to Path() calls with tilde:"
    echo "   Path('~/path') → Path('~/path').expanduser()"
    exit 1
fi