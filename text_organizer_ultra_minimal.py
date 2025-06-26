import os
from datetime import datetime
import json

class UltraMinimalTextOrganizer:
    def __init__(self, source_folder):
        self.source_folder = source_folder
        self.log_file = "processed_files.log"
        self.processed_files = self.load_processed_files()
        
        # Simple categories
        self.categories = [
            "technology", "science", "programming", "gaming", "movies", 
            "books", "music", "sports", "cooking", "travel", "fitness", 
            "photography", "art", "business", "education", "health", 
            "politics", "history", "philosophy", "psychology", "miscellaneous"
        ]
    
    def load_processed_files(self):
        """Load list of already processed files from log"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return set(line.strip() for line in f if line.strip())
        except:
            pass
        return set()
    
    def save_processed_file(self, file_path):
        """Add file to processed log"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{file_path}\n")
            self.processed_files.add(str(file_path))
        except:
            pass
    
    def extract_simple_keywords(self, text, num_keywords=10):
        """Extract keywords using very simple word frequency without any imports"""
        # Convert to lowercase and split on common separators
        text = text.lower()
        
        # Manual character filtering - replace non-letters with spaces
        clean_chars = []
        for char in text:
            if char.isalpha() or char.isspace():
                clean_chars.append(char)
            else:
                clean_chars.append(' ')
        
        clean_text = ''.join(clean_chars)
        words = clean_text.split()
        
        # Simple stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Filter words and count frequency
        word_count = {}
        for word in words:
            if len(word) > 2 and word not in stopwords:
                word_count[word] = word_count.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:num_keywords]]
    
    def categorize_simple(self, text, keywords):
        """Simple categorization based on keyword matching"""
        text_lower = text.lower()
        keyword_text = ' '.join(keywords).lower()
        combined_text = text_lower + ' ' + keyword_text
        
        category_keywords = {
            "technology": ["tech", "software", "computer", "digital", "internet", "ai"],
            "science": ["research", "study", "experiment", "scientific", "biology", "chemistry", "physics"],
            "programming": ["code", "coding", "developer", "programming", "python", "javascript"],
            "gaming": ["game", "gaming", "player", "video", "console"],
            "movies": ["film", "movie", "cinema", "director", "actor"],
            "books": ["book", "reading", "author", "novel", "literature"],
            "music": ["song", "music", "artist", "album", "band"],
            "sports": ["sport", "team", "player", "match"],
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
            score = 0
            for keyword in cat_keywords:
                if keyword in combined_text:
                    score += 1
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def create_folder_structure(self):
        """Create the folder structure for organizing files"""
        organized_folder = os.path.join(self.source_folder, "organized")
        try:
            if not os.path.exists(organized_folder):
                os.makedirs(organized_folder)
            
            for category in self.categories:
                category_folder = os.path.join(organized_folder, category)
                if not os.path.exists(category_folder):
                    os.makedirs(category_folder)
        except Exception as e:
            print(f"Error creating folders: {e}")
        
        return organized_folder
    
    def copy_file(self, src, dst):
        """Manual file copy without using shutil"""
        try:
            with open(src, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    while True:
                        chunk = fsrc.read(8192)
                        if not chunk:
                            break
                        fdst.write(chunk)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    def get_file_stem_and_suffix(self, file_path):
        """Get file stem and suffix without pathlib"""
        base_name = os.path.basename(file_path)
        if '.' in base_name:
            stem = base_name.rsplit('.', 1)[0]
            suffix = '.' + base_name.rsplit('.', 1)[1]
        else:
            stem = base_name
            suffix = ''
        return stem, suffix
    
    def process_single_file(self, file_path):
        """Process a single text file"""
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
            category_folder = os.path.join(organized_folder, category)
            
            file_name = os.path.basename(file_path)
            new_file_path = os.path.join(category_folder, file_name)
            
            # Handle duplicate names
            counter = 1
            while os.path.exists(new_file_path):
                stem, suffix = self.get_file_stem_and_suffix(file_path)
                new_file_name = f"{stem}_{counter}{suffix}"
                new_file_path = os.path.join(category_folder, new_file_name)
                counter += 1
            
            # Copy file manually
            if self.copy_file(file_path, new_file_path):
                # Create metadata file
                metadata = {
                    "original_path": str(file_path),
                    "processed_date": datetime.now().isoformat(),
                    "keywords": keywords,
                    "category": category,
                    "file_size": os.path.getsize(file_path)
                }
                
                metadata_file = new_file_path + '.metadata.json'
                try:
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2)
                except:
                    pass
                
                self.save_processed_file(str(file_path))
                print(f"File organized: {file_path} -> {new_file_path}")
            else:
                print(f"Failed to copy file: {file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def process_existing_files(self):
        """Process all existing txt files"""
        print(f"Scanning for txt files in: {self.source_folder}")
        
        try:
            txt_files = []
            for item in os.listdir(self.source_folder):
                item_path = os.path.join(self.source_folder, item)
                if os.path.isfile(item_path) and item.lower().endswith('.txt'):
                    txt_files.append(item_path)
            
            print(f"Found {len(txt_files)} txt files")
            
            for file_path in txt_files:
                if str(file_path) not in self.processed_files:
                    self.process_single_file(file_path)
        except Exception as e:
            print(f"Error scanning files: {e}")

def main():
    print("Ultra Minimal Text File Organizer (No Dependencies)")
    print("=" * 55)
    
    try:
        source_folder = input("Enter the path to the folder containing txt files (or press Enter for current directory): ").strip()
        
        if not source_folder:
            source_folder = "."
        
        if not os.path.exists(source_folder):
            print(f"Error: Folder '{source_folder}' does not exist.")
            return
        
        print(f"Source folder: {os.path.abspath(source_folder)}")
        
        organizer = UltraMinimalTextOrganizer(source_folder)
        organizer.process_existing_files()
        
        print("\nProcessing complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
