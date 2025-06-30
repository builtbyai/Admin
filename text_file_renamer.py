import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading

class MediaFileRenamer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Media File Renamer")
        self.root.geometry("900x700")
        
        self.selected_text_file = None
        self.rename_mappings = {}
        self.files_to_process = []
        
        self.create_interface()
        
    def create_interface(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text file selection
        ttk.Label(main_frame, text="Select Text File with Rename Instructions:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.file_label = ttk.Label(main_frame, text="No file selected", relief="sunken")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        ttk.Button(main_frame, text="Browse", command=self.select_text_file).grid(row=0, column=2)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.info_text = tk.Text(info_frame, height=5, width=80, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        # File list frame
        list_frame = ttk.LabelFrame(main_frame, text="Media Files to Rename", padding="10")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create treeview for file list
        self.tree = ttk.Treeview(list_frame, columns=("current", "new", "type"), show="tree headings", height=20)
        self.tree.heading("#0", text="Status")
        self.tree.heading("current", text="Original File Name")
        self.tree.heading("new", text="New File Name")
        self.tree.heading("type", text="Type")
        self.tree.column("#0", width=100)
        self.tree.column("current", width=350)
        self.tree.column("new", width=350)
        self.tree.column("type", width=80)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Load Instructions", command=self.load_instructions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Scan Media Files", command=self.scan_media_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rename Files", command=self.rename_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def select_text_file(self):
        file_path = filedialog.askopenfilename(
            title="Select text file with rename instructions",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_text_file = Path(file_path)
            self.file_label.config(text=str(self.selected_text_file))
            self.clear_all()
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"Selected: {self.selected_text_file.name}\nFolder: {self.selected_text_file.parent}")
            
    def clear_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.files_to_process = []
        self.rename_mappings = {}
        
    def load_instructions(self):
        """Load rename instructions from the selected text file"""
        if not self.selected_text_file:
            messagebox.showwarning("No File", "Please select a text file first")
            return
            
        try:
            with open(self.selected_text_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            self.rename_mappings = {}
            lines = content.strip().split('\n')
            
            # Parse the file looking for pairs of lines
            # First line after "Original file name" header is the original name
            # First line after "New file name" header is the new name
            i = 0
            current_original = None
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for headers
                if 'original' in line.lower() and 'file' in line.lower():
                    # Next non-empty line is the original filename
                    i += 1
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    if i < len(lines):
                        current_original = lines[i].strip().strip('"\'')
                elif 'new' in line.lower() and 'file' in line.lower():
                    # Next non-empty line is the new filename
                    i += 1
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    if i < len(lines) and current_original:
                        new_name = lines[i].strip().strip('"\'')
                        self.rename_mappings[current_original.lower()] = new_name
                        current_original = None
                elif line and not line.startswith('#'):
                    # Alternative format: consecutive non-header lines
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith('#'):
                            # Treat as original -> new mapping
                            original = line.strip('"\'')
                            new_name = next_line.strip('"\'')
                            self.rename_mappings[original.lower()] = new_name
                            i += 1  # Skip the next line since we used it
                            
                i += 1
                
            # Update info display
            self.info_text.delete(1.0, tk.END)
            info = f"Loaded {len(self.rename_mappings)} rename instructions from {self.selected_text_file.name}\n\n"
            info += "Mappings found:\n"
            for old, new in list(self.rename_mappings.items())[:10]:  # Show first 10
                info += f"  {old} → {new}\n"
            if len(self.rename_mappings) > 10:
                info += f"  ... and {len(self.rename_mappings) - 10} more"
                
            self.info_text.insert(1.0, info)
            
            if not self.rename_mappings:
                messagebox.showwarning("No Mappings", "No rename mappings found in the file.\n\nExpected format:\noriginal_filename.jpg\nnew_filename.jpg")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")
        
    def scan_media_files(self):
        """Scan for media files in the same folder as the text file"""
        if not self.selected_text_file:
            messagebox.showwarning("No File", "Please select a text file first")
            return
            
        if not self.rename_mappings:
            messagebox.showwarning("No Instructions", "Please load instructions first")
            return
            
        self.clear_all()
        
        # Media file extensions
        media_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',  # Images
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm',  # Videos
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'   # Audio
        ]
        
        folder = self.selected_text_file.parent
        
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                # Check if this file has a rename mapping
                file_name_lower = file_path.name.lower()
                
                if file_name_lower in self.rename_mappings:
                    new_name = self.rename_mappings[file_name_lower]
                    
                    # Preserve the original extension if new name doesn't have one
                    if '.' not in new_name:
                        new_name = new_name + file_path.suffix
                    
                    new_path = file_path.parent / new_name
                    
                    # Check if new name already exists
                    if new_path.exists() and new_path != file_path:
                        # Add number to make unique
                        base_name = new_path.stem
                        extension = new_path.suffix
                        counter = 1
                        while new_path.exists():
                            new_name = f"{base_name}_{counter}{extension}"
                            new_path = file_path.parent / new_name
                            counter += 1
                    
                    # Determine file type
                    file_type = "Image" if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'] else \
                               "Video" if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'] else "Audio"
                    
                    # Add to tree
                    item = self.tree.insert("", "end", text="Ready", 
                                          values=(file_path.name, new_name, file_type))
                    self.files_to_process.append((file_path, new_path, item))
                    
        if not self.files_to_process:
            messagebox.showinfo("No Matches", "No media files found matching the rename instructions")
        else:
            messagebox.showinfo("Scan Complete", f"Found {len(self.files_to_process)} media files to rename")
        
            
    def rename_files(self):
        if not self.files_to_process:
            messagebox.showwarning("No Files", "Please scan media files first")
            return
            
        response = messagebox.askyesno("Confirm Rename", 
                                     f"Rename {len(self.files_to_process)} media files?")
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
    app = MediaFileRenamer()
    app.run()
