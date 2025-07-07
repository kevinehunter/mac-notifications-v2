"""
Smart summary handlers for MCP server
"""

import json
from typing import List
import mcp.types as types


async def handle_get_smart_summary(server, arguments: dict) -> List[types.TextContent]:
    """Generate a smart summary of notifications"""
    time_range = arguments.get("time_range", "1h")
    detail_level = arguments.get("detail_level", "standard")
    focus_apps = arguments.get("focus_apps", None)
    
    result = server.get_smart_summary(time_range, detail_level, focus_apps)
    
    # Return just the summary text for better readability
    if "summary" in result and not result.get("error"):
        output = result["summary"]
        if result.get("recommendations"):
            output += "\n\n**Recommendations:**"
            for rec in result["recommendations"]:
                output += f"\n• {rec}"
        return [types.TextContent(type="text", text=output)]
    else:
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_hourly_digest(server, arguments: dict) -> List[types.TextContent]:
    """Get a quick hourly digest"""
    result = server.get_hourly_digest()
    
    if "summary" in result and not result.get("error"):
        return [types.TextContent(type="text", text=result["summary"])]
    else:
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_daily_digest(server, arguments: dict) -> List[types.TextContent]:
    """Get comprehensive daily digest"""
    result = server.get_daily_digest()
    
    if "summary" in result and not result.get("error"):
        output = result["summary"]
        if result.get("patterns"):
            output += "\n\n**Patterns & Insights:**"
            for pattern in result["patterns"]:
                output += f"\n• {pattern}"
        return [types.TextContent(type="text", text=output)]
    else:
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_executive_brief(server, arguments: dict) -> List[types.TextContent]:
    """Get ultra-brief executive summary"""
    result = server.get_executive_brief()
    
    if "summary" in result and not result.get("error"):
        return [types.TextContent(type="text", text=result["summary"])]
    else:
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


# Export handlers
SUMMARY_HANDLERS = {
    "get_smart_summary": handle_get_smart_summary,
    "get_hourly_digest": handle_get_hourly_digest,
    "get_daily_digest": handle_get_daily_digest,
    "get_executive_brief": handle_get_executive_brief,
}
