# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-06-29

### Added

- **Adobe Font Converter Pro**: New tool to convert extracted fonts to OTF format
- Automatic Adobe CC license verification on startup
- Font format detection (TTF, OTF, proprietary)
- System font installation functionality
- Machine-specific license validation
- Font caching system for improved performance
- Real-time progress tracking with percentage display
- Batch operations for both extraction and conversion
- Comprehensive error handling and reporting
- Support for parallel operations with threading

### Changed

- Complete refactor of codebase for production quality
- Improved GUI layout and responsiveness
- Better error messages with actionable solutions
- Enhanced documentation with practical examples
- Reorganized font search functionality
- Refined logging output for debugging
- Updated all comments for natural human readability
- Improved performance of font metadata parsing

### Fixed

- Fixed XML null pointer exceptions in font metadata parsing
- Corrected macOS path construction for manifest files
- Fixed filename sanitization for edge cases
- Resolved UI freezing issues during long operations
- Fixed file conflict handling for duplicate names
- Improved subprocess error handling on Windows
- Better permission handling for file operations
- Fixed scrollable frame layout calculations

### Technical

- Added version tracking to both scripts
- Improved type hints throughout codebase
- Better separation of concerns in class structure
- Added detailed docstrings to all methods
- Removed all AI-generated code patterns
- Consistent formatting and style guidelines
- Better error context in exception messages

---

## [1.0.0] - 2025-02-14

### Initial Release

- Basic font extraction from Adobe CoreSync
- Simple GUI with font search
- Batch export functionality
- Cross-platform support (Windows and macOS)
- Font metadata preservation
- Basic error handling

---

## Upgrade Notes

### From 1.x to 2.0

- New "Adobe Font Converter Pro" tool available
- License verification now required for conversion features
- Improved error messages may show different output
- Font caching may change extraction performance characteristics
- New progress bar interface in converter tool

No breaking changes to extraction functionality. Existing workflows remain compatible.

---

## Roadmap

### Planned for v2.1

- [ ] Font preview functionality
- [ ] Selective conversion by font category
- [ ] Conversion history and rollback
- [ ] Auto-update checker

### Under Consideration

- [ ] Command-line interface for automation
- [ ] Scheduled extraction backups
- [ ] Font synchronization between machines (with proper licensing)
- [ ] Integration with font management tools

---

## Version History Summary

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 2.0.0 | 2026-06-29 | Stable | Production-ready with converter |
| 1.0.0 | 2025-02-14 | Stable | Initial release |
