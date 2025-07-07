# Day 2: MCP Server, Database Layer & Configuration

## Overview
Day 2 focuses on consolidating the MCP server, creating a proper database abstraction layer, and implementing centralized configuration management.

## Prerequisites Checklist
- [ ] Day 1 tasks completed successfully
- [ ] New directory structure in place
- [ ] Daemon code consolidated
- [ ] Git commit from Day 1 exists

## Tasks

### 1. Morning Status Check (15 minutes)
```bash
# Task 1.1: Verify Day 1 work
cd /Users/khunter/claude/mac_notifications_clean/refactored
git status
git log --oneline -5

# Task 1.2: Document any overnight thoughts/issues
echo "# Day 2 Start Notes - $(date)" >> REFACTORING/migration_log_day2.md
```

### 2. MCP Server Consolidation (2.5 hours)

#### Task 2.1: Analyze MCP Server Versions
```bash
# Document MCP versions
echo "# MCP Server Analysis" > REFACTORING/mcp_analysis.md
ls -la notification_mcp_server*.py >> REFACTORING/mcp_analysis.md
wc -l notification_mcp_server*.py >> REFACTORING/mcp_analysis.md
```

#### Task 2.2: Create MCP Server Module Structure
```python
# mac_notifications/src/mcp_server/server.py
# Main NotificationMCPServer class
# Core server logic and initialization

# mac_notifications/src/mcp_server/handlers.py
# All async handler functions
# Tool routing logic

# mac_notifications/src/mcp_server/tools.py
# Tool definitions and schemas
```

#### Task 2.3: Refactor Handler Functions
- Group handlers by feature (analytics, batch, search, etc.)
- Create handler base class for common functionality
- Implement proper error handling patterns

#### Task 2.4: Update Tool Definitions
- Move tool schemas to separate configuration
- Create tool registry pattern
- Document each tool's purpose and parameters

### 3. Database Abstraction Layer (2 hours)

#### Task 3.1: Create Database Models
```python
# mac_notifications/src/database/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Notification:
    rec_id: int
    app_identifier: str
    delivered_time: datetime
    title: Optional[str]
    subtitle: Optional[str]
    body: Optional[str]
    category: Optional[str]
    thread: Optional[str]
    priority_score: Optional[float]
    priority_level: Optional[str]
    priority_factors: Optional[List[str]]
    is_read: bool = False
    is_archived: bool = False
    created_at: datetime = None

@dataclass
class DaemonMetadata:
    key: str
    value: str
    updated_at: datetime
```

#### Task 3.2: Create Database Connection Manager
```python
# mac_notifications/src/database/connection.py
import sqlite3
from contextlib import contextmanager
from typing import Generator

class DatabaseConnection:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
```

#### Task 3.3: Create Repository Pattern
```python
# mac_notifications/src/database/repositories.py
class NotificationRepository:
    """Handle all notification-related database operations"""
    
    def get_recent(self, limit: int = 10) -> List[Notification]:
        pass
    
    def search(self, query: str) -> List[Notification]:
        pass
    
    def update_priority(self, rec_id: int, priority: str) -> bool:
        pass
```

#### Task 3.4: Create Migration System
```python
# mac_notifications/src/database/migrations.py
class MigrationManager:
    """Handle database schema migrations"""
    
    def get_current_version(self) -> int:
        pass
    
    def migrate_to_version(self, target_version: int) -> None:
        pass
```

### 4. Configuration Management (1.5 hours)

#### Task 4.1: Create Comprehensive Settings
```python
# mac_notifications/src/config/settings.py
import os
from pathlib import Path
from typing import Optional

class Settings:
    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = DATA_DIR / "logs"
    
    # Database
    DEFAULT_DB_PATH = DATA_DIR / "notifications.db"
    DB_TIMEOUT = 30.0
    
    # Daemon
    DAEMON_UPDATE_INTERVAL = 30
    DAEMON_BATCH_SIZE = 100
    MAX_NOTIFICATION_AGE_DAYS = 30
    
    # MCP Server
    MCP_SERVER_NAME = "notification-mcp-server"
    MCP_SERVER_VERSION = "2.0.0"
    
    # Features
    PRIORITY_SCORING_ENABLED = True
    SMART_SUMMARIES_ENABLED = True
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Load settings from environment variables"""
        pass
```

#### Task 4.2: Create Environment Support
```bash
# Create .env.example
cat > mac_notifications/.env.example << 'EOF'
# Database
DB_PATH=/path/to/custom/notifications.db

# Daemon
DAEMON_UPDATE_INTERVAL=30
MAX_NOTIFICATION_AGE_DAYS=30

# Logging
LOG_LEVEL=INFO

# Features
PRIORITY_SCORING_ENABLED=true
SMART_SUMMARIES_ENABLED=true
EOF
```

#### Task 4.3: Update Claude Desktop Configuration
```json
# mac_notifications/config/claude_desktop_config.json
{
  "mcpServers": {
    "notification-server": {
      "command": "python",
      "args": [
        "-m",
        "mac_notifications.mcp_server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mac_notifications",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 5. Update Import Paths (1 hour)

#### Task 5.1: Create Import Updater Script
```python
# REFACTORING/update_imports.py
import re
from pathlib import Path

def update_imports_in_file(file_path: Path):
    """Update import statements to use new structure"""
    pass

# Update all Python files
```

#### Task 5.2: Fix Circular Dependencies
- Identify circular imports
- Refactor to break cycles
- Document dependency graph

### 6. Integration Testing (1 hour)

#### Task 6.1: Create Integration Tests
```python
# mac_notifications/tests/integration/test_daemon_db.py
"""Test daemon with database integration"""

# mac_notifications/tests/integration/test_mcp_features.py
"""Test MCP server with all features"""
```

#### Task 6.2: Test Data Flow
- Test notification capture → database → MCP server → client
- Verify all features work with new structure

### 7. Documentation Updates (45 minutes)

#### Task 7.1: Update Architecture Document
```markdown
# mac_notifications/docs/architecture.md
## Database Layer
- Repository pattern for data access
- Migration system for schema updates
- Connection pooling for performance

## Configuration System
- Environment variable support
- Centralized settings class
- Feature flags
```

#### Task 7.2: Create Database Schema Document
```markdown
# mac_notifications/docs/database_schema.md
# Document all tables, fields, and relationships
```

### 8. End of Day Validation (30 minutes)

#### Task 8.1: Run All Tests
```bash
cd mac_notifications
python -m pytest tests/unit/
python -m pytest tests/integration/
```

#### Task 8.2: Test MCP Server
```bash
# Start the new MCP server
python -m mac_notifications.mcp_server

# In another terminal, check it responds
# Document any issues
```

#### Task 8.3: Git Commit
```bash
git add .
git commit -m "Day 2: MCP server consolidation, database layer, and configuration complete"
```

## Deliverables
- [ ] MCP server code consolidated and refactored
- [ ] Database abstraction layer implemented
- [ ] Repository pattern for data access
- [ ] Migration system created
- [ ] Centralized configuration with env support
- [ ] Import paths updated throughout codebase
- [ ] Integration tests passing
- [ ] Documentation updated

## Known Issues to Address Tomorrow
- Move all tests to new structure
- Consolidate all documentation
- Create proper test fixtures
- Remove obsolete debug scripts

## Notes
- If database layer takes longer, defer some MCP handler refactoring to Day 3
- Keep both old and new database access code until fully tested
- Document any breaking changes for migration guide
