#!/usr/bin/env python3
"""
Validate YAML frontmatter completeness and consistency
"""

import yaml
import sys
from pathlib import Path
import json

class FrontmatterValidator:
    REQUIRED_FIELDS = [
        'id', 'slug', 'title', 'date', 'tier', 'domain', 
        'persona', 'status', 'tags', 'version', 'source_path', 
        'author', 'related', 'last_updated', 'redaction_log'
    ]
    
    VALID_TIERS = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'μ', 'Ω']
    
    VALID_DOMAINS = [
        'governance', 'extraction', 'operational', 'validation',
        'diagnostic', 'instructional', 'emergency'
    ]
    
    VALID_STATUSES = [
        'draft', 'proposed', 'candidate', 'approved', 'active',
        'deprecated', 'superseded', 'rejected', 'withdrawn'
    ]
    
    def validate_file(self, md_file):
        """Validate a single markdown file"""
        try:
            content = md_file.read_text()
            
            if not content.startswith('---'):
                return {
                    'valid': False,
                    'issues': ['Missing frontmatter delimiter']
                }
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {
                    'valid': False,
                    'issues': ['Malformed frontmatter']
                }
            
            metadata = yaml.safe_load(parts[1])
            issues = []
            
            # Check required fields
            for field in self.REQUIRED_FIELDS:
                if field not in metadata:
                    issues.append(f"Missing required field: {field}")
            
            # Validate tier
            if 'tier' in metadata and metadata['tier'] not in self.VALID_TIERS:
                issues.append(f"Invalid tier: {metadata['tier']}")
            
            # Validate domain
            if 'domain' in metadata and metadata['domain'] not in self.VALID_DOMAINS:
                issues.append(f"Invalid domain: {metadata['domain']}")
            
            # Validate status
            if 'status' in metadata and metadata['status'] not in self.VALID_STATUSES:
                issues.append(f"Invalid status: {metadata['status']}")
            
            # Validate ID format
            if 'id' in metadata:
                import re
                if not re.match(r'^prompt_\d{8}_[\w]+$', metadata['id']):
                    issues.append(f"Invalid ID format: {metadata['id']}")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"Validation error: {str(e)}"]
            }
    
    def validate_directory(self, prep_dir):
        """Validate all prepped files in directory"""
        results = {
            'valid': [],
            'invalid': [],
            'statistics': {
                'total': 0,
                'valid_count': 0,
                'invalid_count': 0,
                'tier_distribution': {},
                'domain_distribution': {},
                'persona_distribution': {}
            }
        }
        
        for md_file in Path(prep_dir).glob('*.md'):
            results['statistics']['total'] += 1
            validation = self.validate_file(md_file)
            
            if validation['valid']:
                results['valid'].append(str(md_file))
                results['statistics']['valid_count'] += 1
                
                # Collect statistics
                metadata = validation.get('metadata', {})
                tier = metadata.get('tier', 'unknown')
                domain = metadata.get('domain', 'unknown')
                persona = metadata.get('persona', 'unknown')
                
                results['statistics']['tier_distribution'][tier] = \
                    results['statistics']['tier_distribution'].get(tier, 0) + 1
                results['statistics']['domain_distribution'][domain] = \
                    results['statistics']['domain_distribution'].get(domain, 0) + 1
                results['statistics']['persona_distribution'][persona] = \
                    results['statistics']['persona_distribution'].get(persona, 0) + 1
            else:
                results['invalid'].append({
                    'file': str(md_file),
                    'issues': validation['issues']
                })
                results['statistics']['invalid_count'] += 1
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate prompt frontmatter')
    parser.add_argument('--prep-dir', required=True, help='Directory with prepped prompts')
    parser.add_argument('--report-path', help='Path for JSON report output')
    
    args = parser.parse_args()
    
    validator = FrontmatterValidator()
    results = validator.validate_directory(args.prep_dir)
    
    # Print summary
    print(f"\n📊 Validation Summary:")
    print(f"   Total files: {results['statistics']['total']}")
    print(f"   ✅ Valid: {results['statistics']['valid_count']}")
    print(f"   ❌ Invalid: {results['statistics']['invalid_count']}")
    
    if results['statistics']['tier_distribution']:
        print(f"\n   Tier Distribution:")
        for tier, count in sorted(results['statistics']['tier_distribution'].items()):
            print(f"      {tier}: {count}")
    
    if results['statistics']['domain_distribution']:
        print(f"\n   Domain Distribution:")
        for domain, count in sorted(results['statistics']['domain_distribution'].items()):
            print(f"      {domain}: {count}")
    
    # Print invalid files
    if results['invalid']:
        print(f"\n❌ Invalid Files:")
        for item in results['invalid']:
            print(f"   {Path(item['file']).name}:")
            for issue in item['issues']:
                print(f"      - {issue}")
    
    # Write JSON report if requested
    if args.report_path:
        report_path = Path(args.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Report written to: {report_path}")
    
    sys.exit(0 if results['statistics']['invalid_count'] == 0 else 1)

if __name__ == "__main__":
    main()
