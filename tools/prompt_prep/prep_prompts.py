#!/usr/bin/env python3
"""
Prompt Library Pre-Preparation Script
Converts all prompt files to Markdown with YAML frontmatter stub
"""

import hashlib
import os
import re
from datetime import datetime
from pathlib import Path

import yaml


class PromptPrepper:
    def __init__(self, source_dir, output_dir, dry_run=True):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.processed_files = []
        
    def _generate_slug(self, title):
        """Generate URL-safe slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _generate_id(self, filepath):
        """Generate deterministic ID from file path"""
        # Try to extract existing ID from filename
        match = re.search(r'prompt_(\d{8}_\d{3})', filepath.name)
        if match:
            return f"prompt_{match.group(1)}"
        
        # Generate fallback ID using hash
        hash_suffix = hashlib.md5(str(filepath).encode()).hexdigest()[:6]
        date_prefix = datetime.now().strftime('%Y%m%d')
        return f"prompt_{date_prefix}_{hash_suffix}"
    
    def _extract_title(self, filename, content):
        """Extract title from filename or first heading"""
        # Try to find first markdown heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Fallback to cleaned filename
        title = filename.stem.replace('_', ' ').replace('-', ' ')
        title = re.sub(r'^(batch\d+-|prompt_\d+_\d+_)', '', title, flags=re.IGNORECASE)
        return title.title()
    
    def _detect_tier(self, content, filename):
        """Detect tier from content patterns"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Look for explicit tier declarations
        tier_match = re.search(r'tier:\s*([αβγδεζημΩ])', content)
        if tier_match:
            return tier_match.group(1)
        
        # Heuristic detection based on keywords
        if any(kw in content_lower for kw in ['governance', 'emergency', 'critical', 'core system']):
            return 'α'
        elif any(kw in content_lower for kw in ['integration', 'operational', 'workflow', 'extraction']):
            return 'β'
        elif any(kw in content_lower for kw in ['instruction', 'guide', 'template', 'documentation']):
            return 'γ'
        
        # Default to beta if uncertain
        return 'β'
    
    def _detect_domain(self, content, filename):
        """Detect domain from content patterns"""
        content_lower = content.lower()
        
        # Domain keyword mapping
        domain_keywords = {
            'governance': ['governance', 'policy', 'adr', 'architecture decision'],
            'extraction': ['extract', 'parse', 'mining', 'data extraction'],
            'operational': ['operational', 'workflow', 'pipeline', 'automation'],
            'validation': ['validation', 'verify', 'check', 'quality assurance'],
            'diagnostic': ['diagnostic', 'debug', 'troubleshoot', 'analyze'],
            'instructional': ['instruction', 'guide', 'tutorial', 'how-to'],
            'emergency': ['emergency', 'critical', 'urgent', 'immediate']
        }
        
        # Score each domain
        scores = {}
        for domain, keywords in domain_keywords.items():
            scores[domain] = sum(1 for kw in keywords if kw in content_lower)
        
        # Return domain with highest score, or 'operational' as default
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'operational'
    
    def _detect_persona(self, content):
        """Detect persona from content patterns"""
        content_lower = content.lower()
        
        personas = {
            'promachos': ['promachos', 'governance', 'meta'],
            'strategos': ['strategos', 'strategy', 'planning'],
            'kybernetes': ['kybernetes', 'pilot', 'navigation'],
            'icaria': ['icaria', 'repair', 'fix'],
            'nomia': ['nomia', 'validation', 'rules'],
            'heurion': ['heurion', 'discovery', 'analysis']
        }
        
        for persona, keywords in personas.items():
            if any(kw in content_lower for kw in keywords):
                return persona
        
        return 'generic'
    
    def _detect_status(self, content):
        """Detect status from content patterns"""
        content_lower = content.lower()
        
        if 'deprecated' in content_lower:
            return 'deprecated'
        elif 'approved' in content_lower or 'active' in content_lower:
            return 'approved'
        elif 'draft' in content_lower or 'proposed' in content_lower:
            return 'candidate'
        
        return 'candidate'
    
    def _extract_author(self, content):
        """Extract author from content"""
        match = re.search(r'author:\s*["\']?([^"\'\n]+)["\']?', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return 'Unknown'
    
    def _extract_tags(self, filename, content):
        """Extract tags from content and filename"""
        tags = []
        
        # Extract from YAML frontmatter if exists
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    if 'tags' in metadata:
                        tags.extend(metadata['tags'])
            except:
                pass
        
        # Extract from filename
        filename_lower = filename.lower()
        tag_keywords = ['diagnostic', 'validation', 'extraction', 'automation', 
                       'governance', 'emergency', 'instructional']
        tags.extend([kw for kw in tag_keywords if kw in filename_lower])
        
        return list(set(tags))  # Remove duplicates
    
    def extract_metadata(self, filepath, content):
        """Extract metadata using heuristics"""
        filename = filepath.name
        
        # Extract title from filename or first heading
        title = self._extract_title(filename, content)
        
        # Generate deterministic ID
        file_id = self._generate_id(filepath)
        
        # Generate slug from title
        slug = self._generate_slug(title)
        
        # Detect tier from content patterns
        tier = self._detect_tier(content, filename)
        
        # Detect domain from content patterns
        domain = self._detect_domain(content, filename)
        
        # Detect persona from content patterns  
        persona = self._detect_persona(content)
        
        # Detect status from content patterns
        status = self._detect_status(content)
        
        # Extract author
        author = self._extract_author(content)
        
        # Extract tags from content and filename
        tags = self._extract_tags(filename, content)
        
        return {
            'id': file_id,
            'slug': slug,
            'title': title,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'tier': tier,
            'domain': domain,
            'persona': persona,
            'status': status,
            'tags': tags,
            'version': '1.0',
            'source_path': str(filepath.relative_to(self.source_dir)),
            'author': author,
            'related': [],
            'last_updated': datetime.now().isoformat(),
            'redaction_log': []
        }
    
    def _create_prepped_content(self, metadata, original_content, filepath):
        """Create prepped markdown with frontmatter"""
        # Remove existing frontmatter if present
        content = original_content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Create new frontmatter
        frontmatter = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        
        return f"---\n{frontmatter}---\n\n{content}\n"
    
    def process_file(self, filepath):
        """Process a single file"""
        try:
            with open(filepath, encoding='utf-8') as f:
                content = f.read()
            
            metadata = self.extract_metadata(filepath, content)
            
            # Create output filename (always .md)
            output_name = f"{metadata['id']}_{metadata['slug']}.md"
            output_path = self.output_dir / output_name
            
            # Generate prepped content
            prepped_content = self._create_prepped_content(metadata, content, filepath)
            
            if self.dry_run:
                print(f"[DRY RUN] Would create: {output_name}")
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(prepped_content)
                # Make read-only
                os.chmod(output_path, 0o444)
                print(f"✅ Created: {output_name}")
            
            self.processed_files.append({
                'source': str(filepath),
                'output': str(output_path),
                'metadata': metadata
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            return False
    
    def process_directory(self):
        """Process all files in source directory"""
        stats = {'processed': 0, 'failed': 0}
        
        for filepath in self.source_dir.rglob('*'):
            if filepath.is_file():
                if self.process_file(filepath):
                    stats['processed'] += 1
                else:
                    stats['failed'] += 1
        
        return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare prompts with frontmatter')
    parser.add_argument('--source', required=True, help='Source directory')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    prepper = PromptPrepper(args.source, args.output, args.dry_run)
    stats = prepper.process_directory()
    
    print(f"\n📊 Summary: {stats['processed']} processed, {stats['failed']} failed")
    
    if not args.dry_run:
        print(f"✅ Output written to: {args.output}")
        print("⚠️  Files are read-only until sign-off")

if __name__ == "__main__":
    main()
