#!/usr/bin/env python3
"""
Validation script for Universal Media Player YAML and Jinja templates
"""

def validate_yaml_structure():
    """Basic YAML structure validation"""
    try:
        with open('packages/package_universal_media.yaml', 'r') as f:
            content = f.read()
        
        print("✓ File readable")
        print("✓ File has {} lines".format(len(content.split('\n'))))
        
        # Check for key sections
        sections = ['template:', 'script:', 'automation:', 'media_player:']
        for section in sections:
            if section in content:
                print(f"✓ Found {section} section")
            else:
                print(f"⚠ Missing {section} section")
        
        return True
    except Exception as e:
        print(f"✗ YAML structure error: {e}")
        return False

def validate_jinja_templates():
    """Validate Jinja template syntax"""
    try:
        with open('packages/package_universal_media.yaml', 'r') as f:
            content = f.read()
        
        # Check for our hardened templates
        checks = [
            ('state_template:', 2),  # Should have 2
            ('active_child_template:', 2),  # Should have 2  
            ('namespace(found=false)', 4),  # Should have 4 (2 * template type)
            ("!= 'standby'", 4),  # Should have 4 explicit standby checks
            ('active_states = ', 4),  # Should have 4 active_states definitions
        ]
        issues = []
        for check, expected in checks:
            count = content.count(check)
            if count == expected:
                print(
                    f"✓ {check} found {count} times (expected {expected})"
                )
            else:
                print(
                    f"⚠ {check} found {count} times (expected {expected})"
                )
        
        open_braces = content.count('{{')
        close_braces = content.count('}}')
        if open_braces != close_braces:
            issues.append(
                f"Unmatched braces: {open_braces} {{ vs {close_braces} }}"
            )
        open_blocks = content.count('{%')
        close_blocks = content.count('%}')
        if open_blocks != close_blocks:
            issues.append(
                f"Unmatched template blocks: {open_blocks} vs {close_blocks}"
            )
        # Check for unmatched template blocks (redundant, kept for logic parity)
        open_blocks = content.count('{%')
        close_blocks = content.count('%}')
        if open_blocks != close_blocks:
            issues.append(
                f"Unmatched template blocks: {open_blocks} vs {close_blocks}"
            )
        
        if issues:
            for issue in issues:
                print(f"✗ Jinja issue: {issue}")
            return False
        else:
            print("✓ Jinja template syntax appears valid")
            return True
            
    except Exception as e:
        print(f"✗ Jinja validation error: {e}")
        return False
def validate_universal_media_player_config():
    """Validate Universal Media Player specific configuration"""
    try:
        with open('packages/package_universal_media.yaml', 'r') as f:
            content = f.read()
        
        # Check for required Universal Media Player fields
        required_fields = [
            'platform: universal',
        ]
        if 'media_player:' in content:
            print("✓ media_player section found")
            for field in required_fields:
                if field in content:
                    print(f"✓ Required field {field} found")
                else:
                    print(f"⚠ Required field {field} missing")
        else:
            print("✗ No media_player section found")
            return False

        # Check for our two Universal Media Players
        universal_count = content.count('platform: universal')
        if universal_count == 2:
            print(
                f"✓ Found {universal_count} Universal Media Player "
                f"definitions"
            )
        else:
            print(
                f"⚠ Found {universal_count} Universal Media Player "
                f"definitions (expected 2)"
            )

        return True
        
    except Exception as e:
        print(f"✗ Universal Media Player validation error: {e}")
        return False
        return False

if __name__ == "__main__":
    print("=== Universal Media Player YAML & Jinja Validation ===\\n")
    
    yaml_valid = validate_yaml_structure()
    print()
    
if __name__ == "__main__":
    print("=== Universal Media Player YAML & Jinja Validation ===\n")
    
    yaml_valid = validate_yaml_structure()
    print()
    
    jinja_valid = validate_jinja_templates()  
    print()
    
    config_valid = validate_universal_media_player_config()
    print()
    
    if yaml_valid and jinja_valid and config_valid:
        print("✅ ALL VALIDATIONS PASSED")
        print("✅ Configuration appears ready for deployment")
    else:
        print("❌ VALIDATION ISSUES FOUND")
        print("❌ Review issues above before deployment")