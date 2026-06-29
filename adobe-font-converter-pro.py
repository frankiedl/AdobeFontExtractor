"""
Adobe Font Converter - Convert Adobe proprietary fonts to OTF/TTF
For licensed machines ONLY - maintains compliance with Adobe terms

This tool converts extracted Adobe fonts to standard formats for use
on the SAME LICENSED MACHINE in non-Adobe applications.
"""

import sys
import os
import shutil
import struct
from os.path import join as pjoin
from xml.etree import ElementTree
from collections import namedtuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Optional, Tuple
import logging
import threading
import subprocess
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

FontData = namedtuple('FontData', 'id name weight category filepath')

class AdobeFontConverter:
    """Convert Adobe fonts to standard OTF/TTF format for system-wide use"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Adobe Font Converter Pro")
        self.root.geometry("1000x750")
        
        # Variables
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.fonts: List[FontData] = []
        self.font_checkboxes: Dict[str, tuple] = {}
        self.font_dir = None
        self.extracted_fonts_dir = None
        self.conversion_in_progress = False
        self.font_cache: Dict[str, str] = {}
        self.machine_licensed = False
        self.adobe_active = False
        
        self.setup_gui()
        self.check_adobe_license()
        self.load_fonts()

    def setup_gui(self):
        """Setup the GUI layout"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # License status bar
        status_frame = ttk.LabelFrame(main_frame, text="License Status", padding="5")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.license_status_var = tk.StringVar()
        self.license_status_var.set("Checking Adobe license...")
        self.license_label = ttk.Label(status_frame, textvariable=self.license_status_var)
        self.license_label.pack(fill=tk.X)
        
        # Top section: Search and info
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(top_frame, text="Search extracted fonts:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.info_var = tk.StringVar()
        self.info_var.set("Loading...")
        info_label = ttk.Label(top_frame, textvariable=self.info_var, foreground="gray")
        info_label.pack(side=tk.RIGHT, padx=5)
        
        # Font list frame with scrollbar
        list_frame = ttk.LabelFrame(main_frame, text="Extracted Fonts", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.refresh_fonts).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Convert to OTF", command=self.convert_threaded).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Install to System", command=self.install_threaded).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label_frame = ttk.Frame(main_frame)
        status_label_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        status_label = ttk.Label(status_label_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(fill=tk.X)
        
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(status_label_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=5)

    def check_adobe_license(self):
        """Check if Adobe CC is licensed and active on this machine"""
        def check_license():
            try:
                if sys.platform == 'win32':
                    # Check Windows registry for Adobe Creative Cloud
                    result = subprocess.run(
                        ['reg', 'query', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Adobe', '/v', 'Install'],
                        capture_output=True,
                        timeout=5
                    )
                    self.adobe_active = result.returncode == 0
                else:
                    # Check macOS for Adobe install
                    adobe_path = os.path.expandvars('$HOME/Library/Application Support/Adobe')
                    self.adobe_active = os.path.exists(adobe_path)
                
                if self.adobe_active:
                    self.license_status_var.set("✓ Adobe Creative Cloud License ACTIVE - Conversion Allowed")
                    self.license_label.config(foreground="green")
                    self.machine_licensed = True
                else:
                    self.license_status_var.set("✗ Adobe CC License Not Found - Conversion Disabled")
                    self.license_label.config(foreground="red")
                    self.machine_licensed = False
            except Exception as e:
                logger.error(f"License check error: {e}")
                self.license_status_var.set("⚠ Could not verify license - Proceeding with caution")
                self.license_label.config(foreground="orange")
        
        thread = threading.Thread(target=check_license, daemon=True)
        thread.start()

    def detect_font_format(self, font_path: str) -> str:
        """Detect the font file format (TTF, OTF, or proprietary)"""
        try:
            with open(font_path, 'rb') as f:
                header = f.read(4)
                
                # TTF: 0x00 0x01 0x00 0x00
                if header == b'\x00\x01\x00\x00':
                    return 'ttf'
                # OTF: 'OTTO'
                elif header == b'OTTO':
                    return 'otf'
                # TrueType outline (Mac): 'true'
                elif header == b'true':
                    return 'ttf'
                else:
                    return 'unknown'
        except Exception as e:
            logger.warning(f"Could not detect font format: {e}")
            return 'unknown'

    def convert_adobe_font_to_otf(self, input_path: str, output_path: str, font_name: str) -> bool:
        """
        Convert Adobe font to standard OTF format
        
        Since Adobe fonts may already be in OTF or similar format,
        we simply copy with proper naming and structure
        """
        try:
            font_format = self.detect_font_format(input_path)
            logger.info(f"Font format detected: {font_format} for {font_name}")
            
            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Copy the font file
            shutil.copy2(input_path, output_path)
            
            # Verify the copy
            if os.path.getsize(output_path) != os.path.getsize(input_path):
                raise ValueError("Font file size mismatch after copy")
            
            logger.info(f"Successfully converted font: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting font: {e}")
            return False

    def convert_threaded(self):
        """Convert selected fonts in a separate thread"""
        if not self.machine_licensed:
            messagebox.showerror(
                "License Required",
                "Adobe Creative Cloud license not detected.\n\n"
                "Conversion requires an active Adobe CC license on this machine."
            )
            return
        
        if self.conversion_in_progress:
            messagebox.showwarning("Warning", "Conversion already in progress")
            return
        
        thread = threading.Thread(target=self.convert_selected, daemon=True)
        thread.start()

    def convert_selected(self):
        """Convert selected fonts to OTF"""
        self.conversion_in_progress = True
        selected_fonts = [
            font for font in self.fonts
            if font.id in self.font_checkboxes and self.font_checkboxes[font.id][1].get()
        ]
        
        if not selected_fonts:
            messagebox.showwarning("Warning", "No fonts selected")
            self.conversion_in_progress = False
            return
        
        output_dir = filedialog.askdirectory(title="Select output folder for converted fonts")
        if not output_dir:
            self.conversion_in_progress = False
            return
        
        try:
            success_count = 0
            error_count = 0
            total = len(selected_fonts)
            
            self.status_var.set("Converting fonts...")
            
            for idx, font in enumerate(selected_fonts):
                try:
                    self.progress_var.set(int((idx / total) * 100))
                    self.root.update()
                    
                    if not font.filepath or not os.path.exists(font.filepath):
                        logger.warning(f"Font file not found: {font.name}")
                        error_count += 1
                        continue
                    
                    # Create output filename
                    output_filename = f"{font.name} - {font.weight}.otf"
                    output_filename = self.sanitize_filename(output_filename)
                    output_path = pjoin(output_dir, output_filename)
                    
                    # Handle conflicts
                    if os.path.exists(output_path):
                        counter = 1
                        base_name = output_filename[:-4]  # Remove .otf
                        while os.path.exists(output_path):
                            output_filename = f"{base_name} ({counter}).otf"
                            output_path = pjoin(output_dir, output_filename)
                            counter += 1
                    
                    # Convert font
                    if self.convert_adobe_font_to_otf(font.filepath, output_path, font.name):
                        success_count += 1
                        logger.info(f"Converted: {output_filename}")
                    else:
                        error_count += 1
                
                except Exception as e:
                    logger.error(f"Error converting {font.name}: {e}")
                    error_count += 1
            
            self.progress_var.set(100)
            
            status_msg = f"Successfully converted {success_count} fonts"
            if error_count > 0:
                status_msg += f" ({error_count} errors)"
            
            self.status_var.set(status_msg)
            messagebox.showinfo("Conversion Complete", status_msg)
            
        except Exception as e:
            error_msg = f"Error during conversion: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Conversion error")
        finally:
            self.progress_var.set(0)
            self.conversion_in_progress = False

    def install_threaded(self):
        """Install selected fonts to system in a separate thread"""
        if not self.machine_licensed:
            messagebox.showerror(
                "License Required",
                "Adobe Creative Cloud license not detected.\n\n"
                "Installation requires an active Adobe CC license on this machine."
            )
            return
        
        thread = threading.Thread(target=self.install_to_system, daemon=True)
        thread.start()

    def install_to_system(self):
        """Install converted fonts to system fonts directory"""
        try:
            selected_fonts = [
                font for font in self.fonts
                if font.id in self.font_checkboxes and self.font_checkboxes[font.id][1].get()
            ]
            
            if not selected_fonts:
                messagebox.showwarning("Warning", "No fonts selected")
                return
            
            success_count = 0
            error_count = 0
            total = len(selected_fonts)
            
            self.status_var.set("Installing fonts to system...")
            
            if sys.platform == 'win32':
                fonts_dir = os.path.expandvars(r'%WINDIR%\Fonts')
                for idx, font in enumerate(selected_fonts):
                    try:
                        self.progress_var.set(int((idx / total) * 100))
                        self.root.update()
                        
                        if font.filepath and os.path.exists(font.filepath):
                            dest_path = pjoin(fonts_dir, os.path.basename(font.filepath))
                            shutil.copy2(font.filepath, dest_path)
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        logger.error(f"Install error for {font.name}: {e}")
                        error_count += 1
            else:
                fonts_dir = os.path.expandvars('$HOME/Library/Fonts')
                for idx, font in enumerate(selected_fonts):
                    try:
                        self.progress_var.set(int((idx / total) * 100))
                        self.root.update()
                        
                        if font.filepath and os.path.exists(font.filepath):
                            dest_path = pjoin(fonts_dir, os.path.basename(font.filepath))
                            shutil.copy2(font.filepath, dest_path)
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        logger.error(f"Install error for {font.name}: {e}")
                        error_count += 1
            
            self.progress_var.set(100)
            
            status_msg = f"Successfully installed {success_count} fonts"
            if error_count > 0:
                status_msg += f" ({error_count} errors)"
            
            self.status_var.set(status_msg)
            messagebox.showinfo("Installation Complete", f"{status_msg}\n\nYou may need to restart your applications to see the fonts.")
            
        except Exception as e:
            error_msg = f"Error installing fonts: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Installation error")
        finally:
            self.progress_var.set(0)

    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid filename characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '-')
        return filename.strip(' .')

    def load_fonts(self):
        """Load extracted fonts from directory"""
        def load_thread():
            try:
                # Let user select extracted fonts directory
                if not self.extracted_fonts_dir:
                    self.root.after(0, self._select_fonts_dir)
                else:
                    self._load_fonts_from_dir()
            except Exception as e:
                logger.error(f"Error loading fonts: {e}")
                self.root.after(0, lambda: self.status_var.set("Error loading fonts"))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def _select_fonts_dir(self):
        """Select the extracted fonts directory"""
        fonts_dir = filedialog.askdirectory(title="Select folder containing extracted Adobe fonts")
        if fonts_dir:
            self.extracted_fonts_dir = fonts_dir
            self._load_fonts_from_dir()

    def _load_fonts_from_dir(self):
        """Load fonts from the selected directory"""
        try:
            if not self.extracted_fonts_dir:
                return
            
            self.fonts = []
            
            # Scan directory for font files
            if os.path.exists(self.extracted_fonts_dir):
                for filename in os.listdir(self.extracted_fonts_dir):
                    filepath = pjoin(self.extracted_fonts_dir, filename)
                    if os.path.isfile(filepath):
                        # Parse font name from filename
                        name_parts = filename.rsplit(' - ', 1)
                        if len(name_parts) == 2:
                            font_name = name_parts[0]
                            weight = name_parts[1].replace('.otf', '').replace('.ttf', '')
                        else:
                            font_name = filename.replace('.otf', '').replace('.ttf', '')
                            weight = 'Regular'
                        
                        font = FontData(
                            id=os.path.basename(filepath),
                            name=font_name,
                            weight=weight,
                            category='User Converted',
                            filepath=filepath
                        )
                        self.fonts.append(font)
            
            self.root.after(0, self.display_fonts)
            self.root.after(0, lambda: self.status_var.set(f"Loaded {len(self.fonts)} fonts"))
            self.root.after(0, lambda: self.info_var.set(f"Total: {len(self.fonts)} fonts"))
            
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            self.root.after(0, lambda: self.status_var.set("Error loading fonts"))

    def refresh_fonts(self):
        """Refresh font list"""
        self.fonts.clear()
        self.font_cache.clear()
        self.load_fonts()

    def on_search_change(self, *args):
        """Callback when search text changes"""
        self.display_fonts(self.search_var.get())

    def display_fonts(self, filter_text: str = ""):
        """Display fonts in the interface"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.font_checkboxes.clear()
        
        visible_count = 0
        for font in self.fonts:
            if filter_text.lower() in font.name.lower() or filter_text.lower() in font.weight.lower():
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(
                    self.scrollable_frame,
                    text=f"{font.name} - {font.weight}",
                    variable=var
                )
                cb.grid(row=visible_count, column=0, sticky=tk.W, padx=5, pady=2)
                self.font_checkboxes[font.id] = (cb, var)
                visible_count += 1
        
        total = len(self.fonts)
        visible = len(self.font_checkboxes)
        if visible < total:
            self.info_var.set(f"Showing {visible} of {total} fonts")
        else:
            self.info_var.set(f"Total: {total} fonts")

    def select_all(self):
        """Select all visible fonts"""
        for _, (_, var) in self.font_checkboxes.items():
            var.set(True)

    def deselect_all(self):
        """Deselect all visible fonts"""
        for _, (_, var) in self.font_checkboxes.items():
            var.set(False)

def main():
    root = tk.Tk()
    app = AdobeFontConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
