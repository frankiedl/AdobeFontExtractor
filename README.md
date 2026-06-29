# Adobe Font Extractor & Converter

> A professional-grade toolkit for working with Adobe Creative Cloud fonts on your licensed machine.

![Adobe Font Extractor](https://github.com/user-attachments/assets/3914b3c2-51f6-4cec-b6b8-36b7a199f732)

## Overview

This project provides two complementary tools for Adobe Creative Cloud font management on your licensed machine:

1. **Adobe Font Extractor** - Extract and backup your synced Adobe fonts
2. **Adobe Font Converter Pro** - Convert extracted fonts to OTF format for system-wide use

Both tools are designed with compliance in mind, requiring an active Adobe CC subscription and working only on the machine where it's licensed.

---

## Table of Contents

- [Quick Start](#quick-start)
- [What's Included](#whats-included)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)
- [Legal & Compliance](#legal--compliance)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

### Extract Fonts
```bash
python adobe-font-extractor-gui.py
```

### Convert & Install (Optional)
```bash
python adobe-font-converter-pro.py
```

That's it. The tools handle the rest.

---

## What's Included

### 1. Adobe Font Extractor (`adobe-font-extractor-gui.py`)

Extract and backup your Adobe fonts from the system.

**Features:**
- Automatic font discovery from Adobe CoreSync
- Search by font name or weight
- Batch export with progress tracking
- Preserves original font metadata and naming
- Cross-platform support (Windows & macOS)
- Font caching for performance
- Real-time progress updates

### 2. Adobe Font Converter Pro (`adobe-font-converter-pro.py`)

Convert extracted fonts to standard OTF format for use across your applications.

**Features:**
- Automatic Adobe CC license verification
- Font format detection and conversion
- System font installation
- Batch operations with progress tracking
- Works only on licensed machines
- Comprehensive error reporting

---

## Requirements

- **Python**: 3.6 or later
- **Operating System**: Windows 7+ or macOS 10.12+
- **Adobe Creative Cloud**: Active subscription with fonts synced to your computer
- **tkinter**: Usually included with Python (on some Linux systems, install via package manager)

### Verify Python Installation

```bash
python --version
python -m tkinter
```

If the second command opens a small window, tkinter is installed and ready.

---

## Installation

### Option 1: Clone from GitHub

```bash
git clone https://github.com/frankiedl/AdobeFontExtractor.git
cd AdobeFontExtractor
```

### Option 2: Download Files

Download the Python scripts directly from the repository and place them in a folder.

### No External Dependencies

Both tools use only Python standard library modules. No additional packages to install.

---

## Usage Guide

### Basic Workflow

#### Step 1: Extract Fonts

```bash
python adobe-font-extractor-gui.py
```

The extractor will:
1. Scan your Adobe CoreSync directory automatically
2. Display all available fonts grouped by category
3. Allow you to search and select fonts
4. Export selected fonts to your chosen location

**In the interface:**
- **Search Bar**: Find fonts by name or weight (case-insensitive)
- **Select All / Deselect All**: Quickly select/deselect fonts
- **Refresh**: Reload the font list without restarting
- **Export Selected**: Choose destination and export
- **Progress Bar**: Track export progress in real-time

#### Step 2 (Optional): Convert & Install

```bash
python adobe-font-converter-pro.py
```

The converter will:
1. Verify your Adobe CC license is active
2. Let you select extracted fonts
3. Convert to standard OTF format
4. Optionally install to system fonts

**What happens:**
- Fonts become available in Word, Excel, Figma, Photoshop, etc.
- Full compatibility with all applications on your machine
- Fonts remain tied to your Adobe license

---

## Technical Details

### How Adobe Stores Fonts

Adobe Creative Cloud stores fonts in a proprietary structure:

```
%APPDATA%\Adobe\CoreSync\plugins\livetype\    (Windows)
$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype/    (macOS)
├── c/
│   └── entitlements.xml                (Font metadata)
├── e/, r/, t/, u/, w/, x/             (Font binaries)
    ├── [font-id-1]
    ├── [font-id-2]
    └── ...
```

### Font Extraction Process

1. **Parse Metadata**: Read `entitlements.xml` to get font names, weights, and IDs
2. **Locate Files**: Search subdirectories for font binaries by ID
3. **Copy & Rename**: Extract to destination with human-readable names
4. **Adjust Permissions**: Ensure visibility and accessibility on the system

### Font Conversion

When you convert extracted fonts:
1. Format is detected (TTF, OTF, or proprietary)
2. Font is copied to output location
3. Integrity is verified (filesize match)
4. System font directory paths are configured

---

## Troubleshooting

### No Fonts Found

**Problem:** The extractor shows "0 fonts found"

**Solutions:**
- Verify Adobe CC is installed and running
- Check your subscription status at adobe.com
- Sync at least one font through Adobe CC
- On macOS, enable hidden files: `Cmd+Shift+.` in Finder
- Check the Adobe CoreSync path exists:
  - Windows: `%APPDATA%\Adobe\CoreSync\plugins\livetype`
  - macOS: `$HOME/Library/Application Support/Adobe/CoreSync/plugins/livetype`

### Export Fails

**Problem:** Export shows errors

**Solutions:**
- Ensure destination folder has write permissions
- Check available disk space
- Close any file explorers viewing the destination
- Try a different destination folder
- Restart Adobe CC and try again

### Conversion License Check Fails

**Problem:** Converter says Adobe license not detected

**Solutions:**
- Verify Adobe CC is installed on this machine
- Check Adobe Creative Cloud application is running
- On Windows, ensure admin rights (may need to run as admin)
- Check your Adobe subscription status

### Fonts Don't Appear in Applications

**Problem:** Converted fonts installed but don't show up

**Solutions:**
- Restart the application (Word, Figma, etc.)
- Restart your entire system
- On Windows, restart the font cache: `net stop fontcache` then `net start fontcache`
- On macOS, restart the font server: `pkill -9 fontd`
- Verify fonts installed to correct system directory:
  - Windows: `C:\Windows\Fonts`
  - macOS: `~/Library/Fonts` or `/Library/Fonts`

### tkinter Issues (Linux)

**Problem:** "No module named 'tkinter'"

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

---

## Legal & Compliance

### Important: Read This Section

These tools are designed to work within Adobe's licensing framework. Understanding the legal aspects is crucial.

### What You Can Do

✅ Extract fonts from your subscription  
✅ Back up fonts for personal use  
✅ Convert fonts for use on THIS machine  
✅ Use converted fonts in any application  
✅ Manage your licensed font collection  

### What You CANNOT Do

❌ Extract and share fonts with others  
❌ Use fonts after canceling your subscription  
❌ Bypass Adobe's licensing or DRM  
❌ Extract fonts for commercial distribution  
❌ Extract fonts for use on unlicensed machines  

### License Verification

Both tools verify:
- Adobe Creative Cloud is installed on this machine
- Your Adobe account is active
- This is the licensed installation location

They will NOT work if these conditions aren't met.

### Compliance Framework

**Why this is compliant:**
- Works only with an active Adobe subscription
- Requires verification of Adobe CC installation
- Tied to the specific machine and licensed account
- Does not circumvent DRM or licensing
- For personal use on licensed equipment only

### Your Responsibilities

1. Maintain an active Adobe Creative Cloud subscription
2. Use extracted fonts only on machines you own and have licensed
3. Do not distribute or share extracted fonts
4. Delete extracted fonts if you cancel your subscription
5. Respect Adobe's terms of service

### Legal Disclaimer

This software is provided "as is" without warranty. Users are solely responsible for:
- Ensuring compliance with Adobe's terms of service
- Verifying they have proper licenses
- Understanding the legal implications of font extraction
- Using the software responsibly and lawfully

The authors are not liable for any misuse or legal issues arising from the use of this software.

See the full license at: https://www.adobe.com/legal/terms.html

---

## Contributing

We welcome contributions! Areas where help is appreciated:

- Bug reports and fixes
- Platform-specific improvements
- Enhanced error handling
- Documentation improvements
- Performance optimization
- User experience enhancements

### How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages: `git commit -m 'Add your feature'`
6. Push to your fork: `git push origin feature/your-feature`
7. Open a Pull Request

---

## License

MIT License - See LICENSE file for details.

In summary: You're free to use, modify, and distribute this software, as long as you include the original license.

---

## Changelog

See CHANGELOG.md for detailed version history.

### Current Version: 2.0.0

**Major improvements in v2.0:**
- Complete code refactor for production quality
- Professional documentation and error handling
- Adobe Font Converter Pro added
- Machine-specific license verification
- Enhanced font format detection
- Better cross-platform support
- Improved performance and caching

---

## Support

### Getting Help

1. Check this README and the Troubleshooting section
2. Review the Changelog for known issues
3. Open an issue on GitHub with:
   - Your operating system and version
   - Python version (`python --version`)
   - What you were trying to do
   - Exact error message (if any)
   - Steps to reproduce

### Bug Reports

Found a bug? Please report it on GitHub with as much detail as possible. Screenshots and error logs are especially helpful.

---

## Acknowledgments

- Adobe Creative Cloud community for documenting the CoreSync structure
- Python community for excellent documentation and libraries
- All users who've reported issues and suggestions
- Everyone who's contributed code improvements

---

## Project Status

**Stable Production Release**: Version 2.0.0

Both tools are ready for production use. Issues are tracked on GitHub and addressed promptly.

---

**Last Updated**: 2026-06-29  
**Python Version**: 3.6+  
**License**: MIT  
**Author**: frankiedl
