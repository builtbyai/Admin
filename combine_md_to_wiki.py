import os
import re
import json
import time
import requests
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class MarkdownWikiBuilder:
    def __init__(self):
        self.api_key = None
        self.selected_files = []
        self.output_dir = Path("wiki_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # OpenRouter API endpoint
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Model to use (you can change this)
        self.model = "anthropic/claude-3-haiku"  # Fast and cost-effective
        
        # Target word count
        self.target_words = 20000
        
    def get_api_key(self):
        """Get API key from user or file"""
        api_key_file = Path("openrouter_api_key.txt")
        
        if api_key_file.exists():
            with open(api_key_file, 'r') as f:
                self.api_key = f.read().strip()
        else:
            # Create a simple dialog to get API key
            root = tk.Tk()
            root.withdraw()
            
            from tkinter import simpledialog
            api_key = simpledialog.askstring(
                "API Key Required",
                "Enter your OpenRouter API key:\n(Get one at https://openrouter.ai/)",
                show='*'
            )
            
            if api_key:
                self.api_key = api_key
                # Save for future use
                with open(api_key_file, 'w') as f:
                    f.write(api_key)
            else:
                raise ValueError("API key is required")
    
    def select_files(self):
        """Open file dialog to select markdown files"""
        root = tk.Tk()
        root.withdraw()
        
        files = filedialog.askopenfilenames(
            title="Select Markdown Files",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        self.selected_files = list(files)
        return self.selected_files
    
    def read_markdown_files(self):
        """Read content from selected markdown files"""
        contents = []
        
        for file_path in self.selected_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    filename = Path(file_path).name
                    contents.append({
                        'filename': filename,
                        'content': content,
                        'path': file_path
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
        
        return contents
    
    def extract_topics(self, contents):
        """Extract main topics and structure from markdown contents"""
        all_text = "\n\n".join([f"File: {c['filename']}\n{c['content']}" for c in contents])
        
        # Truncate if too long for initial analysis
        max_chars = 10000
        if len(all_text) > max_chars:
            all_text = all_text[:max_chars] + "..."
        
        prompt = f"""Analyze these markdown files and create a comprehensive table of contents structure for a knowledge base wiki.

The wiki should:
1. Combine all information into a cohesive structure
2. Organize topics logically
3. Identify main themes and subtopics
4. Plan for approximately 20,000 words total

Content to analyze:
{all_text}

Provide a detailed table of contents with:
- Main chapters (at least 5-8)
- Subsections for each chapter
- Estimated word count for each section
- Key topics to cover in each section

Format as a structured outline with clear hierarchy."""

        response = self.call_llm(prompt, max_tokens=2000)
        return response
    
    def call_llm(self, prompt, max_tokens=1000):
        """Call OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/wiki-builder",
            "X-Title": "Wiki Builder"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"API Error: {str(e)}")
            return None
    
    def generate_section(self, section_title, section_outline, contents, word_target):
        """Generate content for a specific section"""
        # Gather relevant content for this section
        relevant_content = self.find_relevant_content(section_title, section_outline, contents)
        
        prompt = f"""Create a comprehensive wiki section for: {section_title}

Section outline:
{section_outline}

Target length: approximately {word_target} words

Use this source content:
{relevant_content}

Requirements:
1. Write in an encyclopedic, informative style
2. Include detailed explanations and examples
3. Use proper markdown formatting
4. Add internal links using [[Topic Name]] format for cross-references
5. Include code examples where relevant
6. Make it comprehensive and educational

Generate the complete section content:"""

        response = self.call_llm(prompt, max_tokens=4000)
        return response
    
    def find_relevant_content(self, section_title, section_outline, contents):
        """Find relevant content from source files for a section"""
        relevant_parts = []
        keywords = self.extract_keywords(section_title + " " + section_outline)
        
        for content in contents:
            text = content['content'].lower()
            relevance_score = sum(1 for keyword in keywords if keyword in text)
            
            if relevance_score > 0:
                # Extract relevant paragraphs
                paragraphs = content['content'].split('\n\n')
                for para in paragraphs:
                    para_lower = para.lower()
                    if any(keyword in para_lower for keyword in keywords):
                        relevant_parts.append(para)
        
        # Limit to reasonable size
        combined = '\n\n'.join(relevant_parts)
        if len(combined) > 5000:
            combined = combined[:5000] + "..."
        
        return combined
    
    def extract_keywords(self, text):
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'}
        keywords = [w for w in words if len(w) > 3 and w not in common_words]
        return list(set(keywords))
    
    def build_wiki(self, contents):
        """Build the complete wiki"""
        print("Analyzing content structure...")
        toc_structure = self.extract_topics(contents)
        
        if not toc_structure:
            raise ValueError("Failed to generate table of contents")
        
        print("Generated table of contents:")
        print(toc_structure)
        print("\n" + "="*60 + "\n")
        
        # Parse the TOC structure to extract sections
        sections = self.parse_toc_structure(toc_structure)
        
        # Calculate words per section
        words_per_section = self.target_words // len(sections)
        
        # Generate wiki content
        wiki_content = f"""# Knowledge Base Wiki

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Table of Contents

{toc_structure}

---

"""
        
        # Generate each section
        for i, section in enumerate(sections):
            print(f"Generating section {i+1}/{len(sections)}: {section['title']}...")
            
            section_content = self.generate_section(
                section['title'],
                section.get('outline', ''),
                contents,
                words_per_section
            )
            
            if section_content:
                # Add section anchor
                anchor = self.create_anchor(section['title'])
                wiki_content += f"\n\n## {section['title']} {{#{anchor}}}\n\n"
                wiki_content += section_content
                wiki_content += "\n\n---"
            
            # Rate limiting
            time.sleep(2)
        
        # Add index and cross-references
        wiki_content = self.add_cross_references(wiki_content)
        
        # Add keyword index
        keywords = self.extract_all_keywords(wiki_content)
        wiki_content += self.create_keyword_index(keywords)
        
        return wiki_content
    
    def parse_toc_structure(self, toc_text):
        """Parse TOC structure into sections"""
        sections = []
        lines = toc_text.split('\n')
        
        current_section = None
        current_outline = []
        
        for line in lines:
            # Look for main sections (various formats)
            if re.match(r'^(\d+\.|\#{1,2}|\*|-)\s+(.+)', line):
                if current_section:
                    sections.append({
                        'title': current_section,
                        'outline': '\n'.join(current_outline)
                    })
                
                # Extract section title
                match = re.match(r'^(?:\d+\.|\#{1,2}|\*|-)\s+(.+)', line)
                if match:
                    current_section = match.group(1).strip()
                    current_outline = []
            elif line.strip() and current_section:
                current_outline.append(line.strip())
        
        # Add last section
        if current_section:
            sections.append({
                'title': current_section,
                'outline': '\n'.join(current_outline)
            })
        
        # If no sections found, create default ones
        if not sections:
            sections = [
                {'title': 'Introduction', 'outline': 'Overview and key concepts'},
                {'title': 'Core Concepts', 'outline': 'Fundamental principles and theories'},
                {'title': 'Implementation', 'outline': 'Practical applications and examples'},
                {'title': 'Advanced Topics', 'outline': 'Complex scenarios and edge cases'},
                {'title': 'Best Practices', 'outline': 'Recommendations and guidelines'},
                {'title': 'Troubleshooting', 'outline': 'Common issues and solutions'},
                {'title': 'Reference', 'outline': 'Quick reference and cheat sheets'},
                {'title': 'Conclusion', 'outline': 'Summary and next steps'}
            ]
        
        return sections
    
    def create_anchor(self, title):
        """Create anchor link from title"""
        return re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
    
    def add_cross_references(self, content):
        """Convert [[Topic]] references to proper markdown links"""
        def replace_reference(match):
            topic = match.group(1)
            anchor = self.create_anchor(topic)
            return f"[{topic}](#{anchor})"
        
        return re.sub(r'\[\[([^\]]+)\]\]', replace_reference, content)
    
    def extract_all_keywords(self, content):
        """Extract all important keywords from the wiki"""
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]()]', ' ', content)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only words longer than 4 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
        return [k[0] for k in keywords]
    
    def create_keyword_index(self, keywords):
        """Create keyword index section"""
        index = "\n\n## Keyword Index\n\n"
        
        # Group by first letter
        grouped = {}
        for keyword in sorted(keywords):
            first_letter = keyword[0].upper()
            if first_letter not in grouped:
                grouped[first_letter] = []
            grouped[first_letter].append(keyword)
        
        for letter, words in sorted(grouped.items()):
            index += f"\n### {letter}\n"
            for word in words:
                index += f"- {word}\n"
        
        return index
    
    def save_wiki(self, content):
        """Save wiki content to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as markdown
        md_file = self.output_dir / f"knowledge_base_wiki_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Save as text
        txt_file = self.output_dir / f"knowledge_base_wiki_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            # Convert markdown to plain text (simple conversion)
            text_content = re.sub(r'[#*`\[\]]', '', content)
            f.write(text_content)
        
        # Save metadata
        meta_file = self.output_dir / f"wiki_metadata_{timestamp}.json"
        metadata = {
            'generated': timestamp,
            'source_files': self.selected_files,
            'word_count': len(content.split()),
            'sections': len(re.findall(r'^##\s+', content, re.MULTILINE))
        }
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return md_file, txt_file
    
    def run(self):
        """Main execution flow"""
        try:
            print("=== Markdown to Wiki Builder ===\n")
            
            # Get API key
            print("Checking API key...")
            self.get_api_key()
            
            # Select files
            print("Select markdown files to combine...")
            files = self.select_files()
            
            if not files:
                print("No files selected. Exiting.")
                return
            
            print(f"\nSelected {len(files)} files:")
            for f in files:
                print(f"  - {Path(f).name}")
            
            # Read files
            print("\nReading markdown files...")
            contents = self.read_markdown_files()
            
            # Build wiki
            print("\nBuilding wiki (this may take several minutes)...")
            wiki_content = self.build_wiki(contents)
            
            # Save output
            print("\nSaving wiki...")
            md_file, txt_file = self.save_wiki(wiki_content)
            
            print(f"\n✓ Wiki successfully created!")
            print(f"  - Markdown: {md_file}")
            print(f"  - Text: {txt_file}")
            print(f"  - Word count: {len(wiki_content.split())}")
            
            # Open output directory
            os.startfile(self.output_dir)
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    builder = MarkdownWikiBuilder()
    builder.run()
