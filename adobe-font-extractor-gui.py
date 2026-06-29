import sys
import os
import shutil
from os.path import join as pjoin
from xml.etree import ElementTree
from collections import namedtuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Optional
import logging
import threading
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Font data structure
FontData = namedtuple('FontData', 'id name weight category')

class FontExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Adobe Font Extractor")
        self.root.geometry("900x700")
        
        # Variables
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.fonts: List[FontData] = []
        self.font_checkboxes: Dict[str, tuple] = {}
        self.font_dir = None
        self.export_in_progress = False
        self.installed_fonts = set()
        self.font_cache: Dict[str, str] = {}
        
        self.setup_gui()
        self.load_fonts()

    def setup_gui(self):
        """Setup the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Top section: Search and info
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(top_frame, text="Search font:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Info label
        self.info_var = tk.StringVar()
        self.info_var.set("Loading fonts...")
        info_label = ttk.Label(top_frame, textvariable=self.info_var, foreground="gray")
        info_label.pack(side=tk.RIGHT, padx=5)
        
        # Font list frame with scrollbar
        list_frame = ttk.LabelFrame(main_frame, text="Available Fonts", padding="5")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
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
        control_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.refresh_fonts).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Selected", command=self.export_selected_threaded).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(fill=tk.X)
        
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=5)

    def platform_setup(self) -> tuple:
        """Set up paths based on platform"""
        Config = namedtuple('Config', 'path_prefix font_dir manifest')
        
        if sys.platform == 'win32':  # Windows
            path_prefix = os.path.expandvars(r'%APPDATA%\Adobe\CoreSync\plugins\livetype')
            manifest = pjoin(path_prefix, 'c', 'entitlements.xml')
            font_dir = path_prefix
        else:  # macOS/Linux
            path_prefix = os.path.expandvars(r'$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype')
            manifest = os.path.join(path_prefix, '.c', 'entitlements.xml')
            font_dir = path_prefix
        
        return Config(path_prefix, font_dir, manifest)

    def get_font_metadata(self, manifest_path: str) -> List[FontData]:
        """Read font metadata from XML file"""
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
        
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
                        logger.debug("Font element missing properties tag")
                        continue
                    
                    id_elem = font_elem.find('id')
                    family_name_elem = props.find('familyName')
                    var_name_elem = props.find('variationName')
                    category_elem = props.find('categoryCode')
                    
                    if id_elem is None or family_name_elem is None or var_name_elem is None:
                        logger.debug("Font element missing required XML elements")
                        continue
                    
                    f_id = id_elem.text
                    f_name = family_name_elem.text
                    f_weight = var_name_elem.text
                    f_category = category_elem.text if category_elem is not None else "Uncategorized"
                    
                    if not all([f_id, f_name, f_weight]):
                        logger.debug("Font element has empty text values")
                        continue
                        
                    font = FontData(id=f_id, name=f_name, weight=f_weight, category=f_category)
                    fonts.append(font)
                except (AttributeError, TypeError) as e:
                    logger.debug(f"Error processing font in manifest: {e}")
                    continue

            logger.info(f"Loaded {len(fonts)} fonts from manifest")
            return fonts
            
        except ElementTree.ParseError as e:
            raise ValueError(f"Error parsing manifest file: {e}")

    def find_font_file(self, font_id: str) -> Optional[str]:
        """Recursively search for font file in Adobe subdirectories"""
        # Check cache first
        if font_id in self.font_cache:
            return self.font_cache[font_id]
        
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
                self.font_cache[font_id] = file_path
                logger.debug(f"Found font file at: {file_path}")
                return file_path
            
            # Recursively search subdirectories
            try:
                for root, dirs, files in os.walk(subdir_path):
                    if font_id_str in files:
                        found_path = os.path.join(root, font_id_str)
                        self.font_cache[font_id] = found_path
                        logger.debug(f"Found font file at: {found_path}")
                        return found_path
            except (OSError, PermissionError) as e:
                logger.debug(f"Error walking directory {subdir_path}: {e}")
                continue
        
        logger.warning(f"Font file not found for ID: {font_id_str}")
        return None

    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid filename characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '-')
        # Remove leading/trailing spaces and dots
        return filename.strip(' .')

    def export_selected_threaded(self):
        """Export selected fonts in a separate thread"""
        if self.export_in_progress:
            messagebox.showwarning("Warning", "Export already in progress")
            return
        
        thread = threading.Thread(target=self.export_selected, daemon=True)
        thread.start()

    def export_selected(self):
        """Export selected fonts"""
        self.export_in_progress = True
        selected_fonts = [
            font for font in self.fonts
            if font.id in self.font_checkboxes and self.font_checkboxes[font.id][1].get()
        ]
        
        if not selected_fonts:
            messagebox.showwarning("Warning", "No fonts selected")
            self.export_in_progress = False
            return
            
        export_dir = filedialog.askdirectory(title="Select destination folder")
        if not export_dir:
            self.export_in_progress = False
            return
            
        try:
            os.makedirs(export_dir, exist_ok=True)
            
            success_count = 0
            error_count = 0
            skipped_count = 0
            total = len(selected_fonts)
            
            self.status_var.set("Exporting fonts...")
            
            for idx, font in enumerate(selected_fonts):
                try:
                    self.progress_var.set(int((idx / total) * 100))
                    self.root.update()
                    
                    src_path = self.find_font_file(font.id)
                    
                    if not src_path:
                        logger.warning(f"Font file not found for ID {font.id} ({font.name})")
                        skipped_count += 1
                        continue

                    # Create filename with font name and weight
                    new_name = f"{font.name} - {font.weight}"
                    new_name = self.sanitize_filename(new_name)
                    dest_path = pjoin(export_dir, new_name)
                    
                    # Handle file conflicts
                    if os.path.exists(dest_path):
                        counter = 1
                        base_name = new_name
                        while os.path.exists(dest_path):
                            new_name = f"{base_name} ({counter})"
                            dest_path = pjoin(export_dir, new_name)
                            counter += 1
                    
                    # Copy the file
                    shutil.copy2(src_path, dest_path)
                    logger.info(f"Font copied: {new_name}")
                    
                    # Make the file visible/readable
                    self._make_file_visible(dest_path, new_name)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error copying font {font.name}: {e}")
                    error_count += 1
            
            self.progress_var.set(100)
            
            status_msg = f"Successfully exported {success_count} fonts"
            if skipped_count > 0:
                status_msg += f" ({skipped_count} skipped)"
            if error_count > 0:
                status_msg += f" ({error_count} errors)"
            
            self.status_var.set(status_msg)
            messagebox.showinfo("Export Complete", status_msg)
            
        except Exception as e:
            error_msg = f"Error exporting fonts: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Export error")
        finally:
            self.progress_var.set(0)
            self.export_in_progress = False

    def _make_file_visible(self, file_path: str, file_name: str) -> None:
        """Make file visible on the system"""
        try:
            if sys.platform == 'win32':
                import subprocess
                subprocess.run(['attrib', '-H', '-S', '-R', file_path], check=False)
            else:
                import stat
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        except Exception as e:
            logger.warning(f"Could not change file attributes for {file_name}: {e}")

    def load_fonts(self):
        """Load fonts from Adobe manifest"""
        def load_thread():
            try:
                config = self.platform_setup()
                
                if not os.path.exists(config.manifest):
                    raise FileNotFoundError(f"Adobe manifest file not found at:\n{config.manifest}")
                
                self.fonts = self.get_font_metadata(config.manifest)
                self.font_dir = config.font_dir
                
                logger.info(f"Font directory: {self.font_dir}")
                logger.info(f"Fonts found: {len(self.fonts)}")
                
                self.root.after(0, self.display_fonts)
                self.root.after(0, lambda: self.status_var.set(f"Loaded {len(self.fonts)} fonts"))
                self.root.after(0, lambda: self.info_var.set(f"Total: {len(self.fonts)} fonts"))
                
            except Exception as e:
                error_msg = f"Could not load fonts: {str(e)}"
                logger.error(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.status_var.set("Error loading fonts"))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def refresh_fonts(self):
        """Refresh font list"""
        self.font_cache.clear()
        self.load_fonts()

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
        
        # Update info
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
    app = FontExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
