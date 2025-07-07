# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-07

### Changed
- Complete project restructure with modular architecture
- Improved separation of concerns with handler-based MCP server
- Database operations now use repository pattern
- Test suite reorganized into unit and integration tests
- All scripts moved to dedicated scripts/ directory

### Added
- Package installation support with setup.py
- Comprehensive test suite with pytest
- CI/CD pipeline with GitHub Actions
- Development scripts for testing and linting
- LaunchD integration for automatic startup
- Database migration system
- Comprehensive documentation (user guide, quick start, migration guide)
- Example scripts demonstrating all features

### Improved
- Better error handling throughout the codebase
- Type hints added to all functions
- Consistent code formatting with black
- Performance optimizations in search and grouping
- More robust daemon management

### Removed
- Obsolete debug scripts and test files
- Duplicate code and redundant features
- Old daemon versions
- Manual configuration files (now using .env)

### Fixed
- Memory leaks in long-running daemon
- Race conditions in database access
- Notification grouping edge cases
- Search query parsing issues

## [1.0.0] - 2024-12-01

### Initial Release
- Basic notification monitoring daemon
- MCP server integration
- Priority scoring feature
- Enhanced search capability
- Template responses
- Notification grouping
- Batch actions
- Smart summaries
- Analytics dashboard
