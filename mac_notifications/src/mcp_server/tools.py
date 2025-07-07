"""
Tool definitions for the MCP server
"""

import mcp.types as types


# Define all available tools
TOOL_DEFINITIONS = [
    # Core tools
    types.Tool(
        name="start_notification_monitoring",
        description="Start the notification monitoring daemon",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="stop_notification_monitoring",
        description="Stop the notification monitoring daemon",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="check_daemon_status",
        description="Check if the notification daemon is running",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="get_recent_notifications",
        description="Get recent notifications from the database",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "number", "description": "Maximum number to return", "default": 10},
                "priority_filter": {"type": "string", "description": "Filter by priority: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', or 'important'"},
                "format": {"type": "string", "description": "Output format: 'terminal' (default), 'html', 'markdown', or 'json'", "default": "terminal"},
                "sort_by": {"type": "string", "description": "Sort order: 'priority' (default) or 'time'", "default": "priority"}
            },
        },
    ),
    types.Tool(
        name="get_priority_notifications",
        description="Get high priority notifications (CRITICAL and HIGH levels) with formatting",
        inputSchema={
            "type": "object",
            "properties": {
                "format": {"type": "string", "description": "Output format: 'terminal' (default), 'html', 'markdown', or 'json'", "default": "terminal"}
            }
        },
    ),
    types.Tool(
        name="get_notification_stats",
        description="Get notification statistics including priority breakdown",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="create_test_notification",
        description="Create a test notification",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title", "default": "Test"},
                "subtitle": {"type": "string", "description": "Subtitle", "default": "MCP Test"},
                "text": {"type": "string", "description": "Body text", "default": "Test notification"}
            },
        },
    ),
    
    # Search tools
    types.Tool(
        name="get_notifications_by_keyword",
        description="Search notifications by keyword",
        inputSchema={
            "type": "object",
            "properties": {"keyword": {"type": "string", "description": "Keyword to search"}},
            "required": ["keyword"]
        },
    ),
    types.Tool(
        name="search_notifications_by_app",
        description="Search notifications by app",
        inputSchema={
            "type": "object",
            "properties": {"app": {"type": "string", "description": "App name or identifier"}},
            "required": ["app"]
        },
    ),
    types.Tool(
        name="enhanced_search",
        description="Search notifications using natural language queries",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query (e.g. 'critical alerts from yesterday', 'messages from amy but not dental')"},
                "limit": {"type": "number", "description": "Maximum results to return", "default": 50},
                "format": {"type": "string", "description": "Output format: 'terminal', 'html', 'markdown', or 'json'", "default": "terminal"}
            },
            "required": ["query"]
        },
    ),
    types.Tool(
        name="get_grouped_notifications",
        description="Get notifications grouped by similarity to reduce clutter",
        inputSchema={
            "type": "object",
            "properties": {
                "hours": {"type": "number", "description": "How many hours back to look", "default": 4},
                "time_window": {"type": "number", "description": "Group notifications within this many minutes", "default": 30},
                "min_group_size": {"type": "number", "description": "Minimum notifications to form a group", "default": 2},
                "format": {"type": "string", "description": "Output format", "default": "terminal"}
            },
        },
    ),
    
    # Batch action tools
    types.Tool(
        name="batch_mark_read",
        description="Mark multiple notifications as read based on selection criteria",
        inputSchema={
            "type": "object",
            "properties": {
                "selection_type": {
                    "type": "string", 
                    "description": "Selection method: 'app', 'app_pattern', 'priority', 'older_than', 'search', 'ids'",
                    "enum": ["app", "app_pattern", "priority", "older_than", "search", "ids"]
                },
                "selection_value": {
                    "type": "string", 
                    "description": "Value for selection (e.g., app name, priority level, '7d' for older_than)"
                },
                "dry_run": {
                    "type": "boolean", 
                    "description": "Preview what would be affected without making changes", 
                    "default": False
                }
            },
            "required": ["selection_type", "selection_value"]
        },
    ),
    types.Tool(
        name="batch_mark_unread",
        description="Mark multiple notifications as unread based on selection criteria",
        inputSchema={
            "type": "object",
            "properties": {
                "selection_type": {
                    "type": "string", 
                    "description": "Selection method: 'app', 'app_pattern', 'priority', 'older_than', 'search', 'ids'",
                    "enum": ["app", "app_pattern", "priority", "older_than", "search", "ids"]
                },
                "selection_value": {
                    "type": "string", 
                    "description": "Value for selection"
                },
                "dry_run": {
                    "type": "boolean", 
                    "description": "Preview what would be affected", 
                    "default": False
                }
            },
            "required": ["selection_type", "selection_value"]
        },
    ),
    types.Tool(
        name="batch_archive",
        description="Archive multiple notifications based on selection criteria",
        inputSchema={
            "type": "object",
            "properties": {
                "selection_type": {
                    "type": "string", 
                    "description": "Selection method: 'app', 'app_pattern', 'priority', 'older_than', 'search', 'ids'",
                    "enum": ["app", "app_pattern", "priority", "older_than", "search", "ids"]
                },
                "selection_value": {
                    "type": "string", 
                    "description": "Value for selection (e.g., '30d' for notifications older than 30 days)"
                },
                "dry_run": {
                    "type": "boolean", 
                    "description": "Preview what would be archived", 
                    "default": False
                }
            },
            "required": ["selection_type", "selection_value"]
        },
    ),
    types.Tool(
        name="batch_delete",
        description="Delete multiple notifications based on selection criteria (requires confirmation)",
        inputSchema={
            "type": "object",
            "properties": {
                "selection_type": {
                    "type": "string", 
                    "description": "Selection method: 'app', 'app_pattern', 'priority', 'older_than', 'search', 'ids'",
                    "enum": ["app", "app_pattern", "priority", "older_than", "search", "ids"]
                },
                "selection_value": {
                    "type": "string", 
                    "description": "Value for selection"
                },
                "confirm": {
                    "type": "boolean", 
                    "description": "Must be true to execute deletion", 
                    "default": False
                },
                "dry_run": {
                    "type": "boolean", 
                    "description": "Preview what would be deleted", 
                    "default": False
                }
            },
            "required": ["selection_type", "selection_value"]
        },
    ),
    types.Tool(
        name="batch_update_priority",
        description="Update priority for multiple notifications based on selection criteria",
        inputSchema={
            "type": "object",
            "properties": {
                "selection_type": {
                    "type": "string", 
                    "description": "Selection method: 'app', 'app_pattern', 'priority', 'older_than', 'search', 'ids'",
                    "enum": ["app", "app_pattern", "priority", "older_than", "search", "ids"]
                },
                "selection_value": {
                    "type": "string", 
                    "description": "Value for selection"
                },
                "new_priority": {
                    "type": "string", 
                    "description": "New priority level: CRITICAL, HIGH, MEDIUM, or LOW",
                    "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                },
                "dry_run": {
                    "type": "boolean", 
                    "description": "Preview what would be updated", 
                    "default": False
                }
            },
            "required": ["selection_type", "selection_value", "new_priority"]
        },
    ),
    
    # Smart summary tools
    types.Tool(
        name="get_smart_summary",
        description="Generate an AI-powered summary of notifications for any time period",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range": {
                    "type": "string", 
                    "description": "Time range like '1h', '24h', '7d'", 
                    "default": "1h"
                },
                "detail_level": {
                    "type": "string", 
                    "description": "Detail level: 'brief', 'standard', or 'detailed'",
                    "enum": ["brief", "standard", "detailed"],
                    "default": "standard"
                },
                "focus_apps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of apps to focus on"
                }
            },
        },
    ),
    types.Tool(
        name="get_hourly_digest",
        description="Get a quick summary of notifications from the last hour",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="get_daily_digest",
        description="Get a comprehensive summary of notifications from the last 24 hours with patterns and insights",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="get_executive_brief",
        description="Get an ultra-concise executive summary focusing only on critical items",
        inputSchema={"type": "object", "properties": {}},
    ),
    
    # Analytics tools
    types.Tool(
        name="get_analytics_dashboard",
        description="Generate a comprehensive analytics dashboard with charts and insights",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "number",
                    "description": "Number of days to analyze",
                    "default": 7
                },
                "output_format": {
                    "type": "string",
                    "description": "Output format: 'html' (with charts), 'text', or 'json'",
                    "enum": ["html", "text", "json"],
                    "default": "html"
                }
            },
        },
    ),
    types.Tool(
        name="get_notification_metrics",
        description="Get key notification metrics and statistics",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "number",
                    "description": "Number of days to analyze",
                    "default": 7
                }
            },
        },
    ),
    types.Tool(
        name="get_hourly_heatmap",
        description="Get hourly notification pattern data for heatmap visualization",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "number",
                    "description": "Number of days to analyze",
                    "default": 7
                }
            },
        },
    ),
    types.Tool(
        name="get_app_analytics",
        description="Get detailed analytics for each app including distribution and patterns",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "number",
                    "description": "Number of days to analyze",
                    "default": 7
                }
            },
        },
    ),
    types.Tool(
        name="get_productivity_report",
        description="Get productivity metrics including focus time analysis and interruption patterns",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "number",
                    "description": "Number of days to analyze",
                    "default": 7
                }
            },
        },
    ),
]