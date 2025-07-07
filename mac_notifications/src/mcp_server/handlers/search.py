"""
Search and filtering handlers for MCP server
"""

import json
from typing import List
from datetime import datetime
import mcp.types as types


async def handle_get_notifications_by_keyword(server, arguments: dict) -> List[types.TextContent]:
    """Search notifications by keyword"""
    keyword = arguments.get("keyword", "")
    result = server.search_notifications(keyword=keyword)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_search_notifications_by_app(server, arguments: dict) -> List[types.TextContent]:
    """Search notifications by app"""
    app = arguments.get("app", "")
    result = server.search_notifications(app=app)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_enhanced_search(server, arguments: dict) -> List[types.TextContent]:
    """Execute natural language search"""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 50)
    format_type = arguments.get("format", "terminal")
    
    result = server.enhanced_search(query, limit, format_type)
    
    if format_type in ["terminal", "html", "markdown"] and 'formatted_output' in result:
        return [types.TextContent(type="text", text=result['formatted_output'])]
    else:
        # Custom JSON encoder to handle datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.strftime('%Y-%m-%d %H:%M:%S')
                return super(DateTimeEncoder, self).default(obj)
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder))]


async def handle_get_grouped_notifications(server, arguments: dict) -> List[types.TextContent]:
    """Get grouped notifications"""
    hours = arguments.get("hours", 4)
    time_window = arguments.get("time_window", 30)
    min_group_size = arguments.get("min_group_size", 2)
    format_type = arguments.get("format", "terminal")
    
    result = server.get_grouped_notifications(hours, time_window, min_group_size, format_type)
    
    # Custom JSON encoder to handle datetime objects
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            return super(DateTimeEncoder, self).default(obj)
    
    return [types.TextContent(type="text", text=json.dumps(result, indent=2, cls=DateTimeEncoder))]


# Export handlers
SEARCH_HANDLERS = {
    "get_notifications_by_keyword": handle_get_notifications_by_keyword,
    "search_notifications_by_app": handle_search_notifications_by_app,
    "enhanced_search": handle_enhanced_search,
    "get_grouped_notifications": handle_get_grouped_notifications,
}
