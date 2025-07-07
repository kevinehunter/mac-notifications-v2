"""
Batch action handlers for MCP server
"""

import json
from typing import List
import mcp.types as types


async def handle_batch_mark_read(server, arguments: dict) -> List[types.TextContent]:
    """Mark notifications as read in batch"""
    selection_type = arguments.get("selection_type", "")
    selection_value = arguments.get("selection_value", "")
    dry_run = arguments.get("dry_run", False)
    
    result = server.batch_mark_read(selection_type, selection_value, dry_run)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_batch_mark_unread(server, arguments: dict) -> List[types.TextContent]:
    """Mark notifications as unread in batch"""
    selection_type = arguments.get("selection_type", "")
    selection_value = arguments.get("selection_value", "")
    dry_run = arguments.get("dry_run", False)
    
    result = server.batch_mark_unread(selection_type, selection_value, dry_run)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_batch_archive(server, arguments: dict) -> List[types.TextContent]:
    """Archive notifications in batch"""
    selection_type = arguments.get("selection_type", "")
    selection_value = arguments.get("selection_value", "")
    dry_run = arguments.get("dry_run", False)
    
    result = server.batch_archive(selection_type, selection_value, dry_run)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_batch_delete(server, arguments: dict) -> List[types.TextContent]:
    """Delete notifications in batch"""
    selection_type = arguments.get("selection_type", "")
    selection_value = arguments.get("selection_value", "")
    confirm = arguments.get("confirm", False)
    dry_run = arguments.get("dry_run", False)
    
    result = server.batch_delete(selection_type, selection_value, confirm, dry_run)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_batch_update_priority(server, arguments: dict) -> List[types.TextContent]:
    """Update priority for notifications in batch"""
    selection_type = arguments.get("selection_type", "")
    selection_value = arguments.get("selection_value", "")
    new_priority = arguments.get("new_priority", "MEDIUM")
    dry_run = arguments.get("dry_run", False)
    
    result = server.batch_update_priority(selection_type, selection_value, new_priority, dry_run)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


# Export handlers
BATCH_HANDLERS = {
    "batch_mark_read": handle_batch_mark_read,
    "batch_mark_unread": handle_batch_mark_unread,
    "batch_archive": handle_batch_archive,
    "batch_delete": handle_batch_delete,
    "batch_update_priority": handle_batch_update_priority,
}
