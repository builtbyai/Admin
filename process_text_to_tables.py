import os
import re
import json
import time
import requests
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, simpledialog
from collections import Counter, defaultdict
import pandas as pd
import csv

class TextAnalyzer:
    def __init__(self):
        # Hardcoded API key for development
        self.api_key = "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"
        self.selected_files = []
        self.output_dir = Path("text_analysis_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # OpenRouter API endpoint
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Use Google's Gemini 2.5 Pro with enhanced capabilities
        self.model = "google/gemini-2.5-pro"
        
        # Chunk size (50,000 characters)
        self.chunk_size = 50000
        
        # File truncation size (100,000 characters max per file)
        self.max_file_size = 100000
        
        # Storage for analysis results
        self.analysis_results = []
        self.file_summaries = []
        self.themes_data = []
        self.categories_data = []
        
    def prompt_api_key(self):
        """Skip API key prompt - using hardcoded key for development"""
        print("Using development API key...")
        return True
    
    def select_files(self):
        """Open file dialog to select text/markdown files"""
        root = tk.Tk()
        root.withdraw()
        
        files = filedialog.askopenfilenames(
            title="Select Text/Markdown Files",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ]
        )
        
        self.selected_files = list(files)
        return self.selected_files
    
    def categorize_content_with_llm(self, file_data):
        """Use LLM to intelligently categorize content"""
        # Truncate content for analysis
        content_preview = file_data['content'][:2000] if len(file_data['content']) > 2000 else file_data['content']
        
        prompt = f"""Analyze this file and provide smart categorization:

Filename: {file_data['filename']}
Content preview: {content_preview}...

Provide a JSON response with:
1. "category": The main category this content belongs to (e.g., "Technical Documentation", "Business Report", "Research Paper", etc.)
2. "subcategory": A more specific subcategory
3. "primary_theme": The main theme or topic
4. "content_type": Type of content (e.g., "Tutorial", "Analysis", "Reference", etc.)
5. "domain": The field or domain (e.g., "Software Development", "Marketing", "Science", etc.)
6. "tags": List of 5 relevant tags
7. "summary": A 2-3 sentence summary
8. "key_topics": List of 3-5 key topics covered
9. "keywords": List of exactly 5 most important keywords or concepts from this content

Format as valid JSON."""

        response = self.call_llm(prompt, max_tokens=1000)
        
        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        
        # Fallback categorization
        return {
            "category": "General",
            "subcategory": "Uncategorized",
            "primary_theme": "Unknown",
            "content_type": "Document",
            "domain": "General",
            "tags": ["unprocessed"],
            "summary": "Unable to process",
            "key_topics": [],
            "keywords": ["unknown", "unprocessed", "general", "document", "content"]
        }
    
    def chunk_text(self, text, chunk_size=50000):
        """Split text into chunks of specified size"""
        chunks = []
        
        # Try to split at sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If no sentences found, fall back to character splitting
        if not chunks:
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        return chunks
    
    def call_llm(self, prompt, max_tokens=2000):
        """Call OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/text-analyzer",
            "X-Title": "Text Analyzer"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3  # Lower temperature for more consistent analysis
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"API Error: {str(e)}")
            return None
    
    def analyze_chunk(self, chunk_text, chunk_number, total_chunks, filename):
        """Analyze a single chunk of text"""
        prompt = f"""Analyze this text chunk (chunk {chunk_number} of {total_chunks} from file: {filename}).

Text chunk:
{chunk_text[:45000]}  # Limit to ensure we don't exceed token limits

Provide a structured analysis with the following:

1. SUMMARY: A concise summary of this chunk (2-3 paragraphs)

2. THEMES: List the main themes found in this chunk (up to 10 themes)

3. KEY_POINTS: Extract 5-10 key points or important facts

4. KEYWORDS: List 10-20 important keywords or phrases

5. TAGS: Generate exactly 5 descriptive tags for this content

Format your response as JSON with these exact keys:
{{
    "summary": "...",
    "themes": ["theme1", "theme2", ...],
    "key_points": ["point1", "point2", ...],
    "keywords": ["keyword1", "keyword2", ...],
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""

        response = self.call_llm(prompt, max_tokens=2000)
        
        if response:
            try:
                # Try to parse JSON response
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    # Fallback parsing if not proper JSON
                    return self.parse_response_fallback(response)
            except:
                return self.parse_response_fallback(response)
        
        return None
    
    def parse_response_fallback(self, response):
        """Fallback parser if JSON parsing fails"""
        result = {
            "summary": "",
            "themes": [],
            "key_points": [],
            "keywords": [],
            "tags": []
        }
        
        # Simple extraction based on sections
        sections = response.split('\n\n')
        for section in sections:
            lower_section = section.lower()
            if 'summary' in lower_section:
                result['summary'] = section.split(':', 1)[-1].strip()
            elif 'theme' in lower_section:
                themes = re.findall(r'[-•]\s*(.+)', section)
                result['themes'] = [t.strip() for t in themes]
            elif 'key' in lower_section and 'point' in lower_section:
                points = re.findall(r'[-•]\s*(.+)', section)
                result['key_points'] = [p.strip() for p in points]
            elif 'keyword' in lower_section:
                keywords = re.findall(r'[-•]\s*(.+)', section)
                result['keywords'] = [k.strip() for k in keywords]
            elif 'tag' in lower_section:
                tags = re.findall(r'[-•]\s*(.+)', section)
                result['tags'] = [t.strip() for t in tags][:5]
        
        return result
    
    def process_file(self, filepath):
        """Process a single file"""
        print(f"\nProcessing: {filepath}")
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return None
        
        # Truncate file if too large
        if len(content) > self.max_file_size:
            print(f"  Truncating file from {len(content)} to {self.max_file_size} characters")
            content = content[:self.max_file_size]
        
        filename = Path(filepath).name
        
        # Get intelligent categorization
        file_data = {
            'filename': filename,
            'filepath': str(filepath),
            'content': content,
            'size': len(content)
        }
        
        print("  Getting smart categorization...")
        categorization = self.categorize_content_with_llm(file_data)
        
        # Chunk the content
        chunks = self.chunk_text(content, self.chunk_size)
        print(f"  Split into {len(chunks)} chunks")
        
        # Process each chunk
        chunk_summaries = []
        all_themes = []
        all_keywords = []
        all_tags = categorization.get('tags', [])
        all_key_points = []
        
        for i, chunk in enumerate(chunks, 1):
            print(f"  Analyzing chunk {i}/{len(chunks)}...")
            
            analysis = self.analyze_chunk(chunk, i, len(chunks), filename)
            
            if analysis:
                chunk_summaries.append(analysis.get('summary', ''))
                all_themes.extend(analysis.get('themes', []))
                all_keywords.extend(analysis.get('keywords', []))
                all_tags.extend(analysis.get('tags', []))
                all_key_points.extend(analysis.get('key_points', []))
            
            # Rate limiting
            time.sleep(2)
        
        # Generate overall file summary
        overall_summary = self.generate_file_summary(filename, chunk_summaries)
        
        # Get the 5 keywords from categorization
        five_keywords = categorization.get('keywords', [])[:5]
        if len(five_keywords) < 5:
            # Fill with top keywords from analysis
            additional_keywords = [kw for kw in all_keywords if kw not in five_keywords]
            five_keywords.extend(additional_keywords[:5-len(five_keywords)])
        
        # Compile results
        file_result = {
            'filename': filename,
            'filepath': str(filepath),
            'file_size': len(content),
            'chunk_count': len(chunks),
            'category': categorization.get('category', 'General'),
            'subcategory': categorization.get('subcategory', 'Uncategorized'),
            'primary_theme': categorization.get('primary_theme', 'Unknown'),
            'content_type': categorization.get('content_type', 'Document'),
            'domain': categorization.get('domain', 'General'),
            'summary': overall_summary or categorization.get('summary', ''),
            'five_keywords': ', '.join(five_keywords),  # Exactly 5 keywords
            'tags': ', '.join(list(set(all_tags))[:5]),  # Top 5 unique tags
            'themes': ', '.join(list(set(all_themes))[:10]),  # Top 10 themes
            'all_keywords': ', '.join(list(set(all_keywords))[:20]),  # Top 20 keywords
            'key_points': ' | '.join(all_key_points[:5]),  # Top 5 key points
            'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.analysis_results.append(file_result)
        
        # Add to themed collections
        self.organize_by_theme(file_result)
        
        return file_result
    
    def organize_by_theme(self, file_result):
        """Organize files into themed collections"""
        # Add to category-based collection
        category_entry = {
            'category': file_result['category'],
            'subcategory': file_result['subcategory'],
            'filename': file_result['filename'],
            'domain': file_result['domain'],
            'content_type': file_result['content_type'],
            'primary_theme': file_result['primary_theme'],
            'summary': file_result['summary'],
            'tags': file_result['tags']
        }
        self.categories_data.append(category_entry)
        
        # Add to theme-based collection
        themes = file_result['themes'].split(', ') if file_result['themes'] else []
        for theme in themes[:3]:  # Top 3 themes
            theme_entry = {
                'theme': theme,
                'filename': file_result['filename'],
                'category': file_result['category'],
                'relevance': 'High' if theme == file_result['primary_theme'] else 'Medium',
                'summary_excerpt': file_result['summary'][:200] + '...' if len(file_result['summary']) > 200 else file_result['summary']
            }
            self.themes_data.append(theme_entry)
    
    def generate_file_summary(self, filename, chunk_summaries):
        """Generate overall summary for the file"""
        if not chunk_summaries:
            return ""
        
        # Combine summaries for overall analysis
        combined_summary = "\n\n".join(chunk_summaries)
        
        prompt = f"""Based on these chunk summaries from {filename}, create a comprehensive overall summary.

Chunk summaries:
{combined_summary[:40000]}

Provide a concise summary (2-3 paragraphs) that captures:
1. The main purpose and content
2. Key insights or findings
3. Overall significance

Format as clear text, not JSON."""

        overall_summary = self.call_llm(prompt, max_tokens=1000)
        return overall_summary or "Summary generation failed"
    
    def create_smart_tables(self):
        """Create intelligently organized CSV tables"""
        print("\nCreating smart categorized tables...")
        
        # Create main analysis table
        main_df = pd.DataFrame(self.analysis_results)
        
        # Create category-based pivot table
        if self.categories_data:
            category_df = pd.DataFrame(self.categories_data)
            
            # Group by category and domain
            category_summary = category_df.groupby(['category', 'domain']).agg({
                'filename': 'count',
                'subcategory': lambda x: ', '.join(set(x))
            }).reset_index()
            category_summary.columns = ['Category', 'Domain', 'File_Count', 'Subcategories']
        
        # Create theme analysis table
        if self.themes_data:
            theme_df = pd.DataFrame(self.themes_data)
            
            # Theme frequency analysis
            theme_freq = theme_df['theme'].value_counts().reset_index()
            theme_freq.columns = ['Theme', 'Frequency']
        
        # Create content type distribution
        content_type_dist = main_df.groupby(['content_type', 'category']).size().reset_index(name='Count')
        
        # Create tag cloud data
        all_tags = []
        for tags in main_df['tags']:
            if tags:
                all_tags.extend(tags.split(', '))
        tag_freq = pd.Series(all_tags).value_counts().reset_index()
        tag_freq.columns = ['Tag', 'Frequency']
        
        return {
            'main_analysis': main_df,
            'category_summary': category_summary if 'category_summary' in locals() else None,
            'theme_analysis': theme_df if self.themes_data else None,
            'theme_frequency': theme_freq if 'theme_freq' in locals() else None,
            'content_type_distribution': content_type_dist,
            'tag_frequency': tag_freq
        }
    
    def export_results(self):
        """Export analysis results to CSV files"""
        print("\nExporting results to CSV files...")
        
        # Create CSV subdirectory with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_dir = self.output_dir / f"csv_analysis_{timestamp}"
        csv_dir.mkdir(exist_ok=True)
        
        # Get smart tables
        tables = self.create_smart_tables()
        
        # Export main analysis table
        if tables['main_analysis'] is not None and not tables['main_analysis'].empty:
            main_file = csv_dir / "01_complete_file_analysis.csv"
            tables['main_analysis'].to_csv(main_file, index=False, encoding='utf-8')
            print(f"  ✓ Exported: {main_file.name}")
        
        # Export category summary
        if tables['category_summary'] is not None and not tables['category_summary'].empty:
            cat_file = csv_dir / "02_category_summary.csv"
            tables['category_summary'].to_csv(cat_file, index=False, encoding='utf-8')
            print(f"  ✓ Exported: {cat_file.name}")
        
        # Export theme analysis
        if tables['theme_analysis'] is not None and not tables['theme_analysis'].empty:
            theme_file = csv_dir / "03_theme_analysis.csv"
            tables['theme_analysis'].to_csv(theme_file, index=False, encoding='utf-8')
            print(f"  ✓ Exported: {theme_file.name}")
        
        # Export theme frequency
        if tables['theme_frequency'] is not None and not tables['theme_frequency'].empty:
            theme_freq_file = csv_dir / "04_theme_frequency.csv"
            tables['theme_frequency'].to_csv(theme_freq_file, index=False, encoding='utf-8')
            print(f"  ✓ Exported: {theme_freq_file.name}")
        
        # Export content type distribution
        if tables['content_type_distribution'] is not None and not tables['content_type_distribution'].empty:
            content_file = csv_dir / "05_content_type_distribution.csv"
            tables['content_type_distribution'].to_csv(content_file, index=False, encoding='utf-8')
            print(f"  ✓ Exported: {content_file.name}")
        
        # Export tag frequency
        if tables['tag_frequency'] is not None and not tables['tag_frequency'].empty:
            tag_file = csv_dir / "06_tag_cloud_data.csv"
            tables['tag_frequency'].to_csv(tag_file, index=False, encoding='utf-8')
            print(f"  ✓ Exported: {tag_file.name}")
        
        # Create a summary report
        self.create_summary_report(csv_dir, tables)
        
        # Create keywords and summaries file
        self.create_keywords_summary_file(csv_dir)
        
        print(f"\n✓ All CSV files exported to: {csv_dir}")
        return csv_dir
    
    def create_keywords_summary_file(self, csv_dir):
        """Create a dedicated file with titles, keywords, and summaries"""
        keywords_file = csv_dir / "keywords_and_summaries.txt"
        
        with open(keywords_file, 'w', encoding='utf-8') as f:
            f.write("FILE KEYWORDS AND SUMMARIES\n")
            f.write("=" * 80 + "\n\n")
            
            for result in self.analysis_results:
                f.write(f"TITLE: {result['filename']}\n")
                f.write(f"5 KEYWORDS: {result['five_keywords']}\n")
                f.write(f"EXPANDED SUMMARY: {result['summary']}\n")
                f.write("\n" + "-" * 80 + "\n\n")
        
        print(f"  ✓ Exported: keywords_and_summaries.txt")
    
    def create_summary_report(self, csv_dir, tables):
        """Create a text summary report"""
        report_file = csv_dir / "00_analysis_summary_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("TEXT ANALYSIS SUMMARY REPORT WITH KEYWORDS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Output Directory: {csv_dir.name}\n\n")
            
            # Files processed
            file_count = len(self.analysis_results)
            f.write(f"Files Processed: {file_count}\n\n")
            
            # Category distribution
            if tables['main_analysis'] is not None and not tables['main_analysis'].empty:
                f.write("CATEGORY DISTRIBUTION:\n")
                f.write("-" * 40 + "\n")
                cat_dist = tables['main_analysis']['category'].value_counts()
                for cat, count in cat_dist.items():
                    f.write(f"  - {cat}: {count} files\n")
                f.write("\n")
            
            # Top themes
            if tables['theme_frequency'] is not None and not tables['theme_frequency'].empty:
                f.write("TOP THEMES:\n")
                f.write("-" * 40 + "\n")
                for _, row in tables['theme_frequency'].head(10).iterrows():
                    f.write(f"  - {row['Theme']}: {row['Frequency']} occurrences\n")
                f.write("\n")
            
            # Content type distribution
            if tables['main_analysis'] is not None and not tables['main_analysis'].empty:
                f.write("CONTENT TYPES:\n")
                f.write("-" * 40 + "\n")
                content_dist = tables['main_analysis']['content_type'].value_counts()
                for ctype, count in content_dist.items():
                    f.write(f"  - {ctype}: {count} files\n")
                f.write("\n")
            
            # File summaries with keywords
            f.write("\nFILE SUMMARIES WITH KEYWORDS:\n")
            f.write("-" * 60 + "\n")
            for result in self.analysis_results:
                f.write(f"\nFILE: {result['filename']}\n")
                f.write(f"KEYWORDS: {result['five_keywords']}\n")
                f.write(f"Category: {result['category']} > {result['subcategory']}\n")
                f.write(f"Tags: {result['tags']}\n")
                f.write(f"Summary: {result['summary']}\n")
                f.write("-" * 60 + "\n")
        
        print(f"  ✓ Exported: {report_file.name}")
    
    def run(self):
        """Main execution flow"""
        try:
            print("=== Smart Text File Analyzer (CSV Export Only) ===\n")
            
            # Prompt for API key at startup
            print("API Key Required...")
            if not self.prompt_api_key():
                return
            
            print("\n✓ API key accepted\n")
            
            # Select files
            print("Select text/markdown files to analyze...")
            files = self.select_files()
            
            if not files:
                print("No files selected. Exiting.")
                return
            
            print(f"\nSelected {len(files)} files:")
            for f in files:
                print(f"  - {Path(f).name}")
            
            # Process each file
            print("\nStarting intelligent content analysis...")
            for filepath in files:
                self.process_file(filepath)
            
            # Export results
            csv_dir = self.export_results()
            
            print("\n✓ Analysis complete!")
            print(f"\nResults saved in: {csv_dir.absolute()}")
            print("\nGenerated files:")
            print("  - 00_analysis_summary_report.txt - Text report with 5 keywords per file")
            print("  - 01_complete_file_analysis.csv - All files with full analysis and keywords")
            print("  - 02_category_summary.csv - Files grouped by category")
            print("  - 03_theme_analysis.csv - Theme-based organization")
            print("  - 04_theme_frequency.csv - Most common themes")
            print("  - 05_content_type_distribution.csv - Content type breakdown")
            print("  - 06_tag_cloud_data.csv - Tag frequency for visualization")
            
            # Open output directory
            os.startfile(csv_dir)
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    analyzer = TextAnalyzer()
    analyzer.run()
