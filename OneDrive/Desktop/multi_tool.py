import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
import subprocess
import json
from PIL import Image, ImageTk
import pytesseract
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd
import eyed3
from mutagen.mp4 import MP4
import cv2
import numpy as np

class MultiToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Use File Organizer Tool")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.monitoring = False
        self.observer = None
        self.log_text = None
        
        # Create main interface
        self.create_interface()
        
    def create_interface(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # File Organizer Tab
        self.create_file_organizer_tab(notebook)
        
        # Image OCR Tab
        self.create_image_ocr_tab(notebook)
        
        # Audio Monitor Tab
        self.create_audio_monitor_tab(notebook)
        
        # Image Processing Tab
        self.create_image_processing_tab(notebook)
        
        # M4A Converter Tab
        self.create_m4a_converter_tab(notebook)
        
        # Data Analysis Tab
        self.create_data_analysis_tab(notebook)
        
        # Log Tab
        self.create_log_tab(notebook)
        
    def create_file_organizer_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="File Organizer")
        
        # Source directory selection
        ttk.Label(frame, text="Source Directory:").pack(pady=5)
        self.source_dir_var = tk.StringVar()
        source_frame = ttk.Frame(frame)
        source_frame.pack(fill='x', padx=10, pady=5)
        ttk.Entry(source_frame, textvariable=self.source_dir_var).pack(side='left', fill='x', expand=True)
        ttk.Button(source_frame, text="Browse", command=self.browse_source_dir).pack(side='right')
        
        # Destination directory selection
        ttk.Label(frame, text="Destination Directory:").pack(pady=5)
        self.dest_dir_var = tk.StringVar()
        dest_frame = ttk.Frame(frame)
        dest_frame.pack(fill='x', padx=10, pady=5)
        ttk.Entry(dest_frame, textvariable=self.dest_dir_var).pack(side='left', fill='x', expand=True)
        ttk.Button(dest_frame, text="Browse", command=self.browse_dest_dir).pack(side='right')
        
        # Options
        options_frame = ttk.LabelFrame(frame, text="Options")
        options_frame.pack(fill='x', padx=10, pady=10)
        
        self.organize_by_date = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Organize by date", variable=self.organize_by_date).pack(anchor='w')
        
        self.organize_by_type = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Organize by file type", variable=self.organize_by_type).pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Organize Files", command=self.organize_files).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Start Monitoring", command=self.start_file_monitoring).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop Monitoring", command=self.stop_file_monitoring).pack(side='left', padx=5)
        
    def create_image_ocr_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Image OCR")
        
        # Directory selection
        ttk.Label(frame, text="Monitor Directory:").pack(pady=5)
        self.ocr_dir_var = tk.StringVar()
        ocr_frame = ttk.Frame(frame)
        ocr_frame.pack(fill='x', padx=10, pady=5)
        ttk.Entry(ocr_frame, textvariable=self.ocr_dir_var).pack(side='left', fill='x', expand=True)
        ttk.Button(ocr_frame, text="Browse", command=self.browse_ocr_dir).pack(side='right')
        
        # OCR Options
        ocr_options_frame = ttk.LabelFrame(frame, text="OCR Options")
        ocr_options_frame.pack(fill='x', padx=10, pady=10)
        
        self.auto_ocr = tk.BooleanVar(value=True)
        ttk.Checkbutton(ocr_options_frame, text="Auto OCR on new images", variable=self.auto_ocr).pack(anchor='w')
        
        self.save_ocr_text = tk.BooleanVar(value=True)
        ttk.Checkbutton(ocr_options_frame, text="Save OCR text to file", variable=self.save_ocr_text).pack(anchor='w')
        
        # Manual OCR
        manual_frame = ttk.LabelFrame(frame, text="Manual OCR")
        manual_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(manual_frame, text="Select Image for OCR", command=self.manual_ocr).pack(pady=5)
        
        # OCR Results
        results_frame = ttk.LabelFrame(frame, text="OCR Results")
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.ocr_results = scrolledtext.ScrolledText(results_frame, height=10)
        self.ocr_results.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Start OCR Monitoring", command=self.start_ocr_monitoring).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop OCR Monitoring", command=self.stop_ocr_monitoring).pack(side='left', padx=5)
        
    def create_audio_monitor_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Audio Monitor")
        
        # Directory selection
        ttk.Label(frame, text="Audio Directory:").pack(pady=5)
        self.audio_dir_var = tk.StringVar()
        audio_frame = ttk.Frame(frame)
        audio_frame.pack(fill='x', padx=10, pady=5)
        ttk.Entry(audio_frame, textvariable=self.audio_dir_var).pack(side='left', fill='x', expand=True)
        ttk.Button(audio_frame, text="Browse", command=self.browse_audio_dir).pack(side='right')
        
        # Audio processing options
        audio_options_frame = ttk.LabelFrame(frame, text="Audio Processing Options")
        audio_options_frame.pack(fill='x', padx=10, pady=10)
        
        self.extract_metadata = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_options_frame, text="Extract metadata", variable=self.extract_metadata).pack(anchor='w')
        
        self.organize_by_artist = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_options_frame, text="Organize by artist", variable=self.organize_by_artist).pack(anchor='w')
        
        self.organize_by_album = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_options_frame, text="Organize by album", variable=self.organize_by_album).pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Process Audio Files", command=self.process_audio_files).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Start Audio Monitoring", command=self.start_audio_monitoring).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop Audio Monitoring", command=self.stop_audio_monitoring).pack(side='left', padx=5)
        
    def create_image_processing_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Image Processing")
        
        # Directory selection
        ttk.Label(frame, text="Image Directory:").pack(pady=5)
        self.image_dir_var = tk.StringVar()
        image_frame = ttk.Frame(frame)
        image_frame.pack(fill='x', padx=10, pady=5)
        ttk.Entry(image_frame, textvariable=self.image_dir_var).pack(side='left', fill='x', expand=True)
        ttk.Button(image_frame, text="Browse", command=self.browse_image_dir).pack(side='right')
        
        # Image processing options
        image_options_frame = ttk.LabelFrame(frame, text="Image Processing Options")
        image_options_frame.pack(fill='x', padx=10, pady=10)
        
        self.resize_images = tk.BooleanVar()
        ttk.Checkbutton(image_options_frame, text="Resize images", variable=self.resize_images).pack(anchor='w')
        
        self.convert_format = tk.BooleanVar()
        ttk.Checkbutton(image_options_frame, text="Convert format", variable=self.convert_format).pack(anchor='w')
        
        self.extract_exif = tk.BooleanVar(value=True)
        ttk.Checkbutton(image_options_frame, text="Extract EXIF data", variable=self.extract_exif).pack(anchor='w')
        
        # Format selection
        format_frame = ttk.Frame(image_options_frame)
        format_frame.pack(fill='x', pady=5)
        ttk.Label(format_frame, text="Target format:").pack(side='left')
        self.target_format = ttk.Combobox(format_frame, values=['JPEG', 'PNG', 'WEBP', 'BMP'])
        self.target_format.pack(side='left', padx=5)
        self.target_format.set('JPEG')
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Process Images", command=self.process_images).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Batch Resize", command=self.batch_resize_images).pack(side='left', padx=5)
        
    def create_m4a_converter_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="M4A Converter")
        
        # File selection
        ttk.Label(frame, text="M4A Files Directory:").pack(pady=5)
        self.m4a_dir_var = tk.StringVar()
        m4a_frame = ttk.Frame(frame)
        m4a_frame.pack(fill='x', padx=10, pady=5)
        ttk.Entry(m4a_frame, textvariable=self.m4a_dir_var).pack(side='left', fill='x', expand=True)
        ttk.Button(m4a_frame, text="Browse", command=self.browse_m4a_dir).pack(side='right')
        
        # Conversion options
        conv_options_frame = ttk.LabelFrame(frame, text="Conversion Options")
        conv_options_frame.pack(fill='x', padx=10, pady=10)
        
        format_frame = ttk.Frame(conv_options_frame)
        format_frame.pack(fill='x', pady=5)
        ttk.Label(format_frame, text="Convert to:").pack(side='left')
        self.conv_format = ttk.Combobox(format_frame, values=['MP3', 'WAV', 'FLAC', 'OGG'])
        self.conv_format.pack(side='left', padx=5)
        self.conv_format.set('MP3')
        
        quality_frame = ttk.Frame(conv_options_frame)
        quality_frame.pack(fill='x', pady=5)
        ttk.Label(quality_frame, text="Quality:").pack(side='left')
        self.quality = ttk.Combobox(quality_frame, values=['128k', '192k', '256k', '320k'])
        self.quality.pack(side='left', padx=5)
        self.quality.set('192k')
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Convert M4A Files", command=self.convert_m4a_files).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Batch Convert", command=self.batch_convert_m4a).pack(side='left', padx=5)
        
    def create_data_analysis_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Data Analysis")
        
        # File selection
        ttk.Label(frame, text="Data File:").pack(pady=5)
        self.data_file_var = tk.StringVar()
        data_frame = ttk.Frame(frame)
        data_frame.pack(fill='x', padx=10, pady=5)
        ttk.Entry(data_frame, textvariable=self.data_file_var).pack(side='left', fill='x', expand=True)
        ttk.Button(data_frame, text="Browse", command=self.browse_data_file).pack(side='right')
        
        # Analysis options
        analysis_frame = ttk.LabelFrame(frame, text="Analysis Options")
        analysis_frame.pack(fill='x', padx=10, pady=10)
        
        self.show_info = tk.BooleanVar(value=True)
        ttk.Checkbutton(analysis_frame, text="Show data info", variable=self.show_info).pack(anchor='w')
        
        self.show_stats = tk.BooleanVar(value=True)
        ttk.Checkbutton(analysis_frame, text="Show statistics", variable=self.show_stats).pack(anchor='w')
        
        self.show_head = tk.BooleanVar(value=True)
        ttk.Checkbutton(analysis_frame, text="Show first 5 rows", variable=self.show_head).pack(anchor='w')
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="Analysis Results")
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.analysis_results = scrolledtext.ScrolledText(results_frame, height=15)
        self.analysis_results.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Analyze Data", command=self.analyze_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export Report", command=self.export_analysis_report).pack(side='left', padx=5)
        
    def create_log_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Log")
        
        # Log area
        log_frame = ttk.LabelFrame(frame, text="Activity Log")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Log controls
        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=10)
        ttk.Button(control_frame, text="Clear Log", command=self.clear_log).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Save Log", command=self.save_log).pack(side='left', padx=5)
        
    def log_message(self, message):
        """Add message to log with timestamp"""
        if self.log_text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
    
    # Browse methods
    def browse_source_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dir_var.set(directory)
    
    def browse_dest_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dest_dir_var.set(directory)
    
    def browse_ocr_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.ocr_dir_var.set(directory)
    
    def browse_audio_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.audio_dir_var.set(directory)
    
    def browse_image_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.image_dir_var.set(directory)
    
    def browse_m4a_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.m4a_dir_var.set(directory)
    
    def browse_data_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.data_file_var.set(file_path)
    
    # File organization methods
    def organize_files(self):
        """Organize files based on selected options"""
        source_dir = self.source_dir_var.get()
        dest_dir = self.dest_dir_var.get()
        
        if not source_dir or not dest_dir:
            messagebox.showerror("Error", "Please select both source and destination directories")
            return
        
        try:
            self.log_message("Starting file organization...")
            
            file_types = {
                'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
                'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
                'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
                'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
                'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'Executables': ['.exe', '.msi', '.deb', '.dmg']
            }
            
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file).suffix.lower()
                    
                    # Determine file category
                    category = 'Others'
                    for cat, extensions in file_types.items():
                        if file_ext in extensions:
                            category = cat
                            break
                    
                    # Create destination path
                    dest_path = dest_dir
                    
                    if self.organize_by_type.get():
                        dest_path = os.path.join(dest_path, category)
                    
                    if self.organize_by_date.get():
                        file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                        date_folder = file_date.strftime("%Y-%m")
                        dest_path = os.path.join(dest_path, date_folder)
                    
                    # Create directories if they don't exist
                    os.makedirs(dest_path, exist_ok=True)
                    
                    # Move file
                    dest_file_path = os.path.join(dest_path, file)
                    if not os.path.exists(dest_file_path):
                        shutil.move(file_path, dest_file_path)
                        self.log_message(f"Moved: {file} -> {dest_path}")
                    else:
                        self.log_message(f"Skipped (exists): {file}")
            
            self.log_message("File organization completed!")
            messagebox.showinfo("Success", "File organization completed!")
            
        except Exception as e:
            self.log_message(f"Error during file organization: {str(e)}")
            messagebox.showerror("Error", f"Error during file organization: {str(e)}")
    
    def start_file_monitoring(self):
        """Start monitoring for new files"""
        source_dir = self.source_dir_var.get()
        if not source_dir:
            messagebox.showerror("Error", "Please select a source directory")
            return
        
        self.monitoring = True
        self.log_message("Started file monitoring...")
        
        # Implementation would use watchdog observer
        # This is a simplified version
        threading.Thread(target=self._monitor_files, daemon=True).start()
    
    def stop_file_monitoring(self):
        """Stop file monitoring"""
        self.monitoring = False
        self.log_message("Stopped file monitoring")
    
    def _monitor_files(self):
        """Monitor files in background thread"""
        while self.monitoring:
            time.sleep(5)  # Check every 5 seconds
            # Implementation would check for new files and organize them
    
    # OCR methods
    def start_ocr_monitoring(self):
        """Start OCR monitoring"""
        ocr_dir = self.ocr_dir_var.get()
        if not ocr_dir:
            messagebox.showerror("Error", "Please select a directory to monitor")
            return
        
        self.log_message("Started OCR monitoring...")
        threading.Thread(target=self._monitor_ocr, daemon=True).start()
    
    def stop_ocr_monitoring(self):
        """Stop OCR monitoring"""
        self.monitoring = False
        self.log_message("Stopped OCR monitoring")
    
    def _monitor_ocr(self):
        """Monitor for new images and perform OCR"""
        # Implementation would use watchdog to monitor for new image files
        pass
    
    def manual_ocr(self):
        """Perform OCR on selected image"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")]
        )
        if file_path:
            try:
                # Perform OCR
                text = pytesseract.image_to_string(Image.open(file_path))
                self.ocr_results.delete(1.0, tk.END)
                self.ocr_results.insert(1.0, text)
                self.log_message(f"OCR completed for: {os.path.basename(file_path)}")
                
                if self.save_ocr_text.get():
                    text_file = file_path + "_ocr.txt"
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    self.log_message(f"OCR text saved to: {text_file}")
                    
            except Exception as e:
                self.log_message(f"OCR error: {str(e)}")
                messagebox.showerror("OCR Error", f"Error performing OCR: {str(e)}")
    
    # Audio processing methods
    def process_audio_files(self):
        """Process audio files in selected directory"""
        audio_dir = self.audio_dir_var.get()
        if not audio_dir:
            messagebox.showerror("Error", "Please select an audio directory")
            return
        
        try:
            self.log_message("Processing audio files...")
            
            for root, dirs, files in os.walk(audio_dir):
                for file in files:
                    if file.lower().endswith(('.mp3', '.m4a', '.wav', '.flac')):
                        file_path = os.path.join(root, file)
                        self._process_audio_file(file_path)
            
            self.log_message("Audio processing completed!")
            messagebox.showinfo("Success", "Audio processing completed!")
            
        except Exception as e:
            self.log_message(f"Error processing audio files: {str(e)}")
            messagebox.showerror("Error", f"Error processing audio files: {str(e)}")
    
    def _process_audio_file(self, file_path):
        """Process individual audio file"""
        try:
            if file_path.lower().endswith('.mp3'):
                audiofile = eyed3.load(file_path)
                if audiofile.tag:
                    artist = audiofile.tag.artist or "Unknown Artist"
                    album = audiofile.tag.album or "Unknown Album"
                    title = audiofile.tag.title or os.path.basename(file_path)
                    
                    self.log_message(f"Processed: {title} by {artist}")
                    
                    # Organize by artist/album if selected
                    if self.organize_by_artist.get() or self.organize_by_album.get():
                        self._organize_audio_file(file_path, artist, album)
                        
        except Exception as e:
            self.log_message(f"Error processing {file_path}: {str(e)}")
    
    def _organize_audio_file(self, file_path, artist, album):
        """Organize audio file by artist/album"""
        base_dir = os.path.dirname(file_path)
        
        if self.organize_by_artist.get():
            artist_dir = os.path.join(base_dir, "Organized", artist)
            if self.organize_by_album.get():
                dest_dir = os.path.join(artist_dir, album)
            else:
                dest_dir = artist_dir
        else:
            dest_dir = os.path.join(base_dir, "Organized", album)
        
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
        
        if not os.path.exists(dest_path):
            shutil.move(file_path, dest_path)
            self.log_message(f"Moved audio file to: {dest_path}")
    
    def start_audio_monitoring(self):
        """Start audio monitoring"""
        self.log_message("Started audio monitoring...")
        # Implementation would monitor for new audio files
    
    def stop_audio_monitoring(self):
        """Stop audio monitoring"""
        self.log_message("Stopped audio monitoring")
    
    # Image processing methods
    def process_images(self):
        """Process images in selected directory"""
        image_dir = self.image_dir_var.get()
        if not image_dir:
            messagebox.showerror("Error", "Please select an image directory")
            return
        
        try:
            self.log_message("Processing images...")
            
            for root, dirs, files in os.walk(image_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')):
                        file_path = os.path.join(root, file)
                        self._process_image_file(file_path)
            
            self.log_message("Image processing completed!")
            messagebox.showinfo("Success", "Image processing completed!")
            
        except Exception as e:
            self.log_message(f"Error processing images: {str(e)}")
            messagebox.showerror("Error", f"Error processing images: {str(e)}")
    
    def _process_image_file(self, file_path):
        """Process individual image file"""
        try:
            with Image.open(file_path) as img:
                # Extract EXIF data if requested
                if self.extract_exif.get():
                    exif_data = img._getexif()
                    if exif_data:
                        self.log_message(f"EXIF data extracted for: {os.path.basename(file_path)}")
                
                # Convert format if requested
                if self.convert_format.get():
                    target_format = self.target_format.get()
                    if target_format and img.format != target_format:
                        new_path = os.path.splitext(file_path)[0] + f".{target_format.lower()}"
                        img.save(new_path, target_format)
                        self.log_message(f"Converted {file_path} to {target_format}")
                
                # Resize if requested
                if self.resize_images.get():
                    # Default resize to 1920x1080 max
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    img.save(file_path)
                    self.log_message(f"Resized: {os.path.basename(file_path)}")
                    
        except Exception as e:
            self.log_message(f"Error processing image {file_path}: {str(e)}")
    
    def batch_resize_images(self):
        """Batch resize images"""
        image_dir = self.image_dir_var.get()
        if not image_dir:
            messagebox.showerror("Error", "Please select an image directory")
            return
        
        # Get resize dimensions from user
        width = tk.simpledialog.askinteger("Resize", "Enter width:", initialvalue=1920)
        height = tk.simpledialog.askinteger("Resize", "Enter height:", initialvalue=1080)
        
        if width and height:
            try:
                self.log_message(f"Batch resizing images to {width}x{height}...")
                
                for root, dirs, files in os.walk(image_dir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                            file_path = os.path.join(root, file)
                            with Image.open(file_path) as img:
                                img.thumbnail((width, height), Image.Resampling.LANCZOS)
                                img.save(file_path)
                                self.log_message(f"Resized: {os.path.basename(file_path)}")
                
                self.log_message("Batch resize completed!")
                messagebox.showinfo("Success", "Batch resize completed!")
                
            except Exception as e:
                self.log_message(f"Error during batch resize: {str(e)}")
                messagebox.showerror("Error", f"Error during batch resize: {str(e)}")
    
    # M4A conversion methods
    def convert_m4a_files(self):
        """Convert M4A files to selected format"""
        m4a_dir = self.m4a_dir_var.get()
        if not m4a_dir:
            messagebox.showerror("Error", "Please select M4A directory")
            return
        
        target_format = self.conv_format.get().lower()
        quality = self.quality.get()
        
        try:
            self.log_message(f"Converting M4A files to {target_format.upper()}...")
            
            for root, dirs, files in os.walk(m4a_dir):
                for file in files:
                    if file.lower().endswith('.m4a'):
                        file_path = os.path.join(root, file)
                        self._convert_m4a_file(file_path, target_format, quality)
            
            self.log_message("M4A conversion completed!")
            messagebox.showinfo("Success", "M4A conversion completed!")
            
        except Exception as e:
            self.log_message(f"Error converting M4A files: {str(e)}")
            messagebox.showerror("Error", f"Error converting M4A files: {str(e)}")
    
    def _convert_m4a_file(self, file_path, target_format, quality):
        """Convert individual M4A file"""
        try:
            output_path = os.path.splitext(file_path)[0] + f".{target_format}"
            
            # Use ffmpeg for conversion
            cmd = [
                'ffmpeg', '-i', file_path,
                '-b:a', quality,
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_message(f"Converted: {os.path.basename(file_path)} -> {target_format.upper()}")
            else:
                self.log_message(f"Conversion failed for: {os.path.basename(file_path)}")
                
        except Exception as e:
            self.log_message(f"Error converting {file_path}: {str(e)}")
    
    def batch_convert_m4a(self):
        """Batch convert all M4A files"""
        self.convert_m4a_files()
    
    # Data analysis methods
    def analyze_data(self):
        """Analyze data file"""
        data_file = self.data_file_var.get()
        if not data_file:
            messagebox.showerror("Error", "Please select a data file")
            return
        
        try:
            self.log_message("Analyzing data file...")
            
            # Load data based on file extension
            if data_file.lower().endswith('.csv'):
                df = pd.read_csv(data_file)
            elif data_file.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(data_file)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
            
            # Clear previous results
            self.analysis_results.delete(1.0, tk.END)
            
            # Show data info
            if self.show_info.get():
                self.analysis_results.insert(tk.END, "=== DATA INFO ===\n")
                self.analysis_results.insert(tk.END, f"Shape: {df.shape}\n")
                self.analysis_results.insert(tk.END, f"Columns: {list(df.columns)}\n")
                self.analysis_results.insert(tk.END, f"Data types:\n{df.dtypes}\n\n")
            
            # Show statistics
            if self.show_stats.get():
                self.analysis_results.insert(tk.END, "=== STATISTICS ===\n")
                self.analysis_results.insert(tk.END, str(df.describe()))
                self.analysis_results.insert(tk.END, "\n\n")
            
            # Show first 5 rows
            if self.show_head.get():
                self.analysis_results.insert(tk.END, "=== FIRST 5 ROWS ===\n")
                self.analysis_results.insert(tk.END, str(df.head()))
                self.analysis_results.insert(tk.END, "\n\n")
            
            self.log_message("Data analysis completed!")
            
        except Exception as e:
            self.log_message(f"Error analyzing data: {str(e)}")
            messagebox.showerror("Error", f"Error analyzing data: {str(e)}")
    
    def export_analysis_report(self):
        """Export analysis report to file"""
        content = self.analysis_results.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"Analysis report exported to: {file_path}")
                messagebox.showinfo("Success", "Analysis report exported successfully!")
            except Exception as e:
                self.log_message(f"Error exporting report: {str(e)}")
                messagebox.showerror("Error", f"Error exporting report: {str(e)}")
    
    # Log methods
    def clear_log(self):
        """Clear the log"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log to file"""
        if not self.log_text:
            return
        
        content = self.log_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No log content to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", "Log saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving log: {str(e)}")

def main():
    root = tk.Tk()
    app = MultiToolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
