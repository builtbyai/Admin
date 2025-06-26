import os
import shutil
import time
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

class SimpleTextOrganizer:
    def __init__(self, source_folder):
        self.source_folder = Path(source_folder)
        self.log_file = Path("processed_files.log")
        self.processed_files = self.load_processed_files()
        
        # Simple categories without AI dependencies
        self.categories = [
            "technology", "science", "programming", "gaming", "movies", 
            "books", "music", "sports", "cooking", "travel", "fitness", 
            "photography", "art", "business", "education", "health", 
            "politics", "history", "philosophy", "psychology", "miscellaneous"
        ]
    
    def load_processed_files(self):
        """Load list of already processed files from log"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def save_processed_file(self, file_path):
        """Add file to processed log"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{file_path}\n")
        self.processed_files.add(str(file_path))
    
    def extract_simple_keywords(self, text, num_keywords=10):
        """Extract keywords using simple word frequency"""
        # Simple text cleaning
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = text.split()
        
        # Simple stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Filter words
        filtered_words = [word for word in words if len(word) > 2 and word not in stopwords]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        return [word for word, freq in word_freq.most_common(num_keywords)]
    
    def categorize_simple(self, text, keywords):
        """Simple categorization based on keyword matching"""
        text_lower = text.lower()
        keyword_text = ' '.join(keywords).lower()
        combined_text = text_lower + ' ' + keyword_text
        
        category_keywords = {
            "technology": ["tech", "software", "computer", "digital", "internet", "ai"],
            "science": ["research", "study", "experiment", "scientific", "biology", "chemistry", "physics"],
            "programming": ["code", "coding", "developer", "programming", "python", "javascript"],
            "gaming": ["game", "gaming", "player", "video game", "console"],
            "movies": ["film", "movie", "cinema", "director", "actor"],
            "books": ["book", "reading", "author", "novel", "literature"],
            "music": ["song", "music", "artist", "album", "band"],
            "sports": ["sport", "team", "player", "game", "match"],
            "cooking": ["recipe", "food", "cooking", "kitchen", "meal"],
            "travel": ["travel", "trip", "vacation", "destination"],
            "fitness": ["workout", "exercise", "fitness", "gym", "health"],
            "photography": ["photo", "camera", "photography", "picture"],
            "art": ["art", "artist", "painting", "drawing", "creative"],
            "business": ["business", "company", "market", "finance"],
            "education": ["education", "school", "learning", "student"],
            "health": ["health", "medical", "doctor", "medicine"],
            "politics": ["politics", "government", "election", "policy"],
            "history": ["history", "historical", "past", "ancient"],
            "philosophy": ["philosophy", "philosophical", "ethics"],
            "psychology": ["psychology", "mental", "behavior", "mind"]
        }
        
        best_category = "miscellaneous"
        best_score = 0
        
        for category, cat_keywords in category_keywords.items():
            score = sum(1 for keyword in cat_keywords if keyword in combined_text)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def create_folder_structure(self):
        """Create the folder structure for organizing files"""
        base_organized_folder = self.source_folder / "organized"
        base_organized_folder.mkdir(exist_ok=True)
        
        for category in self.categories:
            category_folder = base_organized_folder / category
            category_folder.mkdir(exist_ok=True)
        
        return base_organized_folder
    
    def process_single_file(self, file_path):
        """Process a single text file"""
        file_path = Path(file_path)
        
        if str(file_path) in self.processed_files:
            print(f"File already processed: {file_path}")
            return
        
        try:
            print(f"Processing: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                print(f"Empty file skipped: {file_path}")
                return
            
            keywords = self.extract_simple_keywords(content)
            print(f"Keywords: {keywords}")
            
            category = self.categorize_simple(content, keywords)
            print(f"Category: {category}")
            
            organized_folder = self.create_folder_structure()
            category_folder = organized_folder / category
            new_file_path = category_folder / file_path.name
            
            counter = 1
            while new_file_path.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                new_file_path = category_folder / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            shutil.copy2(file_path, new_file_path)
            
            metadata = {
                "original_path": str(file_path),
                "processed_date": datetime.now().isoformat(),
                "keywords": keywords,
                "category": category,
                "file_size": file_path.stat().st_size
            }
            
            metadata_file = new_file_path.with_suffix('.metadata.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            self.save_processed_file(str(file_path))
            print(f"File organized: {file_path} -> {new_file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def process_existing_files(self):
        """Process all existing txt files"""
        print(f"Scanning for txt files in: {self.source_folder}")
        
        txt_files = list(self.source_folder.glob("*.txt"))
        print(f"Found {len(txt_files)} txt files")
        
        for file_path in txt_files:
            if str(file_path) not in self.processed_files:
                self.process_single_file(file_path)

def main():
    print("Simple Text File Organizer (No AI Dependencies)")
    print("=" * 50)
    
    source_folder = input("Enter the path to the folder containing txt files (or press Enter for current directory): ").strip()
    
    if not source_folder:
        source_folder = "."
    
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Folder '{source_folder}' does not exist.")
        return
    
    print(f"Source folder: {source_path.absolute()}")
    
    organizer = SimpleTextOrganizer(source_path)
    organizer.process_existing_files()
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
