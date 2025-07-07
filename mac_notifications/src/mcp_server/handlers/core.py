"""
Core MCP handlers for basic notification operations
"""

import json
import subprocess
from typing import List
import mcp.types as types


async def handle_start_notification_monitoring(server, arguments: dict) -> List[types.TextContent]:
    """Start the notification daemon"""
    result = server.start_daemon()
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_stop_notification_monitoring(server, arguments: dict) -> List[types.TextContent]:
    """Stop the notification daemon"""
    result = server.stop_daemon()
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_check_daemon_status(server, arguments: dict) -> List[types.TextContent]:
    """Check daemon status"""
    status = server._check_daemon_status()
    return [types.TextContent(type="text", text=json.dumps(status, indent=2))]


async def handle_get_recent_notifications(server, arguments: dict) -> List[types.TextContent]:
    """Get recent notifications"""
    limit = arguments.get("limit", 10)
    priority_filter = arguments.get("priority_filter", None)
    format_type = arguments.get("format", "terminal")
    sort_by = arguments.get("sort_by", "priority")
    
    # For terminal format, get the formatted output
    if format_type in ["terminal", "html", "markdown"]:
        formatted = server.get_formatted_notifications(limit, priority_filter, format_type, sort_by)
        return [types.TextContent(type="text", text=formatted)]
    else:
        # Return raw JSON data
        result = server.get_recent_notifications(limit, priority_filter, use_templates=False, sort_by=sort_by)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_priority_notifications(server, arguments: dict) -> List[types.TextContent]:
    """Get high priority notifications"""
    format_type = arguments.get("format", "terminal")
    
    if format_type in ["terminal", "html", "markdown"]:
        formatted = server.get_formatted_notifications(20, "important", format_type)
        return [types.TextContent(type="text", text=formatted)]
    else:
        result = server.get_priority_notifications(format_type="json")
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_notification_stats(server, arguments: dict) -> List[types.TextContent]:
    """Get notification statistics"""
    result = server.get_statistics()
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_create_test_notification(server, arguments: dict) -> List[types.TextContent]:
    """Create a test notification using AppleScript"""
    title = arguments.get("title", "Test Notification")
    subtitle = arguments.get("subtitle", "MCP Server Test")
    text = arguments.get("text", "This is a test notification")
    
    script_parts = [f'display notification "{text}"']
    script_parts.append(f'with title "{title}"')
    if subtitle:
        script_parts.append(f'subtitle "{subtitle}"')
    
    script = " ".join(script_parts)
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            return [types.TextContent(type="text", text=f"✅ Test notification created: {title}")]
        else:
            return [types.TextContent(type="text", text=f"❌ Failed to create notification: {result.stderr}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"❌ Error creating notification: {str(e)}")]


# Export handlers
CORE_HANDLERS = {
    "start_notification_monitoring": handle_start_notification_monitoring,
    "stop_notification_monitoring": handle_stop_notification_monitoring,
    "check_daemon_status": handle_check_daemon_status,
    "get_recent_notifications": handle_get_recent_notifications,
    "get_priority_notifications": handle_get_priority_notifications,
    "get_notification_stats": handle_get_notification_stats,
    "create_test_notification": handle_create_test_notification,
}
