# Day 3: Testing Infrastructure & Documentation Organization

## Overview
Day 3 focuses on creating a comprehensive testing infrastructure and organizing all documentation into a coherent structure.

## Prerequisites Checklist
- [ ] Day 2 tasks completed successfully
- [ ] MCP server and database layer consolidated
- [ ] Basic integration tests passing
- [ ] Git commits from Day 1 & 2 exist

## Tasks

### 1. Morning Status Check (15 minutes)
```bash
# Task 1.1: Review current state
cd /Users/khunter/claude/mac_notifications_clean/refactored
git status
git log --oneline -10

# Task 1.2: Test current functionality
python -m mac_notifications.mcp_server --version
echo "# Day 3 Start - $(date)" >> REFACTORING/migration_log_day3.md
```

### 2. Test Inventory & Analysis (1 hour)

#### Task 2.1: Catalog All Test Files
```bash
# Find all test files
echo "# Test File Inventory" > REFACTORING/test_inventory.md
find . -name "test_*.py" -type f >> REFACTORING/test_inventory.md
find . -name "*_test.py" -type f >> REFACTORING/test_inventory.md
find . -name "check_*.py" -type f >> REFACTORING/test_inventory.md
find . -name "debug_*.py" -type f >> REFACTORING/test_inventory.md
```

#### Task 2.2: Categorize Test Files
```markdown
# REFACTORING/test_categorization.md
## Real Tests (to migrate)
- test_priority_scoring.py
- test_notification_templates.py
- test_enhanced_search.py
- test_batch_actions.py
- test_smart_summaries.py

## Debug Scripts (to convert or archive)
- debug_enhanced_search.py
- check_db_status.py
- check_recent_times.py

## Demo Scripts (to move to examples)
- demo_analytics.py
- demo_smart_summaries.py
- show_template_examples.py

## Obsolete (to delete)
- test_import_fix.py
- test_out.txt
```

### 3. Create Test Infrastructure (2 hours)

#### Task 3.1: Set Up Pytest Configuration
```ini
# mac_notifications/pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

#### Task 3.2: Create Test Fixtures
```python
# mac_notifications/tests/conftest.py
import pytest
import tempfile
import sqlite3
from pathlib import Path
from mac_notifications.src.database.connection import DatabaseConnection

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE notifications (...)''')
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink()

@pytest.fixture
def sample_notifications():
    """Provide sample notification data"""
    return [
        {
            "rec_id": 1,
            "app_identifier": "com.apple.mail",
            "title": "New Email",
            "delivered_time": "2024-01-01 10:00:00"
        },
        # ... more samples
    ]
```

#### Task 3.3: Migrate Unit Tests
```python
# mac_notifications/tests/unit/test_priority_scoring.py
import pytest
from mac_notifications.src.features.priority_scoring import PriorityScorer

class TestPriorityScoring:
    def test_calculate_score(self):
        scorer = PriorityScorer()
        # Migrate existing tests
    
    def test_priority_levels(self):
        # Add new comprehensive tests

# Repeat for each feature module
```

#### Task 3.4: Create Integration Tests
```python
# mac_notifications/tests/integration/test_end_to_end.py
import pytest
from mac_notifications.src.daemon.notification_daemon import NotificationDaemon
from mac_notifications.src.mcp_server.server import NotificationMCPServer

class TestEndToEnd:
    def test_notification_flow(self, temp_db):
        """Test complete flow from daemon to MCP server"""
        # 1. Create daemon
        # 2. Process notifications
        # 3. Query via MCP server
        # 4. Verify results
```

#### Task 3.5: Create Performance Tests
```python
# mac_notifications/tests/performance/test_search_performance.py
import pytest
import time
from mac_notifications.src.features.enhanced_search import EnhancedSearch

class TestSearchPerformance:
    @pytest.mark.performance
    def test_search_speed_large_dataset(self, large_dataset):
        """Ensure search completes within acceptable time"""
        search = EnhancedSearch()
        start = time.time()
        results = search.search("test query", limit=1000)
        duration = time.time() - start
        assert duration < 1.0  # Should complete within 1 second
```

### 4. Documentation Organization (2 hours)

#### Task 4.1: Consolidate Feature Documentation
```bash
# Create consolidated feature docs
echo "# Analytics Feature" > mac_notifications/docs/features/analytics.md
cat FEATURE3_ANALYTICS_DASHBOARD_COMPLETE.md >> mac_notifications/docs/features/analytics.md

echo "# Smart Summaries Feature" > mac_notifications/docs/features/summaries.md
cat FEATURE4_SMART_SUMMARIES_COMPLETE.md >> mac_notifications/docs/features/summaries.md

# Continue for all features...
```

#### Task 4.2: Create User Guide
```markdown
# mac_notifications/docs/user_guide.md
# Mac Notifications User Guide

## Table of Contents
1. Installation
2. Quick Start
3. Using the MCP Server
4. Feature Guide
   - Priority Notifications
   - Smart Search
   - Batch Operations
   - Analytics Dashboard
5. Troubleshooting
6. FAQ
```

#### Task 4.3: Create Developer Guide
```markdown
# mac_notifications/docs/developer_guide.md
# Developer Guide

## Architecture Overview
## Adding New Features
## Testing Guidelines
## Contribution Process
## Code Style Guide
```

#### Task 4.4: API Reference Documentation
```python
# REFACTORING/generate_api_docs.py
"""Generate API documentation from docstrings"""
import inspect
import mac_notifications.src

def generate_api_docs():
    # Extract docstrings from all modules
    # Format as markdown
    # Save to docs/api_reference.md
```

### 5. Create Example Scripts (1 hour)

#### Task 5.1: Basic Usage Examples
```python
# mac_notifications/examples/basic_usage.py
"""Basic example of using the notification system"""
from mac_notifications import NotificationDaemon, NotificationMCPServer

# Example: Start monitoring
daemon = NotificationDaemon()
daemon.start()

# Example: Query notifications
server = NotificationMCPServer()
recent = server.get_recent_notifications(limit=10)
```

#### Task 5.2: Advanced Examples
```python
# mac_notifications/examples/custom_analytics.py
"""Custom analytics and reporting example"""

# mac_notifications/examples/batch_operations.py
"""Batch operation examples"""

# mac_notifications/examples/custom_search.py
"""Advanced search examples"""
```

### 6. Test Suite Validation (1 hour)

#### Task 6.1: Run Complete Test Suite
```bash
cd mac_notifications

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest -m performance tests/
```

#### Task 6.2: Create Test Report
```markdown
# REFACTORING/test_report_day3.md
## Test Coverage Report
- Total Tests: X
- Passing: X
- Failing: X
- Coverage: X%

## Coverage by Module
- daemon: X%
- mcp_server: X%
- features: X%
- database: X%
```

### 7. Documentation Review (45 minutes)

#### Task 7.1: Create Documentation Index
```markdown
# mac_notifications/docs/index.md
# Documentation Index

## Getting Started
- [Installation Guide](setup_guide.md)
- [Quick Start](quick_start.md)

## User Documentation
- [User Guide](user_guide.md)
- [Feature Documentation](features/)

## Developer Documentation
- [Developer Guide](developer_guide.md)
- [API Reference](api_reference.md)
- [Architecture](architecture.md)

## Additional Resources
- [Examples](../examples/)
- [FAQ](faq.md)
- [Changelog](changelog.md)
```

#### Task 7.2: Review and Update README
```markdown
# mac_notifications/README.md
# Update with:
- New structure explanation
- Quick installation steps
- Link to full documentation
- Badge for test coverage
- Contributing guidelines
```

### 8. End of Day Validation (30 minutes)

#### Task 8.1: Documentation Build Test
```bash
# If using sphinx or mkdocs
cd mac_notifications/docs
mkdocs build --strict

# Check for broken links
# Verify all examples work
```

#### Task 8.2: Final Test Run
```bash
# Run all tests one more time
pytest tests/ -v --tb=short
```

#### Task 8.3: Git Commit
```bash
git add .
git commit -m "Day 3: Complete test infrastructure and documentation organization"
```

## Deliverables
- [ ] All tests migrated to new structure
- [ ] Pytest configuration complete
- [ ] Test fixtures created
- [ ] 80%+ test coverage achieved
- [ ] All documentation consolidated
- [ ] User and developer guides created
- [ ] Example scripts created
- [ ] API documentation generated

## Known Issues to Address Tomorrow
- Remove all obsolete files
- Create installation scripts
- Set up CI/CD pipeline
- Performance optimization

## Notes
- Focus on test quality over quantity
- Ensure examples are self-contained and runnable
- Document any flaky tests for later investigation
- Keep old test files until Day 4 cleanup
