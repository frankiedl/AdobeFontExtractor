# Adobe Font Extractor

A Python-based GUI tool to extract and save Adobe Creative Cloud fonts that are installed on your system. This tool helps you backup your Adobe fonts by finding them in the Adobe CoreSync folders and copying them to a location of your choice.

![image](https://github.com/user-attachments/assets/3914b3c2-51f6-4cec-b6b8-36b7a199f732)


## ⚠️ IMPORTANT: Font Usability & Licensing

**CRITICAL LIMITATION:** Extracted Adobe fonts are **NOT directly usable outside Adobe Creative Cloud applications**.

### Why Extracted Fonts Don't Work Elsewhere:
- Adobe Fonts are stored in a **proprietary binary format** with embedded licensing
- They require **authentication with Adobe's service** to function
- Standard applications (Word, Photoshop alternatives, browsers, etc.) **cannot read or render these fonts**
- **Simply copying the files does NOT remove Adobe's licensing restrictions**

### Legal Use Cases for Extraction:
- **Backup purposes**: Create local backups of fonts you've licensed
- **Offline access**: Use extracted fonts in Adobe apps when offline (limited functionality)
- **Archival**: Keep copies for reference or future restoration
- **Migration**: Temporarily backup before reinstalling Adobe Creative Cloud

### What You CANNOT Do:
- ❌ Use extracted fonts in non-Adobe applications
- ❌ Share extracted fonts with others
- ❌ Use extracted fonts after your Adobe subscription expires
- ❌ Install extracted fonts as system fonts for general use

---

## Features

- User-friendly graphical interface
- Search functionality to easily find specific fonts (by name or weight)
- Batch export of selected fonts
- Preserves font names from Adobe's metadata
- Makes files accessible and visible on your system
- Cross-platform support (Windows and MacOS)
- **Threading** for responsive UI during operations
- **Progress bar** showing export status
- **Font caching** for improved performance
- **Refresh button** to reload fonts without restarting

## Requirements

- Python 3.6 or higher
- tkinter (usually comes with Python)
- An active Adobe Creative Cloud subscription with fonts synced to your computer

## Installation

1. Clone this repository or download the Python script:
```bash
git clone https://github.com/frankiedl/AdobeFontExtractor.git
cd AdobeFontExtractor
```

2. Make sure you have Python 3.6+ installed on your system.

3. The script uses only standard library modules, so no additional installations are required.

## Usage

1. Run the script:
```bash
python adobe-font-extractor-gui.py
```

2. The application will open and automatically scan your Adobe fonts directory:
   - **Windows**: `%APPDATA%\Adobe\CoreSync\plugins\livetype`
   - **MacOS**: `$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype`

3. Use the interface to:
   - Search for specific fonts using the search bar (supports font name and weight)
   - Select individual fonts or use "Select All"
   - Click "Refresh" to reload the font list
   - Click "Export Selected" to choose a destination folder
   - Monitor progress with the progress bar
   - View font count and filtering information

## How It Works

The tool works by:

1. **Reading Adobe's metadata**: Parses `entitlements.xml` to get font names, weights, IDs, and categories
2. **Locating font files**: Searches Adobe's CoreSync directories (e, r, t, u, w, x folders) to find actual font files by ID
3. **Extracting files**: Copies the font files to your chosen destination with descriptive names
4. **Making files accessible**: Adjusts file permissions and attributes to ensure visibility

## Important Technical Details

### What Gets Extracted
- Adobe stores fonts in **binary format** in the CoreSync directories
- Files are **numbered** (e.g., `12345`) rather than named
- The tool **maps these IDs to readable names** from the manifest

### Extracted Font Characteristics
- **Format**: Adobe proprietary binary format (NOT standard TTF/OTF)
- **Compatibility**: Only work with Adobe Creative Cloud applications that support font authentication
- **Size**: Files range from ~50KB to ~500KB depending on complexity
- **DRM**: Embedded licensing restrictions remain intact

### Limitations
- Extracted fonts **cannot be installed as system fonts**
- They **will not work** in Microsoft Office, Google Docs, Figma, or other non-Adobe apps
- **Font conversion tools may not work** due to embedded licensing
- **Offline use is limited** and depends on Adobe's authentication cache

---

## Common Issues

### No Fonts Found
- Make sure you have an **active Adobe Creative Cloud subscription**
- Verify that you have **synced fonts through Adobe Creative Cloud**
- Check if the Adobe CoreSync folder exists in the expected location
- On macOS, hidden files (starting with `.`) may be hidden - use `Cmd+Shift+.` in Finder

### Export Errors
- Ensure you have **write permissions** in the destination folder
- Check if you have **enough disk space** for the export
- Make sure the selected fonts are **still synced** in Adobe Creative Cloud
- On Windows, close any file explorers viewing the destination folder

### Extracted Fonts Not Working
- **This is expected and normal**. Extracted fonts will NOT work in most applications
- They are for Adobe app use only or as backups
- Use font conversion services (if legally permitted under your license) for other uses

### Font File Appears Corrupted
- The font file is **not corrupted** - it's in Adobe's proprietary format
- It will only work when accessed through Adobe's authentication system
- Use the exported files only with Adobe Creative Cloud apps

### Missing Fonts After Export
- Some fonts may not have associated files (cloud-only fonts)
- Adobe may have removed access to certain fonts
- Check Adobe's font library for availability

---

## File Locations

### Windows
- Font files: `%APPDATA%\Adobe\CoreSync\plugins\livetype\[e,r,t,u,w,x]`
- Manifest: `%APPDATA%\Adobe\CoreSync\plugins\livetype\c\entitlements.xml`

### MacOS
- Font files: `$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype/.[e,r,t,u,w,x]`
- Manifest: `$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype/.c/entitlements.xml`
- Note: Directories starting with `.` are hidden by default

---

## Technical Architecture

- **Language**: Python 3.6+
- **GUI Framework**: tkinter (standard library)
- **Threading**: Non-blocking UI for font loading and export operations
- **Font Metadata**: XML parsing for Adobe's entitlements manifest
- **Caching**: In-memory cache for font file lookups

---

## Contributing

Contributions are welcome! Areas for improvement:
- Font format conversion tools (if legally compliant)
- Enhanced font preview functionality
- Support for additional Adobe Cloud services
- Better error recovery mechanisms

Please feel free to submit a Pull Request.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Disclaimer

**IMPORTANT LEGAL NOTICE**

This tool is provided for **personal backup purposes only**. 

By using this tool, you agree to:

1. **Comply with Adobe's Terms of Service** - https://www.adobe.com/legal/terms.html
2. **Respect font licensing agreements** - Extracted fonts remain subject to Adobe's licensing terms
3. **Personal use only** - Do NOT distribute, share, or sell extracted fonts
4. **Legal liability** - The authors are NOT responsible for misuse of this tool
5. **Subscription requirement** - You must maintain an active Adobe Creative Cloud subscription to legally use extracted fonts

**Extracted fonts:**
- May NOT be redistributed or shared
- Remain subject to Adobe's licensing terms indefinitely
- May become inaccessible if your subscription expires
- Cannot be used to circumvent Adobe's licensing system

If you no longer have an active Adobe subscription, you should delete all extracted fonts.

---

## Support

If you encounter any issues or have suggestions for improvements:
1. Check the **Common Issues** section above
2. Review your Adobe Creative Cloud subscription status
3. Create an issue in the GitHub repository
4. Provide detailed information about your system, Python version, and the specific error

## Acknowledgments

- Thanks to the Adobe Creative Cloud community for documenting the CoreSync folder structure
- Built with Python and tkinter for cross-platform compatibility
- Special thanks to users who reported bugs and helped improve the tool
