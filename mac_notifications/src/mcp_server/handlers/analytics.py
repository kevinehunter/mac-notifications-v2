"""
Analytics handlers for MCP server
"""

import json
from typing import List
import mcp.types as types


async def handle_get_analytics_dashboard(server, arguments: dict) -> List[types.TextContent]:
    """Generate analytics dashboard"""
    days = arguments.get("days", 7)
    output_format = arguments.get("output_format", "html")
    
    result = server.get_analytics_dashboard(days, output_format)
    
    if output_format == "html" and "html" in result:
        return [types.TextContent(type="text", text=result["html"])]
    elif output_format == "text" and "text" in result:
        return [types.TextContent(type="text", text=result["text"])]
    else:
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_notification_metrics(server, arguments: dict) -> List[types.TextContent]:
    """Get key notification metrics"""
    days = arguments.get("days", 7)
    result = server.get_notification_metrics(days)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_hourly_heatmap(server, arguments: dict) -> List[types.TextContent]:
    """Get hourly notification heatmap"""
    days = arguments.get("days", 7)
    result = server.get_hourly_heatmap(days)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_app_analytics(server, arguments: dict) -> List[types.TextContent]:
    """Get app-specific analytics"""
    days = arguments.get("days", 7)
    result = server.get_app_analytics(days)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_productivity_report(server, arguments: dict) -> List[types.TextContent]:
    """Get productivity metrics"""
    days = arguments.get("days", 7)
    result = server.get_productivity_report(days)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


# Export handlers
ANALYTICS_HANDLERS = {
    "get_analytics_dashboard": handle_get_analytics_dashboard,
    "get_notification_metrics": handle_get_notification_metrics,
    "get_hourly_heatmap": handle_get_hourly_heatmap,
    "get_app_analytics": handle_get_app_analytics,
    "get_productivity_report": handle_get_productivity_report,
}
