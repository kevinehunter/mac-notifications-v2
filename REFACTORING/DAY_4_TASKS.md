# Day 4: Scripts, Automation & Cleanup

## Overview
Day 4 focuses on creating clean automation scripts, removing obsolete files, and preparing the project for deployment.

## Prerequisites Checklist
- [ ] Day 3 tasks completed successfully  
- [ ] Test suite running and passing
- [ ] Documentation organized and complete
- [ ] Git commits from Days 1-3 exist

## Tasks

### 1. Morning Status Check (15 minutes)
```bash
# Task 1.1: Verify test status
cd /Users/khunter/claude/mac_notifications_clean/refactored
pytest mac_notifications/tests/ --tb=short

# Task 1.2: Check documentation
ls -la mac_notifications/docs/

# Task 1.3: Start Day 4 log
echo "# Day 4 Start - $(date)" >> REFACTORING/migration_log_day4.md
echo "Test Status: $(pytest mac_notifications/tests/ -q | tail -1)" >> REFACTORING/migration_log_day4.md
```

### 2. Create Installation Scripts (1.5 hours)

#### Task 2.1: Main Installation Script
```bash
# mac_notifications/scripts/install.sh
#!/bin/bash
set -e

echo "Mac Notifications System Installer"
echo "=================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install package in development mode
echo "Installing mac_notifications package..."
pip install -e .

# Create data directories
echo "Creating data directories..."
mkdir -p data/logs
mkdir -p data/backups

# Initialize database
echo "Initializing database..."
python -m mac_notifications.database.migrations init

echo "Installation complete!"
echo "To start the daemon: ./scripts/start_daemon.sh"
```

#### Task 2.2: Daemon Management Scripts
```bash
# mac_notifications/scripts/start_daemon.sh
#!/bin/bash
source venv/bin/activate
python -m mac_notifications.daemon.notification_daemon \
    --db data/notifications.db \
    --log data/logs/daemon.log \
    --pid data/daemon.pid

# mac_notifications/scripts/stop_daemon.sh
#!/bin/bash
if [ -f data/daemon.pid ]; then
    pid=$(cat data/daemon.pid)
    kill $pid
    rm data/daemon.pid
    echo "Daemon stopped (PID: $pid)"
else
    echo "No daemon PID file found"
fi

# mac_notifications/scripts/restart_daemon.sh
#!/bin/bash
./scripts/stop_daemon.sh
sleep 2
./scripts/start_daemon.sh
```

#### Task 2.3: LaunchD Integration
```bash
# mac_notifications/scripts/create_launchd_plist.sh
#!/bin/bash
cat > ~/Library/LaunchAgents/com.user.mac-notifications.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.mac-notifications</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/scripts/start_daemon.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$(pwd)/data/logs/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>$(pwd)/data/logs/launchd.err.log</string>
</dict>
</plist>
EOF

echo "LaunchD plist created. To install:"
echo "launchctl load ~/Library/LaunchAgents/com.user.mac-notifications.plist"
```

### 3. Create Development Scripts (1 hour)

#### Task 3.1: Development Environment Setup
```bash
# mac_notifications/scripts/setup_dev.sh
#!/bin/bash
# Development environment setup
pip install -r requirements-dev.txt
pip install -e ".[dev]"
pre-commit install

# mac_notifications/scripts/run_tests.sh
#!/bin/bash
pytest tests/ -v --cov=src --cov-report=html

# mac_notifications/scripts/lint.sh
#!/bin/bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

#### Task 3.2: Database Management Scripts
```bash
# mac_notifications/scripts/db_backup.sh
#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
cp data/notifications.db data/backups/notifications_${timestamp}.db
echo "Database backed up to data/backups/notifications_${timestamp}.db"

# mac_notifications/scripts/db_migrate.sh
#!/bin/bash
source venv/bin/activate
python -m mac_notifications.database.migrations upgrade
```

### 4. Cleanup Obsolete Files (2 hours)

#### Task 4.1: Create Cleanup Manifest
```bash
# REFACTORING/cleanup_manifest.md
echo "# Cleanup Manifest - $(date)" > REFACTORING/cleanup_manifest.md

# List files to remove
echo "## Debug Scripts to Remove" >> REFACTORING/cleanup_manifest.md
ls -la check_*.py >> REFACTORING/cleanup_manifest.md
ls -la debug_*.py >> REFACTORING/cleanup_manifest.md
ls -la analyze_*.py >> REFACTORING/cleanup_manifest.md

echo "## Test Files to Remove" >> REFACTORING/cleanup_manifest.md
ls -la test_*.py >> REFACTORING/cleanup_manifest.md

echo "## Old Capture Files" >> REFACTORING/cleanup_manifest.md
ls -la notification_capture_*.json >> REFACTORING/cleanup_manifest.md
ls -la log_dump_*.json >> REFACTORING/cleanup_manifest.md

echo "## Checkpoint Files" >> REFACTORING/cleanup_manifest.md
ls -la *CHECKPOINT*.md >> REFACTORING/cleanup_manifest.md
ls -la SESSION_*.md >> REFACTORING/cleanup_manifest.md
```

#### Task 4.2: Archive Important Files
```bash
# Create archive directory
mkdir -p ARCHIVE/debug_scripts
mkdir -p ARCHIVE/old_captures
mkdir -p ARCHIVE/checkpoints

# Move files to archive
mv check_*.py ARCHIVE/debug_scripts/
mv debug_*.py ARCHIVE/debug_scripts/
mv analyze_*.py ARCHIVE/debug_scripts/
mv notification_capture_*.json ARCHIVE/old_captures/
mv *CHECKPOINT*.md ARCHIVE/checkpoints/

# Create archive README
echo "# Archive - $(date)" > ARCHIVE/README.md
echo "Files archived during refactoring" >> ARCHIVE/README.md
```

#### Task 4.3: Remove Obsolete Files
```bash
# Remove old test files (now in tests/)
rm -f test_*.py

# Remove old captures and dumps
rm -f log_dump_*.json

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find . -name "*.pyc" -delete

# Remove old PID and log files
rm -f *.pid
rm -f *.log

# Remove backup files
rm -f *.bak
rm -f *.old
```

### 5. Create Package Configuration (1 hour)

#### Task 5.1: Create setup.py
```python
# mac_notifications/setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mac-notifications",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Mac notification monitoring system with MCP server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mac-notifications",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp",
        "psutil",
        "python-dotenv",
        # Add all requirements
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
    },
    entry_points={
        "console_scripts": [
            "mac-notifications-daemon=mac_notifications.daemon:main",
            "mac-notifications-server=mac_notifications.mcp_server:main",
        ],
    },
)
```

#### Task 5.2: Create requirements.txt
```txt
# mac_notifications/requirements.txt
# Core dependencies
mcp>=0.1.0
psutil>=5.9.0
python-dotenv>=0.19.0

# Database
# (sqlite3 is built-in)

# Testing (move to requirements-dev.txt)
# pytest>=6.0
# pytest-cov>=3.0

# Development (move to requirements-dev.txt)
# black>=22.0
# flake8>=4.0
# mypy>=0.910
```

#### Task 5.3: Create MANIFEST.in
```txt
# mac_notifications/MANIFEST.in
include README.md
include LICENSE
include requirements.txt
recursive-include src *.py
recursive-include docs *.md
recursive-include config *.json
recursive-exclude * __pycache__
recursive-exclude * *.pyc
```

### 6. Final Organization (1 hour)

#### Task 6.1: Create .gitignore
```gitignore
# mac_notifications/.gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs and databases
*.log
data/notifications.db
data/logs/*
!data/logs/.gitkeep

# OS
.DS_Store

# Project specific
*.pid
.env
```

#### Task 6.2: Create CI/CD Configuration
```yaml
# mac_notifications/.github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### 7. Validation & Documentation (45 minutes)

#### Task 7.1: Create Migration Guide
```markdown
# REFACTORING/MIGRATION_GUIDE.md
# Migration Guide from Old Structure

## For Users
1. Stop the old daemon
2. Backup your database
3. Install the new version
4. Update Claude Desktop config

## For Developers
1. Update import paths
2. New feature location: src/features/
3. New test location: tests/

## Breaking Changes
- Database path changed
- Import paths changed
- Configuration location changed
```

#### Task 7.2: Update Changelog
```markdown
# mac_notifications/CHANGELOG.md
# Changelog

## [2.0.0] - 2024-XX-XX
### Changed
- Complete project restructure
- Modular architecture
- Improved test coverage
- Better documentation

### Added
- Package installation support
- CI/CD pipeline
- Development scripts
- Comprehensive examples

### Removed
- Obsolete debug scripts
- Duplicate code
- Old test files
```

### 8. End of Day Validation (30 minutes)

#### Task 8.1: Clean Install Test
```bash
# Test installation from scratch
cd /tmp
git clone /path/to/mac_notifications
cd mac_notifications
./scripts/install.sh
./scripts/run_tests.sh
```

#### Task 8.2: Final Cleanup Check
```bash
# Verify no obsolete files remain
find . -name "*.pyc" -o -name "__pycache__" | wc -l  # Should be 0
ls -la *.py | wc -l  # Should be minimal
```

#### Task 8.3: Git Commit
```bash
git add .
git add -u  # Stage deletions
git commit -m "Day 4: Scripts, automation, and cleanup complete"
```

## Deliverables
- [ ] Installation scripts created and tested
- [ ] Daemon management scripts working
- [ ] Development scripts created
- [ ] All obsolete files removed or archived
- [ ] Package configuration complete
- [ ] CI/CD pipeline configured
- [ ] .gitignore properly configured
- [ ] Migration guide written

## Notes for Tomorrow
- Final integration testing
- Performance benchmarking
- Deploy to production
- Update Claude Desktop configuration
- Final documentation review
