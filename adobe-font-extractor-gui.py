import sys
import os
import shutil
from os.path import join as pjoin
from xml.etree import ElementTree
from collections import namedtuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Font data structure
FontData = namedtuple('FontData', 'id name weight')

class FontExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Adobe Font Extractor")
        self.root.geometry("800x600")
        
        # Variables
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.fonts: List[FontData] = []
        self.font_checkboxes: Dict[str, tuple] = {}
        self.font_dir = None
        
        self.setup_gui()
        self.load_fonts()

    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Search bar
        ttk.Label(main_frame, text="Search font:").grid(row=0, column=0, sticky=tk.W)
        search_entry = ttk.Entry(main_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Font list frame with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
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
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Selected", command=self.export_selected).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    def platform_setup(self):
        """Set up paths based on platform"""
        Config = namedtuple('Config', 'path_prefix font_dir manifest')
        
        if sys.platform == 'win32':  # Windows
            path_prefix = os.path.expandvars(r'%APPDATA%\Adobe\CoreSync\plugins\livetype')
            manifest = pjoin(path_prefix, 'c', 'entitlements.xml')
            font_dir = path_prefix
        else:  # MacOS
            path_prefix = os.path.expandvars(r'$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype')
            manifest = os.path.join(path_prefix, '.c', 'entitlements.xml')
            font_dir = path_prefix
        
        return Config(path_prefix, font_dir, manifest)

    def get_font_metadata(self, manifest_path: str) -> List[FontData]:
        """Read font metadata from XML file"""
        try:
            tree = ElementTree.parse(manifest_path)
            fonts_subtree = tree.getroot().find('fonts')
            
            if fonts_subtree is None:
                raise ValueError("'fonts' element not found in manifest")
            
            fonts = []
            for font_elem in fonts_subtree.findall('font'):
                try:
                    props = font_elem.find('properties')
                    if props is None:
                        logger.warning("Font element missing properties tag")
                        continue
                    
                    id_elem = font_elem.find('id')
                    family_name_elem = props.find('familyName')
                    var_name_elem = props.find('variationName')
                    
                    if id_elem is None or family_name_elem is None or var_name_elem is None:
                        logger.warning("Font element missing required XML elements")
                        continue
                    
                    f_id = id_elem.text
                    f_name = family_name_elem.text
                    f_weight = var_name_elem.text
                    
                    if not all([f_id, f_name, f_weight]):
                        logger.warning("Font element has empty text values")
                        continue
                        
                    font = FontData(id=f_id, name=f_name, weight=f_weight)
                    fonts.append(font)
                except (AttributeError, TypeError) as e:
                    logger.warning(f"Error processing font in manifest: {e}")
                    continue

            return fonts
            
        except ElementTree.ParseError as e:
            raise ValueError(f"Error parsing manifest file: {e}")

    def find_font_file(self, font_id: str) -> str:
        """Recursively search for font file in Adobe subdirectories"""
        adobe_root = self.font_dir
        font_id_str = str(font_id)
        
        # List of subdirectories to check (excluding 'c')
        subdirs = ['e', 'r', 't', 'u', 'w', 'x']
        
        for subdir in subdirs:
            subdir_path = os.path.join(adobe_root, subdir)
            if not os.path.exists(subdir_path):
                continue
            
            # Check for file directly in subdir
            file_path = os.path.join(subdir_path, font_id_str)
            if os.path.isfile(file_path):
                logger.debug(f"Found font file at: {file_path}")
                return file_path
            
            # Recursively search subdirectories for nested structures
            try:
                for root, dirs, files in os.walk(subdir_path):
                    if font_id_str in files:
                        found_path = os.path.join(root, font_id_str)
                        logger.debug(f"Found font file at: {found_path}")
                        return found_path
            except (OSError, PermissionError) as e:
                logger.warning(f"Error walking directory {subdir_path}: {e}")
                continue
        
        logger.warning(f"Font file not found for ID: {font_id_str}")
        return None

    def export_selected(self):
        """Export selected fonts"""
        selected_fonts = [
            font for font in self.fonts
            if font.id in self.font_checkboxes and self.font_checkboxes[font.id][1].get()
        ]
        
        if not selected_fonts:
            messagebox.showwarning("Warning", "No fonts selected")
            return
            
        export_dir = filedialog.askdirectory(title="Select destination folder")
        if not export_dir:
            return
            
        try:
            os.makedirs(export_dir, exist_ok=True)
            
            success_count = 0
            error_count = 0
            skipped_count = 0
            
            for font in selected_fonts:
                try:
                    src_path = self.find_font_file(font.id)
                    
                    if not src_path:
                        logger.warning(f"Font file not found for ID {font.id} ({font.name})")
                        skipped_count += 1
                        continue

                    # Create filename with font name and weight (preserve original format)
                    new_name = f"{font.name} - {font.weight}"
                    # Replace invalid filename characters
                    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
                    for char in invalid_chars:
                        new_name = new_name.replace(char, '-')
                    
                    dest_path = pjoin(export_dir, new_name)
                    
                    # Check if file exists and handle conflicts
                    if os.path.exists(dest_path):
                        counter = 1
                        base_name = new_name
                        while os.path.exists(dest_path):
                            new_name = f"{base_name} ({counter})"
                            dest_path = pjoin(export_dir, new_name)
                            counter += 1
                    
                    # Copy the file and rename it
                    shutil.copy2(src_path, dest_path)
                    logger.info(f"Font copied: {new_name}")
                    
                    # Make the file visible/readable
                    if sys.platform == 'win32':
                        try:
                            import subprocess
                            subprocess.run(['attrib', '-H', '-S', '-R', dest_path], check=False)
                        except Exception as e:
                            logger.warning(f"Could not change file attributes for {new_name}: {e}")
                    else:
                        # For Unix/Mac systems
                        try:
                            import stat
                            os.chmod(dest_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                        except Exception as e:
                            logger.warning(f"Could not change file permissions for {new_name}: {e}")
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error copying font {font.name}: {e}")
                    error_count += 1
            
            status_msg = f"Successfully exported {success_count} fonts"
            if skipped_count > 0:
                status_msg += f" ({skipped_count} skipped)"
            if error_count > 0:
                status_msg += f" ({error_count} errors)"
            
            self.status_var.set(status_msg)
            messagebox.showinfo("Result", status_msg)
            
        except Exception as e:
            error_msg = f"Error exporting fonts: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Export error")

    def load_fonts(self):
        """Load fonts from Adobe manifest"""
        try:
            config = self.platform_setup()
            
            if not os.path.exists(config.manifest):
                raise FileNotFoundError(f"Adobe manifest file not found: {config.manifest}")
            
            self.fonts = self.get_font_metadata(config.manifest)
            self.font_dir = config.font_dir
            
            logger.info(f"Font directory: {self.font_dir}")
            logger.info(f"Fonts found: {len(self.fonts)}")
            
            self.display_fonts()
            self.status_var.set(f"Loaded {len(self.fonts)} fonts")
            
        except Exception as e:
            error_msg = f"Could not load fonts: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error loading fonts")

    def on_search_change(self, *args):
        """Callback when search text changes"""
        self.display_fonts(self.search_var.get())

    def display_fonts(self, filter_text: str = ""):
        """Display fonts in the interface, optionally filtered"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.font_checkboxes.clear()
        
        visible_count = 0
        for font in self.fonts:
            if filter_text.lower() in font.name.lower():
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(
                    self.scrollable_frame,
                    text=f"{font.name} - {font.weight}",
                    variable=var
                )
                cb.grid(row=visible_count, column=0, sticky=tk.W)
                self.font_checkboxes[font.id] = (cb, var)
                visible_count += 1

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
    app = FontExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
