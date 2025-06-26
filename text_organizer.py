import os
import shutil
import time
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

class TextFileHandler(FileSystemEventHandler):
    def __init__(self, organizer):
        self.organizer = organizer
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            print(f"New file detected: {event.src_path}")
            time.sleep(1)  # Wait a moment for file to be fully written
            self.organizer.process_single_file(event.src_path)

class TextOrganizer:
    def __init__(self, source_folder):
        self.source_folder = Path(source_folder)
        self.log_file = Path("processed_files.log")
        self.processed_files = self.load_processed_files()
        self.lemmatizer = WordNetLemmatizer()
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Predefined subreddit-style categories
        self.subreddit_categories = [
            "technology", "science", "programming", "gaming", "movies", 
            "books", "music", "sports", "cooking", "travel", "fitness", 
            "photography", "art", "business", "education", "health", 
            "politics", "history", "philosophy", "psychology"
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
    
    def clean_text(self, text):
        """Clean and preprocess text for analysis"""
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_keywords(self, text, num_keywords=10):
        """Extract top keywords from text using TF-IDF"""
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text.strip():
            return []
        
        # Use TF-IDF to find important words
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform([cleaned_text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [keyword for keyword, score in keyword_scores[:num_keywords]]
        except:
            # Fallback to simple word frequency
            words = cleaned_text.split()
            word_freq = Counter(words)
            return [word for word, freq in word_freq.most_common(num_keywords)]
    
    def categorize_content(self, text, keywords):
        """Determine the best subreddit-style category for the content"""
        text_lower = text.lower()
        keyword_text = ' '.join(keywords).lower()
        combined_text = text_lower + ' ' + keyword_text
        
        # Score each category based on keyword matches
        category_scores = {}
        
        for category in self.subreddit_categories:
            score = 0
            
            # Direct category name match
            if category in combined_text:
                score += 10
            
            # Category-specific keyword matching
            category_keywords = self.get_category_keywords(category)
            for keyword in category_keywords:
                if keyword in combined_text:
                    score += 5
            
            # Check extracted keywords for category relevance
            for extracted_keyword in keywords:
                if any(cat_keyword in extracted_keyword or extracted_keyword in cat_keyword 
                      for cat_keyword in category_keywords):
                    score += 3
            
            category_scores[category] = score
        
        # Return category with highest score, or 'miscellaneous' if no good match
        best_category = max(category_scores, key=category_scores.get)
        if category_scores[best_category] > 0:
            return best_category
        else:
            return "miscellaneous"
    
    def get_category_keywords(self, category):
        """Get relevant keywords for each category"""
        category_map = {
            "technology": ["tech", "software", "hardware", "computer", "digital", "internet", "ai", "machine learning"],
            "science": ["research", "study", "experiment", "theory", "discovery", "scientific", "biology", "chemistry", "physics"],
            "programming": ["code", "coding", "developer", "programming", "software", "algorithm", "python", "javascript"],
            "gaming": ["game", "gaming", "player", "video game", "console", "pc gaming", "esports"],
            "movies": ["film", "movie", "cinema", "director", "actor", "hollywood", "entertainment"],
            "books": ["book", "reading", "author", "novel", "literature", "writing", "story"],
            "music": ["song", "music", "artist", "album", "concert", "band", "musician"],
            "sports": ["sport", "team", "player", "game", "match", "competition", "athletic"],
            "cooking": ["recipe", "food", "cooking", "kitchen", "ingredient", "meal", "chef"],
            "travel": ["travel", "trip", "vacation", "destination", "tourism", "journey"],
            "fitness": ["workout", "exercise", "fitness", "gym", "health", "training"],
            "photography": ["photo", "camera", "photography", "picture", "image", "lens"],
            "art": ["art", "artist", "painting", "drawing", "creative", "design"],
            "business": ["business", "company", "market", "finance", "economy", "corporate"],
            "education": ["education", "school", "learning", "student", "teacher", "academic"],
            "health": ["health", "medical", "doctor", "medicine", "wellness", "healthcare"],
            "politics": ["politics", "government", "election", "policy", "political"],
            "history": ["history", "historical", "past", "ancient", "war", "civilization"],
            "philosophy": ["philosophy", "philosophical", "ethics", "moral", "existence"],
            "psychology": ["psychology", "mental", "behavior", "mind", "cognitive"]
        }
        return category_map.get(category, [])
    
    def create_folder_structure(self):
        """Create the folder structure for organizing files"""
        base_organized_folder = self.source_folder / "organized"
        base_organized_folder.mkdir(exist_ok=True)
        
        # Create category folders
        for category in self.subreddit_categories + ["miscellaneous"]:
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
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                print(f"Empty file skipped: {file_path}")
                return
            
            # Extract keywords
            keywords = self.extract_keywords(content)
            print(f"Keywords: {keywords}")
            
            # Categorize content
            category = self.categorize_content(content, keywords)
            print(f"Category: {category}")
            
            # Create organized folder structure
            organized_folder = self.create_folder_structure()
            
            # Move file to appropriate category folder
            category_folder = organized_folder / category
            new_file_path = category_folder / file_path.name
            
            # Handle duplicate names
            counter = 1
            while new_file_path.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                new_file_path = category_folder / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            shutil.copy2(file_path, new_file_path)
            
            # Create metadata file with keywords
            metadata_file = new_file_path.with_suffix('.metadata.json')
            metadata = {
                "original_path": str(file_path),
                "processed_date": datetime.now().isoformat(),
                "keywords": keywords,
                "category": category,
                "file_size": file_path.stat().st_size
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Log as processed
            self.save_processed_file(str(file_path))
            
            print(f"File organized: {file_path} -> {new_file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def process_existing_files(self):
        """Process all existing txt files in the source folder"""
        print(f"Scanning for txt files in: {self.source_folder}")
        
        txt_files = list(self.source_folder.glob("*.txt"))
        print(f"Found {len(txt_files)} txt files")
        
        for file_path in txt_files:
            if str(file_path) not in self.processed_files:
                self.process_single_file(file_path)
    
    def start_monitoring(self):
        """Start monitoring the folder for new txt files"""
        print(f"Starting to monitor: {self.source_folder}")
        
        event_handler = TextFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.source_folder), recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nMonitoring stopped.")
        
        observer.join()

def main():
    # Get source folder from user or use current directory
    source_folder = input("Enter the path to the folder containing txt files (or press Enter for current directory): ").strip()
    
    if not source_folder:
        source_folder = "."
    
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Folder '{source_folder}' does not exist.")
        return
    
    print(f"Text File Organizer starting...")
    print(f"Source folder: {source_path.absolute()}")
    
    organizer = TextOrganizer(source_path)
    
    # Process existing files first
    organizer.process_existing_files()
    
    print("\nInitial processing complete!")
    print("Now monitoring for new txt files...")
    print("Press Ctrl+C to stop monitoring.")
    
    # Start monitoring for new files
    organizer.start_monitoring()

if __name__ == "__main__":
    main()
