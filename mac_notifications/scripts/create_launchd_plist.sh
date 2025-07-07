#!/bin/bash
cat > ~/Library/LaunchAgents/com.user.mac-notifications.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.mac-notifications</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/scripts/start_daemon.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$(pwd)/data/logs/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>$(pwd)/data/logs/launchd.err.log</string>
</dict>
</plist>
EOF

echo "LaunchD plist created. To install:"
echo "launchctl load ~/Library/LaunchAgents/com.user.mac-notifications.plist"
