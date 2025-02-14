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
            font_dir = path_prefix  # Usamos el directorio raíz para buscar en todas las carpetas
        else:  # MacOS
            path_prefix = os.path.expandvars(r'$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype')
            manifest = os.path.join(path_prefix, '.c/entitlements.xml')
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
                    f_id = font_elem.find('id').text
                    f_name = props.find('familyName').text
                    f_weight = props.find('variationName').text
                    
                    if not all([f_id, f_name, f_weight]):
                        continue
                        
                    font = FontData(id=f_id, name=f_name, weight=f_weight)
                    fonts.append(font)
                except (AttributeError, TypeError) as e:
                    logger.warning(f"Error procesando fuente en manifest: {e}")
                    continue

            return fonts
            
        except ElementTree.ParseError as e:
            raise ValueError(f"Error al analizar el archivo manifest: {e}")

    def find_font_file(self, font_id: str) -> str:
        """Busca el archivo numerado en todas las subcarpetas excepto 'c'"""
        adobe_root = self.font_dir
        font_id_str = str(font_id)
        
        # Lista de subdirectorios a revisar (excluyendo 'c')
        subdirs = ['e', 'r', 't', 'u', 'w', 'x']
        
        for subdir in subdirs:
            subdir_path = os.path.join(adobe_root, subdir)
            if not os.path.exists(subdir_path):
                continue
                
            # Buscar el archivo por su número ID
            file_path = os.path.join(subdir_path, font_id_str)
            if os.path.exists(file_path):
                return file_path
                
            # También buscar en una subcarpeta con el mismo número
            nested_path = os.path.join(subdir_path, font_id_str, font_id_str)
            if os.path.exists(nested_path):
                return nested_path
        
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
                        logger.warning(f"No se encontró el archivo para ID {font.id} ({font.name})")
                        skipped_count += 1
                        continue

                    # Crear el nuevo nombre con extensión .otf
                    new_name = f"{font.name} - {font.weight}.otf"
                    # Reemplazar caracteres inválidos para nombres de archivo
                    new_name = new_name.replace('/', '-').replace('\\', '-').replace(':', '-')
                    dest_path = pjoin(export_dir, new_name)
                    
                    # Copiar el archivo y renombrarlo
                    shutil.copy2(src_path, dest_path)
                    
                    # Hacer el archivo visible
                    if sys.platform == 'win32':
                        try:
                            import subprocess
                            subprocess.run(['attrib', '-H', '-S', '-R', dest_path], check=True)
                        except subprocess.CalledProcessError as e:
                            logger.warning(f"No se pudieron cambiar los atributos del archivo {new_name}: {e}")
                    else:
                        # Para sistemas Unix/Mac
                        try:
                            import stat
                            os.chmod(dest_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                        except Exception as e:
                            logger.warning(f"No se pudieron cambiar los permisos del archivo {new_name}: {e}")
                    
                    success_count += 1
                    logger.info(f"Fuente copiada y hecha visible: {new_name}")
                    
                except Exception as e:
                    logger.error(f"Error copiando fuente {font.name}: {e}")
                    error_count += 1
            
            status_msg = f"Successfully exported {success_count} fonts"
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
                raise FileNotFoundError(f"No se encontró el archivo manifest de Adobe: {config.manifest}")
            
            self.fonts = self.get_font_metadata(config.manifest)
            self.font_dir = config.font_dir
            
            logger.info(f"Directorio de fuentes: {self.font_dir}")
            logger.info(f"Fuentes encontradas: {len(self.fonts)}")
            
            self.display_fonts()
            self.status_var.set(f"Se cargaron {len(self.fonts)} fuentes")
            
        except Exception as e:
            error_msg = f"No se pudieron cargar las fuentes: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error cargando fuentes")

    def on_search_change(self, *args):
        """Callback when search text changes"""
        self.display_fonts(self.search_var.get())

    def display_fonts(self, filter_text: str = ""):
        """Display fonts in the interface, optionally filtered"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.font_checkboxes.clear()
        
        for i, font in enumerate(self.fonts):
            if filter_text.lower() in font.name.lower():
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(
                    self.scrollable_frame,
                    text=f"{font.name} - {font.weight}",
                    variable=var
                )
                cb.grid(row=i, column=0, sticky=tk.W)
                self.font_checkboxes[font.id] = (cb, var)

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