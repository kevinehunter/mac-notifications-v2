# Mac Notifications Monitoring System

[![Tests](https://github.com/username/mac-notifications/workflows/Tests/badge.svg)](https://github.com/username/mac-notifications/actions)
[![Coverage](https://codecov.io/gh/username/mac-notifications/branch/main/graph/badge.svg)](https://codecov.io/gh/username/mac-notifications)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful system for monitoring, analyzing, and managing Mac notifications with Claude Desktop integration.

## ✨ Features

### 🔔 Core Functionality
- **Real-time Monitoring** - Captures all macOS notifications as they arrive
- **Smart Priority Scoring** - AI-powered importance ranking (CRITICAL, HIGH, MEDIUM, LOW)
- **Natural Language Search** - Search like "urgent emails from John yesterday"
- **Claude Desktop Integration** - Full MCP server for seamless AI assistance

### 🎯 Advanced Features
- **Smart Summaries** - Hourly, daily, and executive briefs
- **Analytics Dashboard** - Beautiful visualizations of notification patterns
- **Batch Operations** - Mark read, archive, or update multiple notifications
- **Similar Grouping** - Reduces noise by grouping related notifications
- **Focus Time Analysis** - Understand when you're most/least interrupted

### 🔍 Intelligent Search
- Natural language queries ("important Slack messages this morning")
- Boolean operators (AND, OR, NOT)
- Field-specific search (from:Mail, priority:high)
- Time-aware filtering ("last 24 hours", "yesterday", "this week")

## 🚀 Quick Start

### Installation (5 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/mac-notifications.git
cd mac-notifications/mac_notifications

# Run the installer
./scripts/install.sh

# Start monitoring
./scripts/start_daemon.sh
```

### Claude Desktop Setup (2 minutes)

1. Copy the configuration:
```bash
cp config/claude_desktop_config.json ~/Library/Application\ Support/Claude/
```

2. Restart Claude Desktop

3. Test with: "Show my recent notifications"

See the [Quick Start Guide](docs/QUICK_START.md) for detailed instructions.

## 📚 Documentation

- 📖 [Quick Start Guide](docs/QUICK_START.md) - Get up and running fast
- 👤 [User Guide](docs/user_guide.md) - Complete feature documentation  
- 🤖 [Claude Usage Examples](docs/claude_usage.md) - How to use with Claude
- 🏗️ [Architecture Overview](docs/architecture.md) - System design details
- 🔧 [Developer Guide](docs/developer_guide.md) - Contributing and extending
- 📋 [API Reference](docs/api_reference.md) - Complete API documentation

## 💬 Example Claude Interactions

```
You: "Show me critical notifications I haven't read"
Claude: Here are your unread critical notifications:
1. Security Alert - Unusual login attempt detected
2. Bank - Large transaction requires approval
3. Calendar - Meeting with CEO in 10 minutes

You: "Summarize my Slack notifications from today"
Claude: Today's Slack Summary:
- 3 direct messages (2 from Sarah about project deadline)
- 5 mentions in #engineering (deployment discussion)
- 12 messages in #general (mostly about lunch plans)

You: "Archive all read emails older than a week"
Claude: I'll archive 47 read email notifications older than 7 days.
This action will be performed. Continue? (yes/no)
```

## 🏗️ Architecture

```
mac_notifications/
├── src/
│   ├── daemon/          # Background notification monitor
│   ├── mcp_server/      # Claude Desktop integration
│   ├── database/        # SQLite storage layer
│   ├── features/        # Core features
│   │   ├── priority_scoring.py   # AI importance ranking
│   │   ├── enhanced_search.py    # Natural language search
│   │   ├── smart_summaries.py    # Intelligent digests
│   │   ├── analytics.py          # Insights & visualizations
│   │   ├── grouping.py           # Similar notification clustering
│   │   └── batch_actions.py      # Bulk operations
│   └── config/          # Settings management
├── tests/               # Comprehensive test suite
├── docs/                # Documentation
├── scripts/             # Installation & management
└── examples/            # Usage examples
```

## 📊 Performance

- **Search Speed**: < 50ms for 10,000 notifications
- **Memory Usage**: ~100MB average
- **CPU Usage**: < 2% during monitoring
- **Startup Time**: 2 seconds
- **Database Size**: ~1MB per 1,000 notifications

## 🧪 Testing

```bash
# Run all tests
./scripts/run_tests.sh

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_enhanced_search.py -v
```

## 🔒 Privacy & Security

- ✅ **100% Local** - All data stays on your Mac
- ✅ **No Cloud Dependencies** - Works entirely offline
- ✅ **Respects macOS Permissions** - Only sees allowed notifications
- ✅ **Secure Storage** - SQLite database with optional encryption
- ✅ **No Telemetry** - Zero data collection or tracking

## 🛠️ Advanced Configuration

### Environment Variables
```bash
# Optional configuration
export MAC_NOTIFICATIONS_DB_PATH="~/Documents/notifications.db"
export MAC_NOTIFICATIONS_LOG_LEVEL="DEBUG"
export MAC_NOTIFICATIONS_ARCHIVE_DAYS="30"
```

### Custom Priority Rules
Edit `src/config/priority_rules.json` to customize importance scoring.

## 🤝 Contributing

We welcome contributions! See our [Developer Guide](docs/developer_guide.md) for:
- Development setup
- Code style guidelines  
- Testing requirements
- Pull request process

## 📈 Roadmap

- [ ] iOS notification support via Continuity
- [ ] Notification snoozing
- [ ] Custom notification actions
- [ ] Export to various formats (PDF, CSV)
- [ ] Multi-language support
- [ ] Webhook integrations

## 🐛 Troubleshooting

### Common Issues

**Notifications not captured?**
- Ensure Terminal has Full Disk Access in System Preferences
- Check daemon status: `./scripts/status.sh`

**Claude can't connect?**
- Verify config path in Claude Desktop settings
- Restart Claude after config changes

See [Troubleshooting Guide](docs/troubleshooting.md) for more solutions.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for [Claude Desktop](https://claude.ai) by Anthropic
- Uses [MCP](https://modelcontextprotocol.com) for AI integration
- Inspired by the need for better notification management

## 📞 Support

- 🐛 [GitHub Issues](https://github.com/yourusername/mac-notifications/issues)
- 📚 [Documentation](docs/)
- 💡 [Feature Requests](https://github.com/yourusername/mac-notifications/discussions)

---

<p align="center">
Made with ❤️ for the macOS community
<br>
Star ⭐ this repo if you find it helpful!
</p>
