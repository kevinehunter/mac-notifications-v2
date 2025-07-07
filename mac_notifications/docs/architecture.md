# Mac Notifications System Architecture

## Overview

The Mac Notifications system is designed as a modular, extensible platform for monitoring, analyzing, and managing macOS notifications. It follows a clean architecture pattern with clear separation of concerns.

## System Components

### 1. Notification Daemon (`src/daemon/`)
The daemon is the core component that continuously monitors the macOS notification database.

- **notification_daemon.py**: Main daemon process
  - `NotificationDaemon`: Orchestrates the monitoring process
  - `DatabaseManager`: Handles all database operations
  - `NotificationExtractor`: Extracts notifications from macOS
  - `PriorityScorer`: Calculates notification priorities

- **daemon_manager.py**: Process lifecycle management
  - Start/stop/restart daemon
  - Health monitoring
  - Process cleanup

### 2. MCP Server (`src/mcp_server/`)
Provides the Model Context Protocol interface for Claude Desktop integration.

- **server.py**: Main MCP server implementation
- **handlers.py**: Request handlers for all MCP tools
- **tools.py**: Tool definitions and schemas

### 3. Features (`src/features/`)
Modular feature implementations that can be enabled/disabled:

- **priority_scoring.py**: Intelligent notification prioritization
- **templates.py**: Rich formatting for different output types
- **enhanced_search.py**: Natural language search capabilities
- **grouping.py**: Smart notification grouping
- **batch_actions.py**: Bulk operations on notifications
- **smart_summaries.py**: AI-powered notification summaries
- **analytics.py**: Statistical analysis and reporting

### 4. Database Layer (`src/database/`)
Abstraction layer for all data operations:

- **models.py**: Data models (Notification, DaemonMetadata, etc.)
- **connection.py**: Database connection management
- **repositories.py**: Repository pattern for data access
- **migrations.py**: Schema version management

### 5. Configuration (`src/config/`)
Centralized configuration management:

- **settings.py**: All application settings
- Environment variable support
- JSON configuration files
- Feature flags

### 6. Utilities (`src/utils/`)
Shared utilities and helpers:

- **logging.py**: Logging configuration
- **helpers.py**: Common utility functions

## Data Flow

```
macOS Notification Database
           ↓
    NotificationExtractor
           ↓
      PriorityScorer
           ↓
     DatabaseManager
           ↓
    Local SQLite DB
           ↓
      MCP Server
           ↓
    Claude Desktop
```

## Database Schema

### notifications Table
- `id`: Primary key
- `rec_id`: macOS record ID (unique)
- `app_identifier`: Source application
- `delivered_time`: When notification was delivered
- `title`, `subtitle`, `body`: Notification content
- `category`, `thread`: Grouping information
- `priority_score`, `priority_level`, `priority_factors`: Priority data
- `is_read`, `is_archived`: Status flags
- `raw_data`: Original plist data
- `created_at`, `updated_at`: Timestamps

### daemon_metadata Table
- `key`: Metadata key
- `value`: Metadata value
- `updated_at`: Last update time

## Key Design Decisions

### 1. Separation of Daemon and Server
The daemon runs independently of the MCP server, ensuring:
- Continuous notification capture even if Claude is closed
- Better resource management
- Easier debugging and maintenance

### 2. Priority Scoring System
Multi-factor scoring based on:
- Content analysis (keywords, amounts, dates)
- Application weights
- Time decay
- Special patterns (security at night, etc.)

### 3. Modular Features
Each feature is self-contained:
- Can be enabled/disabled via configuration
- No hard dependencies between features
- Easy to add new features

### 4. Repository Pattern
Database operations go through repositories:
- Consistent data access patterns
- Easy to mock for testing
- Future-proof for different storage backends

### 5. Template System
Rich formatting for multiple output types:
- Terminal (with ANSI colors)
- HTML (for web display)
- Markdown (for documentation)

## Extension Points

### Adding New Features
1. Create new module in `src/features/`
2. Add feature flag to settings
3. Integrate with MCP server handlers
4. Add tests

### Adding New Data Sources
1. Create new extractor class
2. Implement common interface
3. Register with daemon

### Adding New Output Formats
1. Extend template system
2. Add new format type
3. Implement formatting logic

## Performance Considerations

- **Batch Processing**: Notifications processed in batches
- **Index Usage**: Strategic indexes on frequently queried columns
- **Connection Pooling**: Reuse database connections
- **Async Operations**: MCP server uses async handlers
- **Cleanup Jobs**: Regular removal of old data

## Security Considerations

- **Read-Only Access**: Only reads from macOS database
- **Sandboxed Operations**: Temporary copies for safety
- **No Network Access**: All operations are local
- **Configurable Retention**: Auto-cleanup of old data

## Error Handling

- **Graceful Degradation**: Features fail independently
- **Comprehensive Logging**: All errors logged with context
- **Recovery Mechanisms**: Auto-restart on failures
- **User Feedback**: Clear error messages in UI

## Testing Strategy

- **Unit Tests**: Each module tested independently
- **Integration Tests**: End-to-end scenarios
- **Performance Tests**: Load and stress testing
- **Mock Objects**: External dependencies mocked
