#!/bin/bash
# Production backup script before v2.0 deployment

echo "========================================="
echo "Mac Notifications Production Backup"
echo "========================================="
echo "Backup started at: $(date)"
echo ""

# Configuration
BACKUP_DIR="$HOME/mac_notifications_backups/$(date +%Y%m%d_%H%M%S)"
PROD_DIR="$HOME/claude/mac_notifications_clean/refactored"
DB_PATH="$PROD_DIR/notifications.db"

# Create backup directory
echo "Creating backup directory..."
mkdir -p "$BACKUP_DIR"

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo "  ✓ $1"
    else
        echo "  ✗ $1 FAILED"
        exit 1
    fi
}

# Stop daemon if running
echo ""
echo "Stopping notification daemon..."
if pgrep -f notification_daemon > /dev/null; then
    cd "$PROD_DIR"
    ./stop_daemon.sh > /dev/null 2>&1
    check_status "Daemon stopped"
else
    echo "  ℹ Daemon not running"
fi

# Backup database
echo ""
echo "Backing up database..."
if [ -f "$DB_PATH" ]; then
    # Create database backup with integrity check
    sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/notifications.db'"
    check_status "Database backed up"
    
    # Verify backup
    sqlite3 "$BACKUP_DIR/notifications.db" "PRAGMA integrity_check" > /dev/null
    check_status "Database integrity verified"
    
    # Get database stats
    NOTIF_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM notifications" 2>/dev/null || echo "0")
    DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo "  ℹ Database size: $DB_SIZE"
    echo "  ℹ Notifications: $NOTIF_COUNT"
else
    echo "  ⚠ No database found at $DB_PATH"
fi

# Backup configuration files
echo ""
echo "Backing up configuration..."
CONFIG_FILES=(
    "claude_desktop_config.json"
    "notification_daemon.py"
    "notification_mcp_server.py"
    ".env"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$PROD_DIR/$file" ]; then
        cp "$PROD_DIR/$file" "$BACKUP_DIR/"
        check_status "Backed up $file"
    fi
done

# Backup current features
echo ""
echo "Backing up feature files..."
if [ -d "$PROD_DIR/features" ]; then
    cp -r "$PROD_DIR/features" "$BACKUP_DIR/"
    check_status "Features directory backed up"
fi

# Create system state snapshot
echo ""
echo "Creating system state snapshot..."
cat > "$BACKUP_DIR/system_state.txt" << EOF
Backup Date: $(date)
System: $(uname -a)
Python: $(python3 --version)
Current Directory: $PROD_DIR
Database Location: $DB_PATH
Database Size: $DB_SIZE
Total Notifications: $NOTIF_COUNT

Installed Python Packages:
$(pip list)

Current Git Status:
$(cd "$PROD_DIR" && git status --short)

Current Git Branch:
$(cd "$PROD_DIR" && git branch --show-current)

Last Git Commit:
$(cd "$PROD_DIR" && git log -1 --oneline)
EOF
check_status "System state recorded"

# Create restore script
echo ""
echo "Creating restore script..."
cat > "$BACKUP_DIR/restore.sh" << 'EOF'
#!/bin/bash
# Restore script for Mac Notifications backup

echo "Mac Notifications Restore Script"
echo "================================"
echo ""
echo "This will restore from backup: $(basename $(dirname $0))"
echo ""
read -p "Are you sure you want to restore? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

BACKUP_DIR="$(dirname $0)"
RESTORE_TO="$HOME/claude/mac_notifications_clean/refactored"

# Stop daemon if running
echo "Stopping daemon..."
cd "$RESTORE_TO"
./stop_daemon.sh > /dev/null 2>&1

# Restore database
echo "Restoring database..."
if [ -f "$BACKUP_DIR/notifications.db" ]; then
    cp "$BACKUP_DIR/notifications.db" "$RESTORE_TO/notifications.db"
    echo "  ✓ Database restored"
fi

# Restore configuration files
echo "Restoring configuration..."
for file in claude_desktop_config.json notification_daemon.py notification_mcp_server.py .env; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        cp "$BACKUP_DIR/$file" "$RESTORE_TO/$file"
        echo "  ✓ Restored $file"
    fi
done

# Restore features
if [ -d "$BACKUP_DIR/features" ]; then
    cp -r "$BACKUP_DIR/features" "$RESTORE_TO/"
    echo "  ✓ Features restored"
fi

echo ""
echo "Restore completed!"
echo "You can now start the daemon with: ./start_daemon.sh"
EOF

chmod +x "$BACKUP_DIR/restore.sh"
check_status "Restore script created"

# Create backup manifest
echo ""
echo "Creating backup manifest..."
cd "$BACKUP_DIR"
find . -type f -exec md5sum {} \; > manifest.txt
check_status "Manifest created"

# Compress backup
echo ""
echo "Compressing backup..."
cd "$(dirname "$BACKUP_DIR")"
tar -czf "$(basename "$BACKUP_DIR").tar.gz" "$(basename "$BACKUP_DIR")"
check_status "Backup compressed"

# Final summary
echo ""
echo "========================================="
echo "Backup Summary"
echo "========================================="
echo "Backup location: $BACKUP_DIR"
echo "Compressed file: $(dirname "$BACKUP_DIR")/$(basename "$BACKUP_DIR").tar.gz"
echo "Database size: $DB_SIZE"
echo "Notifications: $NOTIF_COUNT"
echo ""
echo "To restore from this backup, run:"
echo "  $BACKUP_DIR/restore.sh"
echo ""
echo "Backup completed at: $(date)"
echo "========================================="

# Keep last 5 backups
echo ""
echo "Cleaning old backups..."
cd "$HOME/mac_notifications_backups"
ls -t *.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
echo "  ✓ Old backups cleaned (keeping last 5)"

exit 0
