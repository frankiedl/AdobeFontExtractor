# Adobe Font Extractor

A Python-based GUI tool to extract and save Adobe Creative Cloud fonts that are installed on your system. This tool helps you backup your Adobe fonts by finding them in the Adobe CoreSync folders and saving them with their proper names and extensions.

![image](https://github.com/user-attachments/assets/3914b3c2-51f6-4cec-b6b8-36b7a199f732)


## Features

- User-friendly graphical interface
- Search functionality to easily find specific fonts
- Batch export of selected fonts
- Preserves font names from Adobe's metadata
- Makes fonts visible and accessible
- Cross-platform support (Windows and MacOS)

## Requirements

- Python 3.6 or higher
- tkinter (usually comes with Python)
- An active Adobe Creative Cloud subscription with fonts synced to your computer

## Installation

1. Clone this repository or download the Python script:
```bash
git clone https://github.com/yourusername/adobe-font-extractor.git
```

2. Make sure you have Python installed on your system.

3. The script uses only standard library modules, so no additional installations are required.

## Usage

1. Run the script:
```bash
python adobe-font-extractor.py
```

2. The application will open and automatically scan your Adobe fonts directory:
   - Windows: `%APPDATA%\Adobe\CoreSync\plugins\livetype`
   - MacOS: `$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype`

3. Use the interface to:
   - Search for specific fonts using the search bar
   - Select individual fonts or use "Select All"
   - Click "Export Selected" to choose a destination folder
   - Wait for the export process to complete

## How It Works

The tool works by:

1. Reading Adobe's `entitlements.xml` file to get font metadata (names, weights, IDs)
2. Scanning Adobe's CoreSync folders (except 'c') to find the actual font files
3. Copying the files to your chosen destination with proper names and .otf extension
4. Making the exported files visible and accessible

## Common Issues

### No Fonts Found
- Make sure you have an active Adobe Creative Cloud subscription
- Verify that you have synced fonts through Adobe Creative Cloud
- Check if the Adobe CoreSync folder exists in the expected location

### Export Errors
- Ensure you have write permissions in the destination folder
- Check if you have enough disk space
- Make sure the selected fonts are still synced in Adobe Creative Cloud

## File Locations

### Windows
- Font files: `%APPDATA%\Adobe\CoreSync\plugins\livetype\[e,r,t,u,w,x]`
- Manifest: `%APPDATA%\Adobe\CoreSync\plugins\livetype\c\entitlements.xml`

### MacOS
- Font files: `$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype/.[e,r,t,u,w,x]`
- Manifest: `$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype/.c/entitlements.xml`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for personal backup purposes only. Please ensure you comply with Adobe's terms of service and font licensing agreements when using this tool. The extracted fonts are still subject to Adobe's licensing terms.

## Support

If you encounter any issues or have suggestions for improvements:
1. Check the Common Issues section above
2. Create an issue in the GitHub repository
3. Provide detailed information about your system and the error

## Acknowledgments

- Thanks to the Adobe Creative Cloud community for helping understand the font storage structure
- Built with Python and tkinter for cross-platform compatibility
