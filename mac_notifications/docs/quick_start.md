# Quick Start Guide

## Installation (5 minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/mac-notifications.git
cd mac-notifications
```

### 2. Run the Installer
```bash
cd mac_notifications
./scripts/install.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Set up the database
- Create necessary directories
- Make scripts executable

### 3. Start the Notification Daemon
```bash
./scripts/start_daemon.sh
```

You should see:
```
Starting notification daemon...
Notification daemon started successfully! (PID: 12345)
```

## Claude Desktop Setup (2 minutes)

### 1. Locate Claude's Configuration
Open Finder and navigate to:
```
~/Library/Application Support/Claude/
```

### 2. Update the Configuration
Copy the provided configuration:
```bash
cp config/claude_desktop_config.json ~/Library/Application\ Support/Claude/
```

Or manually add to your existing `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mac-notifications": {
      "command": "python",
      "args": ["-m", "mac_notifications.mcp_server"],
      "cwd": "/path/to/mac_notifications",
      "env": {
        "PYTHONPATH": "/path/to/mac_notifications/src",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Restart Claude Desktop
Quit and relaunch Claude Desktop for the changes to take effect.

### 4. Test the Integration
In Claude, try:
- "Show my recent notifications"
- "Start monitoring notifications"

## First Steps

### 1. View Recent Notifications
Ask Claude: "Show me my recent notifications"

You'll see something like:
```
Recent Notifications:
1. Mail - New message from John
2. Slack - Team standup in 5 minutes  
3. Calendar - Meeting with Sarah at 2pm
```

### 2. Try Searching
Ask Claude: "Search for notifications from Slack"

### 3. Check Your Statistics
Ask Claude: "Show me notification analytics"

## Common Commands

| What you want | What to ask Claude |
|--------------|-------------------|
| See recent notifications | "Show my recent notifications" |
| Search by app | "Show notifications from [App Name]" |
| Filter by priority | "Show me critical notifications" |
| Get a summary | "Summarize the last hour" |
| Mark as read | "Mark all Slack notifications as read" |
| View analytics | "Show notification analytics dashboard" |

## Automatic Startup (Optional)

To have notifications monitored automatically when you log in:

```bash
./scripts/create_launchd_plist.sh
```

This creates a LaunchDaemon that starts the monitoring on system startup.

## Troubleshooting

### Notifications Not Appearing?

1. **Check Terminal Permissions**
   - System Preferences → Security & Privacy → Privacy → Full Disk Access
   - Add Terminal.app (or your terminal of choice)

2. **Verify Daemon is Running**
   ```bash
   ./scripts/stop_daemon.sh
   ./scripts/start_daemon.sh
   ```

3. **Check the Logs**
   ```bash
   tail -f data/logs/daemon.log
   ```

### Claude Can't Connect?

1. **Verify Configuration Path**
   - Make sure the `cwd` in Claude's config points to your installation

2. **Check Python Path**
   - The virtual environment should be activated
   - Try: `which python` to verify

3. **Restart Claude Desktop**
   - Configuration changes require a restart

## Next Steps

- Read the [User Guide](user_guide.md) for detailed features
- Check out [Claude Usage Examples](claude_usage.md)
- Explore [Advanced Features](../examples/advanced_features.py)

## Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md)
- View daemon logs: `tail -f data/logs/daemon.log`
- Report issues on GitHub

## Quick Tips

1. **Reduce Noise**: Archive low-priority notifications regularly
2. **Stay Focused**: Use "Do Not Disturb" mode during deep work
3. **Review Daily**: Ask for a daily summary each morning
4. **Clean Up**: Archive old notifications weekly

Ready to take control of your notifications! 🎉
