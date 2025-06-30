import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading

class TextFileRenamer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text File Renamer")
        self.root.geometry("800x600")
        
        self.selected_folder = None
        self.files_to_process = []
        
        self.create_interface()
        
    def create_interface(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Folder selection
        ttk.Label(main_frame, text="Select Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_label = ttk.Label(main_frame, text="No folder selected", relief="sunken")
        self.folder_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        ttk.Button(main_frame, text="Browse", command=self.select_folder).grid(row=0, column=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Renaming Options", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.max_length_var = tk.IntVar(value=50)
        ttk.Label(options_frame, text="Max filename length:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(options_frame, from_=20, to=100, textvariable=self.max_length_var, width=10).grid(row=0, column=1, sticky=tk.W)
        
        self.include_date_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Include date in filename", variable=self.include_date_var).grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        self.preview_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Preview changes before renaming", variable=self.preview_var).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # File list frame
        list_frame = ttk.LabelFrame(main_frame, text="Files to Process", padding="10")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create treeview for file list
        self.tree = ttk.Treeview(list_frame, columns=("current", "new"), show="tree headings", height=15)
        self.tree.heading("#0", text="Status")
        self.tree.heading("current", text="Current Name")
        self.tree.heading("new", text="New Name")
        self.tree.column("#0", width=100)
        self.tree.column("current", width=300)
        self.tree.column("new", width=300)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Scan Files", command=self.scan_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rename Files", command=self.rename_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing text files")
        if folder:
            self.selected_folder = Path(folder)
            self.folder_label.config(text=str(self.selected_folder))
            self.clear_list()
            
    def clear_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.files_to_process = []
        
    def extract_title_from_content(self, file_path):
        """Extract a suitable title from the text file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Clean the content
            content = content.strip()
            if not content:
                return None
                
            # Try to find a title-like line
            lines = content.split('\n')
            
            # Look for common title patterns
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line looks like a title
                if (len(line) > 5 and len(line) < 100 and
                    not line.endswith('.') and
                    not line.endswith(',') and
                    line[0].isupper()):
                    return self.clean_filename(line)
                    
            # If no title found, use first meaningful line
            for line in lines:
                line = line.strip()
                if len(line) > 10:
                    return self.clean_filename(line)
                    
            # Last resort: use first few words
            words = content.split()[:10]
            if words:
                return self.clean_filename(' '.join(words))
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return None
        
    def clean_filename(self, text):
        """Clean text to make it suitable as a filename"""
        # Remove invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing spaces and dots
        text = text.strip(' .')
        
        # Limit length
        max_length = self.max_length_var.get()
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0]  # Cut at word boundary
            
        # Ensure filename is not empty
        if not text:
            text = "untitled"
            
        return text
        
    def scan_files(self):
        if not self.selected_folder:
            messagebox.showwarning("No Folder", "Please select a folder first")
            return
            
        self.clear_list()
        
        # Find all text files
        text_extensions = ['.txt', '.text', '.md', '.log']
        
        for file_path in self.selected_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                new_name = self.extract_title_from_content(file_path)
                
                if new_name and new_name != file_path.stem:
                    # Add date if requested
                    if self.include_date_var.get():
                        from datetime import datetime
                        date_str = datetime.now().strftime("%Y%m%d_")
                        new_name = date_str + new_name
                        
                    # Keep original extension
                    new_filename = new_name + file_path.suffix
                    
                    # Check if new name already exists
                    new_path = file_path.parent / new_filename
                    if new_path.exists():
                        # Add number to make unique
                        counter = 1
                        while new_path.exists():
                            new_filename = f"{new_name}_{counter}{file_path.suffix}"
                            new_path = file_path.parent / new_filename
                            counter += 1
                            
                    # Add to tree
                    item = self.tree.insert("", "end", text="Ready", 
                                          values=(file_path.name, new_filename))
                    self.files_to_process.append((file_path, new_path, item))
                    
        if not self.files_to_process:
            messagebox.showinfo("No Changes", "No files need renaming or no text files found")
            
    def rename_files(self):
        if not self.files_to_process:
            messagebox.showwarning("No Files", "Please scan files first")
            return
            
        if self.preview_var.get():
            response = messagebox.askyesno("Confirm Rename", 
                                         f"Rename {len(self.files_to_process)} files?")
            if not response:
                return
                
        success_count = 0
        error_count = 0
        
        for old_path, new_path, tree_item in self.files_to_process:
            try:
                old_path.rename(new_path)
                self.tree.item(tree_item, text="✓ Done")
                success_count += 1
            except Exception as e:
                self.tree.item(tree_item, text="✗ Error")
                error_count += 1
                print(f"Error renaming {old_path}: {e}")
                
        messagebox.showinfo("Complete", 
                          f"Renaming complete!\nSuccess: {success_count}\nErrors: {error_count}")
        
        # Clear the processed files
        self.files_to_process = []
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TextFileRenamer()
    app.run()
