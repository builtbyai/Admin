import os
import re
import json
import time
import requests
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from collections import Counter, defaultdict
import pandas as pd

class TextAnalyzer:
    def __init__(self):
        self.api_key = None
        self.selected_files = []
        self.output_dir = Path("text_analysis_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # OpenRouter API endpoint
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Use Google's Gemini 2.5 Pro with enhanced capabilities
        self.model = "google/gemini-2.5-pro"
        
        # Chunk size (50,000 characters)
        self.chunk_size = 50000
        
        # Database setup
        self.db_path = self.output_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        self.conn = None
        self.cursor = None
        
    def get_api_key(self):
        """Get API key from user or file"""
        api_key_file = Path("openrouter_api_key.txt")
        
        if api_key_file.exists():
            with open(api_key_file, 'r') as f:
                self.api_key = f.read().strip()
        else:
            root = tk.Tk()
            root.withdraw()
            
            from tkinter import simpledialog
            
            # Create a more detailed dialog
            message = """Enter your OpenRouter API key:

This script uses Google's Gemini 2.5 Pro model for advanced text analysis.

To get an API key:
1. Go to https://openrouter.ai/
2. Sign up for a free account
3. Generate an API key from your dashboard
4. Paste it below

Your API key will be saved locally for future use."""
            
            api_key = simpledialog.askstring(
                "OpenRouter API Key Required",
                message,
                show='*'
            )
            
            if api_key:
                self.api_key = api_key
                with open(api_key_file, 'w') as f:
                    f.write(api_key)
            else:
                raise ValueError("API key is required")
    
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
    
    def setup_database(self):
        """Create database tables for storing analysis results"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Files table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_hash TEXT UNIQUE,
                total_size INTEGER,
                chunk_count INTEGER,
                processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chunks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                chunk_number INTEGER,
                chunk_size INTEGER,
                content TEXT,
                summary TEXT,
                themes TEXT,
                FOREIGN KEY (file_id) REFERENCES files(file_id)
            )
        ''')
        
        # Themes table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS themes (
                theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_name TEXT UNIQUE,
                description TEXT,
                occurrence_count INTEGER DEFAULT 0
            )
        ''')
        
        # File themes relationship table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_themes (
                file_id INTEGER,
                theme_id INTEGER,
                relevance_score REAL,
                PRIMARY KEY (file_id, theme_id),
                FOREIGN KEY (file_id) REFERENCES files(file_id),
                FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
            )
        ''')
        
        # Tags table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE
            )
        ''')
        
        # File tags relationship table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files(file_id),
                FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
            )
        ''')
        
        # Key points table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_points (
                point_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                point_text TEXT,
                importance_score REAL,
                FOREIGN KEY (file_id) REFERENCES files(file_id)
            )
        ''')
        
        # Keywords table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE,
                frequency INTEGER DEFAULT 0
            )
        ''')
        
        # File keywords relationship table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_keywords (
                file_id INTEGER,
                keyword_id INTEGER,
                frequency INTEGER,
                PRIMARY KEY (file_id, keyword_id),
                FOREIGN KEY (file_id) REFERENCES files(file_id),
                FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id)
            )
        ''')
        
        # Summary table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                summary_text TEXT,
                summary_type TEXT,
                FOREIGN KEY (file_id) REFERENCES files(file_id)
            )
        ''')
        
        # Cross-file relationships table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_relationships (
                relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file1_id INTEGER,
                file2_id INTEGER,
                relationship_type TEXT,
                similarity_score REAL,
                FOREIGN KEY (file1_id) REFERENCES files(file_id),
                FOREIGN KEY (file2_id) REFERENCES files(file_id)
            )
        ''')
        
        self.conn.commit()
    
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
        
        # Calculate file hash
        file_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Check if file already processed
        self.cursor.execute("SELECT file_id FROM files WHERE file_hash = ?", (file_hash,))
        existing = self.cursor.fetchone()
        if existing:
            print(f"File already processed (ID: {existing[0]})")
            return existing[0]
        
        # Chunk the content
        chunks = self.chunk_text(content, self.chunk_size)
        print(f"Split into {len(chunks)} chunks")
        
        # Insert file record
        filename = Path(filepath).name
        self.cursor.execute('''
            INSERT INTO files (filename, filepath, file_hash, total_size, chunk_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, str(filepath), file_hash, len(content), len(chunks)))
        file_id = self.cursor.lastrowid
        
        # Process each chunk
        all_themes = []
        all_keywords = []
        all_tags = []
        all_key_points = []
        
        for i, chunk in enumerate(chunks, 1):
            print(f"  Analyzing chunk {i}/{len(chunks)}...")
            
            analysis = self.analyze_chunk(chunk, i, len(chunks), filename)
            
            if analysis:
                # Store chunk data
                self.cursor.execute('''
                    INSERT INTO chunks (file_id, chunk_number, chunk_size, content, summary, themes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (file_id, i, len(chunk), chunk, analysis.get('summary', ''), 
                      json.dumps(analysis.get('themes', []))))
                
                # Collect data for aggregation
                all_themes.extend(analysis.get('themes', []))
                all_keywords.extend(analysis.get('keywords', []))
                all_tags.extend(analysis.get('tags', []))
                all_key_points.extend(analysis.get('key_points', []))
                
                # Store summary
                if analysis.get('summary'):
                    self.cursor.execute('''
                        INSERT INTO summaries (file_id, summary_text, summary_type)
                        VALUES (?, ?, ?)
                    ''', (file_id, analysis['summary'], f'chunk_{i}'))
            
            # Rate limiting
            time.sleep(2)
        
        # Process aggregated data
        self.process_themes(file_id, all_themes)
        self.process_keywords(file_id, all_keywords)
        self.process_tags(file_id, all_tags)
        self.process_key_points(file_id, all_key_points)
        
        # Generate overall file summary
        self.generate_file_summary(file_id, chunks)
        
        self.conn.commit()
        return file_id
    
    def process_themes(self, file_id, themes):
        """Process and store themes"""
        theme_counts = Counter(themes)
        
        for theme, count in theme_counts.items():
            # Insert or get theme
            self.cursor.execute("SELECT theme_id FROM themes WHERE theme_name = ?", (theme,))
            result = self.cursor.fetchone()
            
            if result:
                theme_id = result[0]
                self.cursor.execute(
                    "UPDATE themes SET occurrence_count = occurrence_count + ? WHERE theme_id = ?",
                    (count, theme_id)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO themes (theme_name, occurrence_count) VALUES (?, ?)",
                    (theme, count)
                )
                theme_id = self.cursor.lastrowid
            
            # Link theme to file
            relevance_score = count / len(themes) if themes else 0
            self.cursor.execute('''
                INSERT INTO file_themes (file_id, theme_id, relevance_score)
                VALUES (?, ?, ?)
            ''', (file_id, theme_id, relevance_score))
    
    def process_keywords(self, file_id, keywords):
        """Process and store keywords"""
        keyword_counts = Counter(keywords)
        
        for keyword, count in keyword_counts.items():
            # Insert or get keyword
            self.cursor.execute("SELECT keyword_id FROM keywords WHERE keyword = ?", (keyword,))
            result = self.cursor.fetchone()
            
            if result:
                keyword_id = result[0]
                self.cursor.execute(
                    "UPDATE keywords SET frequency = frequency + ? WHERE keyword_id = ?",
                    (count, keyword_id)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO keywords (keyword, frequency) VALUES (?, ?)",
                    (keyword, count)
                )
                keyword_id = self.cursor.lastrowid
            
            # Link keyword to file
            self.cursor.execute('''
                INSERT INTO file_keywords (file_id, keyword_id, frequency)
                VALUES (?, ?, ?)
            ''', (file_id, keyword_id, count))
    
    def process_tags(self, file_id, tags):
        """Process and store tags (limit to 5 most common)"""
        tag_counts = Counter(tags)
        top_tags = [tag for tag, _ in tag_counts.most_common(5)]
        
        for tag in top_tags:
            # Insert or get tag
            self.cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ?", (tag,))
            result = self.cursor.fetchone()
            
            if result:
                tag_id = result[0]
            else:
                self.cursor.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag,))
                tag_id = self.cursor.lastrowid
            
            # Link tag to file
            self.cursor.execute('''
                INSERT OR IGNORE INTO file_tags (file_id, tag_id)
                VALUES (?, ?)
            ''', (file_id, tag_id))
    
    def process_key_points(self, file_id, key_points):
        """Process and store key points"""
        # Remove duplicates while preserving order
        seen = set()
        unique_points = []
        for point in key_points:
            if point not in seen:
                seen.add(point)
                unique_points.append(point)
        
        # Calculate importance scores based on position and frequency
        for i, point in enumerate(unique_points[:20]):  # Limit to top 20
            importance_score = 1.0 - (i / len(unique_points))
            self.cursor.execute('''
                INSERT INTO key_points (file_id, point_text, importance_score)
                VALUES (?, ?, ?)
            ''', (file_id, point, importance_score))
    
    def generate_file_summary(self, file_id, chunks):
        """Generate overall summary for the file"""
        # Get all chunk summaries
        self.cursor.execute(
            "SELECT summary FROM chunks WHERE file_id = ? ORDER BY chunk_number",
            (file_id,)
        )
        chunk_summaries = [row[0] for row in self.cursor.fetchall()]
        
        if not chunk_summaries:
            return
        
        # Combine summaries for overall analysis
        combined_summary = "\n\n".join(chunk_summaries)
        
        prompt = f"""Based on these chunk summaries, create a comprehensive overall summary of the entire document.

Chunk summaries:
{combined_summary[:40000]}

Provide:
1. A comprehensive summary (3-5 paragraphs)
2. Main conclusions or insights
3. How different parts of the document relate to each other

Format as clear text, not JSON."""

        overall_summary = self.call_llm(prompt, max_tokens=1500)
        
        if overall_summary:
            self.cursor.execute('''
                INSERT INTO summaries (file_id, summary_text, summary_type)
                VALUES (?, ?, ?)
            ''', (file_id, overall_summary, 'overall'))
    
    def find_file_relationships(self):
        """Find relationships between files based on themes and keywords"""
        print("\nAnalyzing relationships between files...")
        
        # Get all files
        self.cursor.execute("SELECT file_id FROM files")
        file_ids = [row[0] for row in self.cursor.fetchall()]
        
        for i, file1_id in enumerate(file_ids):
            for file2_id in file_ids[i+1:]:
                # Calculate similarity based on shared themes
                self.cursor.execute('''
                    SELECT COUNT(*) as shared_themes,
                           AVG(ft1.relevance_score + ft2.relevance_score) as avg_relevance
                    FROM file_themes ft1
                    JOIN file_themes ft2 ON ft1.theme_id = ft2.theme_id
                    WHERE ft1.file_id = ? AND ft2.file_id = ?
                ''', (file1_id, file2_id))
                
                result = self.cursor.fetchone()
                shared_themes = result[0] if result else 0
                avg_relevance = result[1] if result and result[1] else 0
                
                if shared_themes > 0:
                    # Calculate similarity score
                    similarity_score = shared_themes * avg_relevance
                    
                    self.cursor.execute('''
                        INSERT INTO file_relationships 
                        (file1_id, file2_id, relationship_type, similarity_score)
                        VALUES (?, ?, ?, ?)
                    ''', (file1_id, file2_id, 'thematic_similarity', similarity_score))
        
        self.conn.commit()
    
    def export_results(self):
        """Export analysis results to various formats"""
        print("\nExporting results...")
        
        # Create CSV subdirectory
        csv_dir = self.output_dir / "csv_exports"
        csv_dir.mkdir(exist_ok=True)
        
        # Export all tables to CSV
        self.export_all_tables_to_csv(csv_dir)
        
        # Export to Excel
        excel_file = self.output_dir / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Files overview
            files_df = pd.read_sql_query(
                "SELECT * FROM files ORDER BY filename",
                self.conn
            )
            files_df.to_excel(writer, sheet_name='Files', index=False)
            
            # Themes analysis
            themes_df = pd.read_sql_query('''
                SELECT t.theme_name, t.occurrence_count, 
                       GROUP_CONCAT(f.filename) as files
                FROM themes t
                JOIN file_themes ft ON t.theme_id = ft.theme_id
                JOIN files f ON ft.file_id = f.file_id
                GROUP BY t.theme_id
                ORDER BY t.occurrence_count DESC
            ''', self.conn)
            themes_df.to_excel(writer, sheet_name='Themes', index=False)
            
            # Keywords analysis
            keywords_df = pd.read_sql_query('''
                SELECT k.keyword, k.frequency,
                       COUNT(DISTINCT fk.file_id) as file_count
                FROM keywords k
                JOIN file_keywords fk ON k.keyword_id = fk.keyword_id
                GROUP BY k.keyword_id
                ORDER BY k.frequency DESC
                LIMIT 100
            ''', self.conn)
            keywords_df.to_excel(writer, sheet_name='Top Keywords', index=False)
            
            # File relationships
            relationships_df = pd.read_sql_query('''
                SELECT f1.filename as file1, f2.filename as file2,
                       fr.relationship_type, fr.similarity_score
                FROM file_relationships fr
                JOIN files f1 ON fr.file1_id = f1.file_id
                JOIN files f2 ON fr.file2_id = f2.file_id
                ORDER BY fr.similarity_score DESC
            ''', self.conn)
            relationships_df.to_excel(writer, sheet_name='File Relationships', index=False)
            
            # Summaries
            summaries_df = pd.read_sql_query('''
                SELECT f.filename, s.summary_type, s.summary_text
                FROM summaries s
                JOIN files f ON s.file_id = f.file_id
                WHERE s.summary_type = 'overall'
                ORDER BY f.filename
            ''', self.conn)
            summaries_df.to_excel(writer, sheet_name='Summaries', index=False)
        
        print(f"Results exported to: {excel_file}")
        
        # Also create a summary report
        self.create_summary_report()
    
    def export_all_tables_to_csv(self, csv_dir):
        """Export all database tables to CSV files"""
        print("Exporting database tables to CSV...")
        
        # Get all table names
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.cursor.fetchall()]
        
        for table in tables:
            try:
                # Read table into DataFrame
                df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
                
                # Save to CSV
                csv_file = csv_dir / f"{table}.csv"
                df.to_csv(csv_file, index=False, encoding='utf-8')
                print(f"  - Exported {table}.csv ({len(df)} rows)")
                
            except Exception as e:
                print(f"  - Error exporting {table}: {str(e)}")
        
        # Also export some custom queries as CSV
        
        # Files with all relationships
        query = '''
            SELECT f.*, 
                   GROUP_CONCAT(DISTINCT t.tag_name) as tags,
                   COUNT(DISTINCT ft.theme_id) as theme_count,
                   COUNT(DISTINCT fk.keyword_id) as keyword_count
            FROM files f
            LEFT JOIN file_tags ftg ON f.file_id = ftg.file_id
            LEFT JOIN tags t ON ftg.tag_id = t.tag_id
            LEFT JOIN file_themes ft ON f.file_id = ft.file_id
            LEFT JOIN file_keywords fk ON f.file_id = fk.file_id
            GROUP BY f.file_id
        '''
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(csv_dir / "files_with_metadata.csv", index=False)
        print("  - Exported files_with_metadata.csv")
        
        # Theme analysis
        query = '''
            SELECT t.theme_name, t.occurrence_count,
                   COUNT(DISTINCT ft.file_id) as file_count,
                   AVG(ft.relevance_score) as avg_relevance,
                   GROUP_CONCAT(DISTINCT f.filename) as files
            FROM themes t
            JOIN file_themes ft ON t.theme_id = ft.theme_id
            JOIN files f ON ft.file_id = f.file_id
            GROUP BY t.theme_id
            ORDER BY t.occurrence_count DESC
        '''
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(csv_dir / "theme_analysis.csv", index=False)
        print("  - Exported theme_analysis.csv")
        
        # Keyword analysis
        query = '''
            SELECT k.keyword, k.frequency,
                   COUNT(DISTINCT fk.file_id) as file_count,
                   GROUP_CONCAT(DISTINCT f.filename) as files
            FROM keywords k
            JOIN file_keywords fk ON k.keyword_id = fk.keyword_id
            JOIN files f ON fk.file_id = f.file_id
            GROUP BY k.keyword_id
            ORDER BY k.frequency DESC
        '''
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(csv_dir / "keyword_analysis.csv", index=False)
        print("  - Exported keyword_analysis.csv")
        
        # All summaries
        query = '''
            SELECT f.filename, s.summary_type, s.summary_text
            FROM summaries s
            JOIN files f ON s.file_id = f.file_id
            ORDER BY f.filename, s.summary_type
        '''
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(csv_dir / "all_summaries.csv", index=False)
        print("  - Exported all_summaries.csv")
        
        # Key points with scores
        query = '''
            SELECT f.filename, kp.point_text, kp.importance_score
            FROM key_points kp
            JOIN files f ON kp.file_id = f.file_id
            ORDER BY f.filename, kp.importance_score DESC
        '''
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(csv_dir / "key_points.csv", index=False)
        print("  - Exported key_points.csv")
        
        print(f"\nAll CSV files exported to: {csv_dir}")
    
    def create_summary_report(self):
        """Create a text summary report"""
        report_file = self.output_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("TEXT ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {self.db_path}\n\n")
            
            # Files processed
            self.cursor.execute("SELECT COUNT(*) FROM files")
            file_count = self.cursor.fetchone()[0]
            f.write(f"Files Processed: {file_count}\n\n")
            
            # Top themes
            f.write("TOP THEMES:\n")
            f.write("-" * 40 + "\n")
            self.cursor.execute('''
                SELECT theme_name, occurrence_count
                FROM themes
                ORDER BY occurrence_count DESC
                LIMIT 10
            ''')
            for theme, count in self.cursor.fetchall():
                f.write(f"  - {theme}: {count} occurrences\n")
            
            # File summaries
            f.write("\n\nFILE SUMMARIES:\n")
            f.write("-" * 40 + "\n")
            self.cursor.execute('''
                SELECT f.filename, s.summary_text
                FROM files f
                JOIN summaries s ON f.file_id = s.file_id
                WHERE s.summary_type = 'overall'
                ORDER BY f.filename
            ''')
            for filename, summary in self.cursor.fetchall():
                f.write(f"\n{filename}:\n{summary}\n")
        
        print(f"Report saved to: {report_file}")
    
    def run(self):
        """Main execution flow"""
        try:
            print("=== Text File Analyzer ===\n")
            
            # Get API key
            print("Checking API key...")
            self.get_api_key()
            
            # Select files
            print("Select text/markdown files to analyze...")
            files = self.select_files()
            
            if not files:
                print("No files selected. Exiting.")
                return
            
            print(f"\nSelected {len(files)} files:")
            for f in files:
                print(f"  - {Path(f).name}")
            
            # Setup database
            print("\nSetting up database...")
            self.setup_database()
            
            # Process each file
            for filepath in files:
                self.process_file(filepath)
            
            # Find relationships
            self.find_file_relationships()
            
            # Export results
            self.export_results()
            
            # Close database
            self.conn.close()
            
            print("\n✓ Analysis complete!")
            print(f"Results saved in: {self.output_dir.absolute()}")
            print("\nExported files:")
            print(f"  - SQLite database: {self.db_path.name}")
            print(f"  - Excel workbook: analysis_results_*.xlsx")
            print(f"  - CSV files: csv_exports/ directory")
            print(f"  - Summary report: analysis_report_*.txt")
            
            # Open output directory
            os.startfile(self.output_dir)
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    analyzer = TextAnalyzer()
    analyzer.run()
