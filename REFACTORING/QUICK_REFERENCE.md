# Refactoring Quick Reference Guide

## Daily Overview

### Day 1: Foundation & Core Consolidation
- **Duration**: 7 hours
- **Focus**: Create structure, consolidate daemon
- **Key Files**: 
  - notification_daemon.py (consolidated)
  - Basic directory structure
  - Initial tests

### Day 2: MCP Server, Database & Config
- **Duration**: 8 hours  
- **Focus**: MCP consolidation, database layer
- **Key Files**:
  - mcp_server/server.py
  - database/models.py
  - config/settings.py

### Day 3: Testing & Documentation
- **Duration**: 7 hours
- **Focus**: Test infrastructure, docs organization
- **Key Files**:
  - tests/conftest.py
  - docs/user_guide.md
  - examples/*.py

### Day 4: Scripts, Automation & Cleanup
- **Duration**: 7 hours
- **Focus**: Create scripts, remove obsolete files
- **Key Files**:
  - scripts/install.sh
  - setup.py
  - requirements.txt

### Day 5: Integration & Deployment
- **Duration**: 8 hours
- **Focus**: Final testing, deployment
- **Key Files**:
  - Final integration tests
  - Claude config
  - Release package

## Critical Commands

```bash
# Start each day
cd /Users/khunter/claude/mac_notifications_clean/refactored
git checkout refactoring/clean-architecture

# End each day
git add .
git commit -m "Day X: Description"

# Test at any time
pytest mac_notifications/tests/ -v

# Quick validation
python -m mac_notifications.mcp_server --help
```

## File Mapping

| Old File | New Location |
|----------|--------------|
| notification_daemon_v2.py | src/daemon/notification_daemon.py |
| notification_mcp_server_v2.py | src/mcp_server/server.py |
| features/*.py | src/features/*.py |
| test_*.py | tests/unit/test_*.py |
| claude_desktop_config.json | config/claude_desktop_config.json |

## Risk Mitigation

1. **Before starting**: Full backup
2. **After each module**: Test imports
3. **During cleanup**: Archive before delete
4. **If something breaks**: Git reset to last good commit
5. **Emergency**: Use backup from Day 1

## Success Checkpoints

- [ ] Day 1: Can import daemon module
- [ ] Day 2: MCP server starts
- [ ] Day 3: Tests run and pass
- [ ] Day 4: Installation script works
- [ ] Day 5: Claude integration works

## Contact for Issues

- Check REFACTORING/migration_log_dayX.md for daily issues
- Review error messages in git commits
- Test incrementally, don't wait until end of day
