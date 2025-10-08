#!/usr/bin/env python3
"""
Prompt preparation tool for the Hestia prompt library consolidation workflow.
Extracts metadata from prompt files and generates content-based slugs and filenames.
Enhanced version with file date detection and improved slug generation.
"""
import argparse
import hashlib
import os
import re
from datetime import datetime
from pathlib import Path

import yaml


class PromptPrepper:
    def __init__(self, source_dir, output_dir, dry_run=False):
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

    def _get_file_date(self, filepath):
        """Get file creation/modification date, prioritizing content date if available"""
        try:
            # Get file modification time
            mtime = filepath.stat().st_mtime
            return datetime.fromtimestamp(mtime)
        except Exception:
            # Fallback to current date
            return datetime.now()

    def _extract_date_from_content(self, content, filepath):
        """Extract date from content, fallback to file date"""
        # Look for date in YAML frontmatter
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    for date_field in ['date', 'created', 'original_date', 'created_at']:
                        if date_field in metadata:
                            date_str = str(metadata[date_field])
                            # Try to parse various date formats
                            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d']:
                                try:
                                    return datetime.strptime(date_str, fmt)
                                except ValueError:
                                    continue
            except Exception:
                pass
        
        # Look for date patterns in content
        date_patterns = [
            r'(?:date|created|updated):\s*(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})',  # ISO date format
            r'(\d{1,2}/\d{1,2}/\d{4})',  # US date format
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
        
        # Fallback to file modification date
        return self._get_file_date(filepath)

    def _generate_id(self, filepath, content_date):
        """Generate deterministic ID using content/file date"""
        # Try to extract existing ID from filename
        id_match = re.search(r'prompt[_-](\d{8}[_-]\w+)', filepath.name)
        if id_match:
            return f"prompt_{id_match.group(1)}"
        
        # Generate ID using content/file date + hash
        hash_suffix = hashlib.md5(str(filepath).encode()).hexdigest()[:6]
        date_prefix = content_date.strftime('%Y%m%d')
        return f"prompt_{date_prefix}_{hash_suffix}"

    def _extract_title_from_content(self, content, filepath):
        """Extract title from content first, fallback to filename"""
        # Try to find first markdown heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Try to find title in YAML frontmatter
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    if 'title' in metadata:
                        return metadata['title'].strip('"\'')
            except Exception:
                pass
        
        # Look for objective or context patterns
        objective_match = re.search(
            r'(?:objective|purpose|goal)[:*]\s*(.+?)(?:\n|$)', 
            content, re.IGNORECASE
        )
        if objective_match:
            title = objective_match.group(1).strip()
            if len(title) < 100:  # Reasonable title length
                return title

        # Look for "You are" patterns common in prompts
        you_are_match = re.search(
            r'^You are (?:an? )?(.+?)(?:\.|$)', content, re.MULTILINE | re.IGNORECASE
        )
        if you_are_match:
            title = you_are_match.group(1).strip()
            if len(title) < 80:
                return f"Assistant: {title.title()}"
        
        # Look for first sentence as title
        first_sentence = re.search(r'^(.+?)\.', content.strip())
        if first_sentence:
            sentence = first_sentence.group(1).strip()
            if 10 < len(sentence) < 100:  # Reasonable length
                return sentence

        # Fallback to cleaned filename
        title = filepath.stem.replace('_', ' ').replace('-', ' ')
        title = re.sub(
            r'^(batch\d+-|prompt_\d+_\d+_)', '', title, flags=re.IGNORECASE
        )
        return title.title()

    def _detect_tier(self, content, filepath):
        """Detect tier from content patterns"""
        content_lower = content.lower()
        
        # Look for explicit tier declarations
        tier_match = re.search(r'tier:\s*([αβγδεζμΩ])', content)
        if tier_match:
            return tier_match.group(1)
        
        # Heuristic detection based on keywords (content-first approach)
        governance_kw = ['governance', 'emergency', 'critical', 'core system', 'meta']
        if any(kw in content_lower for kw in governance_kw):
            return 'α'
        
        operational_kw = ['integration', 'operational', 'workflow', 'extraction', 'automation']
        if any(kw in content_lower for kw in operational_kw):
            return 'β'
        
        instructional_kw = ['instruction', 'guide', 'template', 'documentation', 'tutorial']
        if any(kw in content_lower for kw in instructional_kw):
            return 'γ'
        
        universal_kw = ['universal', 'meta', 'framework']
        if any(kw in content_lower for kw in universal_kw):
            return 'Ω'
        
        # Default to beta if uncertain
        return 'β'

    def _generate_slug_from_content(self, content, filepath):
        """Generate slug from content, promoting it as filename basis"""
        title = self._extract_title_from_content(content, filepath)
        
        # Clean and slugify the title
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'\s+', '-', slug)  # Replace spaces with hyphens
        slug = re.sub(r'-+', '-', slug)  # Collapse multiple hyphens
        slug = slug.strip('-')  # Remove leading/trailing hyphens
        
        # Limit length for practical filenames
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')
        
        # If slug is still empty or too short, use filename
        if len(slug) < 3:
            slug = filepath.stem.lower()
            slug = re.sub(r'[^a-z0-9-]', '-', slug)
            slug = re.sub(r'-+', '-', slug).strip('-')
        
        return slug

    def _detect_domain(self, content, filepath):
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
            return max(scores.keys(), key=lambda k: scores[k])
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
        match = re.search(
            r'author:\s*["\']?([^"\'\n]+)["\']?', content, re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
        
        # Look for authors field (plural)
        match = re.search(
            r'authors?:\s*["\']?([^"\'\n]+)["\']?', content, re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
            
        return 'Unknown'

    def _extract_tags(self, filepath, content):
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
            except Exception:
                pass
        
        # Extract from filename
        filename_lower = filepath.name.lower()
        tag_keywords = [
            'diagnostic', 'validation', 'extraction', 'automation', 
            'governance', 'emergency', 'instructional'
        ]
        tags.extend([kw for kw in tag_keywords if kw in filename_lower])
        
        return list(set(tags))  # Remove duplicates

    def extract_metadata(self, filepath, content):
        """Extract metadata using heuristics"""
        # Extract date from content or use file date
        content_date = self._extract_date_from_content(content, filepath)
        
        # Extract title from content and generate slug from it
        title = self._extract_title_from_content(content, filepath)
        slug = self._generate_slug_from_content(content, filepath)
        
        # Generate deterministic ID using content/file date
        file_id = self._generate_id(filepath, content_date)
        
        # Detect tier from content patterns
        tier = self._detect_tier(content, filepath)
        
        # Detect domain from content patterns
        domain = self._detect_domain(content, filepath)
        
        # Detect persona from content patterns  
        persona = self._detect_persona(content)
        
        # Detect status from content patterns
        status = self._detect_status(content)
        
        # Extract author
        author = self._extract_author(content)
        
        # Extract tags from content and filename
        tags = self._extract_tags(filepath, content)
        
        return {
            'id': file_id,
            'slug': slug,
            'title': title,
            'date': content_date.strftime('%Y-%m-%d'),
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
        frontmatter = yaml.dump(
            metadata, default_flow_style=False, sort_keys=False
        )
        
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
            prepped_content = self._create_prepped_content(
                metadata, content, filepath
            )
            
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prepare prompts with frontmatter'
    )
    parser.add_argument('--source', required=True, help='Source directory')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    prepper = PromptPrepper(args.source, args.output, args.dry_run)
    stats = prepper.process_directory()
    
    print(f"\n📊 Summary: {stats['processed']} processed, {stats['failed']} failed")