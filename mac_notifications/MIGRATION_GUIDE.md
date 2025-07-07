# Migration Guide from Old Structure

## For Users

### Step 1: Stop the Old Daemon
```bash
# If using the old start_daemon.sh
./stop_daemon.sh

# Or manually kill the process
ps aux | grep notification_daemon
kill <PID>
```

### Step 2: Backup Your Database
```bash
cp notifications.db notifications_backup_$(date +%Y%m%d).db
```

### Step 3: Install the New Version
```bash
cd mac_notifications
./scripts/install.sh
```

### Step 4: Update Claude Desktop Config
Update your Claude Desktop configuration to point to the new server location:
```json
{
  "mcpServers": {
    "notifications": {
      "command": "python",
      "args": ["-m", "mac_notifications.mcp_server"],
      "cwd": "/path/to/mac_notifications"
    }
  }
}
```

## For Developers

### Import Path Changes
Old structure:
```python
from notification_mcp_server import NotificationMCPServer
from features.enhanced_search import enhanced_search
```

New structure:
```python
from mac_notifications.mcp_server.server import NotificationMCPServer
from mac_notifications.features.enhanced_search import enhanced_search
```

### Feature Locations
- Features moved from `/features/` to `/mac_notifications/src/features/`
- Tests moved from root to `/mac_notifications/tests/`
- Configuration in `/mac_notifications/config/`

### Database Path
- Old: `notifications.db` in project root
- New: `mac_notifications/data/notifications.db`

## Breaking Changes

1. **Import Paths** - All imports must be updated to use the new module structure
2. **Database Location** - Database is now in `data/` subdirectory
3. **Configuration** - Settings now use environment variables via `.env` file
4. **Script Locations** - All scripts are now in `scripts/` directory
5. **Test Organization** - Tests are organized into unit/integration subdirectories

## Feature Mapping

| Old Feature File | New Location |
|-----------------|--------------|
| features/priority_scoring.py | src/features/priority_scoring.py |
| features/enhanced_search.py | src/features/enhanced_search.py |
| features/templates.py | src/features/templates.py |
| features/grouping.py | src/features/grouping.py |
| features/batch_actions.py | src/features/batch_actions.py |
| features/smart_summaries.py | src/features/smart_summaries.py |
| features/analytics.py | src/features/analytics.py |

## MCP Server Updates

The MCP server has been modularized with separate handlers:
- Core operations: `src/mcp_server/handlers/core.py`
- Search operations: `src/mcp_server/handlers/search.py`
- Batch operations: `src/mcp_server/handlers/batch.py`
- Summary operations: `src/mcp_server/handlers/summary.py`
- Analytics operations: `src/mcp_server/handlers/analytics.py`

## Getting Started

1. Clone the new repository
2. Run `./scripts/install.sh`
3. Copy your old database to `data/notifications.db`
4. Start the daemon: `./scripts/start_daemon.sh`
5. Update your Claude Desktop configuration
6. Test with: `python examples/basic_usage.py`

## Support

For issues with migration, please check:
- The user guide: `docs/user_guide.md`
- Example scripts: `examples/`
- Test suite: Run `./scripts/run_tests.sh` to verify installation
