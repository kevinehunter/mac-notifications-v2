# Day 1: Foundation & Core Consolidation

## Overview
Day 1 focuses on creating the foundation for the new structure, backing up everything, and consolidating the daemon components.

## Prerequisites Checklist
- [ ] Ensure Git is installed
- [ ] Have at least 10GB free disk space for backups
- [ ] Close any running daemon instances
- [ ] Stop Claude Desktop temporarily

## Tasks

### 1. Backup & Version Control (30 minutes)
```bash
# Task 1.1: Create timestamped backup
cd /Users/khunter/claude/mac_notifications_clean
cp -r refactored refactored_backup_$(date +%Y%m%d_%H%M%S)

# Task 1.2: Initialize Git (if needed)
cd refactored
git init
git add .
git commit -m "Pre-refactoring snapshot - $(date +%Y-%m-%d)"

# Task 1.3: Create refactoring branch
git checkout -b refactoring/clean-architecture
```

### 2. Create New Directory Structure (15 minutes)
```bash
# Task 2.1: Create all directories
mkdir -p mac_notifications/{src/{daemon,mcp_server,features,database,utils},scripts,tests/{unit,integration,fixtures},docs/features,examples,data/logs,config}

# Task 2.2: Create __init__.py files
touch mac_notifications/src/__init__.py
touch mac_notifications/src/daemon/__init__.py
touch mac_notifications/src/mcp_server/__init__.py
touch mac_notifications/src/features/__init__.py
touch mac_notifications/src/database/__init__.py
touch mac_notifications/src/utils/__init__.py
touch mac_notifications/tests/__init__.py
touch mac_notifications/tests/unit/__init__.py
touch mac_notifications/tests/integration/__init__.py

# Task 2.3: Create placeholder README files
echo "# Mac Notifications Monitoring System" > mac_notifications/README.md
echo "# Installation & Setup Guide" > mac_notifications/docs/setup_guide.md
```

### 3. Consolidate Daemon Code (2 hours)

#### Task 3.1: Analyze Existing Daemon Versions
```bash
# Document daemon versions
echo "# Daemon Version Analysis" > REFACTORING/daemon_analysis.md
echo "## Files to consolidate:" >> REFACTORING/daemon_analysis.md
ls -la notification_daemon*.py >> REFACTORING/daemon_analysis.md
```

#### Task 3.2: Create Unified Daemon Module
```python
# Create the main daemon file
# mac_notifications/src/daemon/notification_daemon.py
```

Key consolidation points:
- Use notification_daemon_v2.py as base (it has priority scoring)
- Merge unique features from notification_daemon_iphone_debug.py
- Extract constants to config module
- Create proper class structure

#### Task 3.3: Extract Daemon Manager
```python
# mac_notifications/src/daemon/daemon_manager.py
# Extract process management, PID handling, and daemon lifecycle
```

#### Task 3.4: Create Database Models
```python
# mac_notifications/src/database/models.py
# Extract notification model from daemon code
```

### 4. Move and Organize Features (1 hour)

#### Task 4.1: Copy Feature Files
```bash
# Copy with better names
cp features/notification_analytics.py mac_notifications/src/features/analytics.py
cp features/batch_actions.py mac_notifications/src/features/batch_actions.py
cp features/enhanced_search.py mac_notifications/src/features/enhanced_search.py
cp features/notification_grouping.py mac_notifications/src/features/grouping.py
cp features/priority_scorer.py mac_notifications/src/features/priority_scoring.py
cp features/smart_summaries.py mac_notifications/src/features/smart_summaries.py
cp features/notification_templates.py mac_notifications/src/features/templates.py
```

#### Task 4.2: Update Feature Imports
- Change absolute imports to relative imports
- Update class names for consistency
- Remove redundant code

### 5. Create Configuration Module (45 minutes)

#### Task 5.1: Create Settings File
```python
# mac_notifications/src/config/settings.py
DEFAULT_DB_PATH = "data/notifications.db"
DAEMON_UPDATE_INTERVAL = 30
MAX_NOTIFICATION_AGE_DAYS = 30
BATCH_SIZE = 100
# ... etc
```

#### Task 5.2: Move Config Files
```bash
cp claude_desktop_config_v2.json mac_notifications/config/claude_desktop_config.json
```

### 6. Create Basic Tests (45 minutes)

#### Task 6.1: Create Test Structure
```python
# mac_notifications/tests/unit/test_daemon.py
# Basic daemon tests

# mac_notifications/tests/unit/test_features.py
# Feature module tests
```

### 7. Documentation (30 minutes)

#### Task 7.1: Create Architecture Document
```markdown
# mac_notifications/docs/architecture.md
# Document the new structure and design decisions
```

#### Task 7.2: Create Migration Log
```markdown
# REFACTORING/migration_log_day1.md
# Document what was moved/changed and any issues encountered
```

### 8. End of Day Validation (30 minutes)

#### Task 8.1: Run Basic Tests
```bash
# Test that imports work
cd mac_notifications
python -c "from src.daemon import notification_daemon"
python -c "from src.features import analytics"
```

#### Task 8.2: Git Commit
```bash
git add .
git commit -m "Day 1: Foundation and daemon consolidation complete"
```

## Deliverables
- [ ] Complete backup created
- [ ] Git repository initialized with refactoring branch
- [ ] New directory structure created
- [ ] Daemon code consolidated into single module
- [ ] Features moved to new location
- [ ] Basic configuration module created
- [ ] Initial tests created
- [ ] Documentation started

## Known Issues to Address Tomorrow
- MCP server consolidation
- Import path updates in all files
- Database connection improvements
- More comprehensive tests

## Notes
- If daemon consolidation takes longer than expected, defer feature moves to Day 2
- Keep the original files untouched until Day 4 cleanup
- Document any unexpected dependencies or issues found
