# Mac Notifications User Guide

This guide will help you get the most out of the Mac Notifications system.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Priority Notifications](#priority-notifications)
4. [Natural Language Search](#natural-language-search)
5. [Notification Grouping](#notification-grouping)
6. [Batch Operations](#batch-operations)
7. [Smart Summaries](#smart-summaries)
8. [Analytics Dashboard](#analytics-dashboard)
9. [Tips and Tricks](#tips-and-tricks)
10. [Troubleshooting](#troubleshooting)

## Getting Started

After installation, the notification daemon runs in the background and the MCP server is available in Claude Desktop.

### Starting the System

1. Start the notification daemon:
   ```bash
   python -m mac_notifications.src.daemon.notification_daemon
   ```

2. Open Claude Desktop - the notification tools will be available automatically

### First Time Setup

The system will automatically:
- Create a notification database
- Start monitoring all system notifications
- Apply intelligent priority scoring
- Make notifications searchable

## Basic Usage

### Viewing Recent Notifications

In Claude Desktop, you can ask:
- "Show me my recent notifications"
- "What notifications did I get today?"
- "Show me the last 20 notifications"

### Understanding Priority Levels

Notifications are automatically categorized:
- **CRITICAL** (Red) - Urgent items requiring immediate attention
- **HIGH** (Orange) - Important but not urgent
- **MEDIUM** (Yellow) - Normal priority
- **LOW** (Green) - Informational or routine

## Priority Notifications

### What Makes a Notification Critical?

The system automatically identifies critical notifications:
- Security alerts (stranger detection)
- Fraud warnings
- Medical appointments
- Urgent work messages
- System emergencies

### Viewing High Priority Items

Ask Claude:
- "Show me critical notifications"
- "What urgent items do I have?"
- "Show important notifications from today"

## Natural Language Search

### Basic Searches

You can search using everyday language:
- "messages from John"
- "emails about the project"
- "notifications from yesterday"
- "security alerts"

### Advanced Search Queries

Combine multiple criteria:
- "urgent emails from last week"
- "teams messages but not from bot"
- "financial notifications from October"
- "critical items excluding security cameras"

### Time-Based Searches

- "notifications from today"
- "messages from last hour"
- "alerts from this week"
- "notifications between Monday and Wednesday"

### App-Based Searches

- "from mail"
- "in teams"
- "from security camera"
- "messages from slack"

## Notification Grouping

### Automatic Grouping

The system automatically groups:
- Multiple messages from the same person
- Security camera events from the same location
- Email threads
- Repeated notifications

### Viewing Groups

Ask Claude:
- "Group my notifications from today"
- "Show notification groups"
- "Group security alerts by location"

### Benefits of Grouping

- Reduces clutter
- Shows patterns
- Makes bulk actions easier
- Identifies notification storms

## Batch Operations

### Marking Notifications as Read

- "Mark all low priority as read"
- "Mark teams notifications as read"
- "Mark everything older than 3 days as read"

### Archiving Notifications

- "Archive security camera notifications"
- "Archive notifications older than a week"
- "Archive all read notifications"

### Deleting Notifications

- "Delete low priority notifications older than 30 days"
- "Delete all archived notifications"
- "Delete security camera alerts from last month"

### Updating Priority

- "Change all news notifications to low priority"
- "Mark financial notifications as high priority"

## Smart Summaries

### Hourly Digest

Get a quick overview:
- "Give me an hourly summary"
- "What happened in the last hour?"

Shows:
- Critical items
- Key conversations
- Overall statistics

### Daily Digest

Comprehensive daily review:
- "Show me today's summary"
- "Daily notification digest"

Includes:
- Urgent items
- Communication summary
- Patterns detected
- Recommendations

### Executive Brief

Ultra-concise summary:
- "Executive summary"
- "Quick brief"

Perfect for:
- Morning review
- Quick status check
- Identifying urgent items

## Analytics Dashboard

### Accessing Analytics

- "Show notification analytics"
- "Generate analytics dashboard"
- "Show my notification patterns"

### Key Metrics

The dashboard shows:
- Total notifications
- Average per hour
- Peak notification times
- App distribution
- Priority breakdown

### Productivity Insights

- Focus time analysis
- Interruption patterns
- Best times for deep work
- Notification-free periods

### Trends and Patterns

- Daily/weekly trends
- App usage patterns
- Communication patterns
- Unusual activity detection

## Tips and Tricks

### Reducing Notification Overload

1. **Use Batch Operations**: Regularly archive or delete old notifications
2. **Adjust App Settings**: Disable notifications from chatty apps
3. **Schedule Focus Time**: Use insights to find quiet periods
4. **Group Similar Items**: Use grouping to handle bulk notifications

### Staying on Top of Important Items

1. **Check Critical Daily**: Review critical notifications each morning
2. **Use Smart Summaries**: Get quick overviews instead of scrolling
3. **Set Up Keywords**: Pay attention to specific terms
4. **Monitor Patterns**: Watch for unusual activity

### Search Tips

1. **Be Specific**: "urgent" vs "critical" have different meanings
2. **Use Exclusions**: "but not" to filter out unwanted results
3. **Combine Criteria**: Mix time, app, and keyword filters
4. **Try Variations**: Different phrasings may yield better results

## Troubleshooting

### Common Issues

**No notifications appearing:**
- Check if daemon is running
- Verify macOS notification permissions
- Check database path in settings

**Search not finding results:**
- Try simpler search terms
- Check time range
- Verify notifications exist for that period

**Performance issues:**
- Archive old notifications
- Reduce retention period
- Check database size

### Getting Help

1. Check the logs in `data/logs/`
2. Run diagnostic commands
3. Check system permissions
4. Restart the daemon if needed

### Database Maintenance

Periodically:
- Archive old notifications
- Compact the database
- Clear temporary data
- Update retention settings

## Advanced Usage

### Custom Searches with Regex

For power users, regex patterns are supported:
- "Search for /error.*critical/"
- "Find /^URGENT:/"

### Keyboard Shortcuts in Claude

While in Claude Desktop:
- Quick search: Just type your query
- Filter by app: "from [app]"
- Time filter: "last [time period]"

### Integration with Other Tools

The system can be extended to:
- Export notifications to CSV
- Integrate with task managers
- Send alerts to other services
- Create custom workflows

---

Remember: The system is designed to help you manage information overload. Use the features that work best for your workflow, and don't hesitate to experiment with different approaches to find what works for you.
