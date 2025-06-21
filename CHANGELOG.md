# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Command-line interface for the auto-categorization feature.
- Main GUI application window to serve as a launchpad for tools.
- Auto-categorization feature based on user-defined rules in an "AutoCat" sheet.
- GUI for managing and running the auto-categorization feature.
- Detailed feature specification for auto-categorization (`docs/auto_categorize.md`).
- Initial project structure
- Basic bank transaction import functionality
- Support for Ally and Capital One banks
- Command-line and GUI interfaces
- Excel spreadsheet management
- Transaction categorization
- Duplicate detection

### Changed
- **Major Refactoring**: Reworked the command-line interface to use subcommands (`import`, `autocat`) for better usability and extensibility.
- **Major Refactoring**: Migrated the GUI from a multi-window design to a modern single-window, frame-based architecture for better performance and user experience.
- Improved the auto-categorizer to support natural language rule headers (e.g., "Description Contains") for more intuitive rule creation.
- Enhanced the auto-categorizer to allow multiple rules to apply to a single transaction.
- Standardized UI elements (buttons, styles) for a consistent look and feel across all views.
- Updated and clarified the auto-categorization documentation.
- Restructured project to follow standard GitHub repository format

### Fixed
- None yet

### Security
- None yet 