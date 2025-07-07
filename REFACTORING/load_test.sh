#!/bin/bash
# Load test for notification daemon

echo "================================"
echo "Notification Daemon Load Test"
echo "================================"
echo "Starting at: $(date)"
echo ""

# Check if daemon is running
if ! pgrep -f "notification_daemon" > /dev/null; then
    echo "Error: Notification daemon is not running!"
    echo "Please start the daemon first with: ./scripts/start_daemon.sh"
    exit 1
fi

# Get initial system stats
echo "Initial System Stats:"
ps aux | grep -E "notification_daemon|Python" | grep -v grep
echo ""

# Function to monitor resources
monitor_resources() {
    echo "Monitoring system resources during test..."
    while [ -f /tmp/load_test_running ]; do
        echo -n "$(date +%H:%M:%S) - "
        ps aux | grep notification_daemon | grep -v grep | awk '{print "CPU: " $3 "%, MEM: " $4 "%"}'
        sleep 5
    done
}

# Create flag file
touch /tmp/load_test_running

# Start resource monitoring in background
monitor_resources &
MONITOR_PID=$!

echo "Starting load test - generating 100 notifications..."
echo "Progress:"

# Generate notifications rapidly
for i in {1..100}; do
    # Create notification with varying content
    osascript -e "display notification \"Load test notification $i at $(date +%H:%M:%S)\" with title \"Test App $((i % 5))\" subtitle \"Category $((i % 3))\""
    
    # Progress indicator
    if [ $((i % 10)) -eq 0 ]; then
        echo "  $i notifications sent..."
    fi
    
    # Small delay to avoid overwhelming the system
    sleep 0.1
done

echo ""
echo "All notifications sent. Waiting for processing..."
sleep 10

# Clean up
rm -f /tmp/load_test_running
kill $MONITOR_PID 2>/dev/null
wait $MONITOR_PID 2>/dev/null

echo ""
echo "Final System Stats:"
ps aux | grep -E "notification_daemon|Python" | grep -v grep

# Check database for captured notifications
echo ""
echo "Checking database for captured notifications..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 - <<EOF
import sqlite3
import os

# Find the database
db_path = os.path.expanduser('~/claude/mac_notifications_clean/refactored/mac_notifications/data/notifications.db')
if not os.path.exists(db_path):
    db_path = 'notifications.db'
    
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count recent notifications
    cursor.execute("""
        SELECT COUNT(*) FROM notifications 
        WHERE created_at > datetime('now', '-5 minutes')
        AND title LIKE 'Test App%'
    """)
    count = cursor.fetchone()[0]
    
    print(f"Notifications captured in last 5 minutes: {count}")
    
    if count > 0:
        # Show distribution by app
        cursor.execute("""
            SELECT title, COUNT(*) as cnt
            FROM notifications 
            WHERE created_at > datetime('now', '-5 minutes')
            AND title LIKE 'Test App%'
            GROUP BY title
            ORDER BY cnt DESC
        """)
        
        print("\nDistribution by app:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} notifications")
    
    # Check processing speed
    cursor.execute("""
        SELECT 
            MIN(created_at) as first,
            MAX(created_at) as last,
            COUNT(*) as total
        FROM notifications 
        WHERE created_at > datetime('now', '-5 minutes')
        AND title LIKE 'Test App%'
    """)
    
    row = cursor.fetchone()
    if row and row[2] > 0:
        print(f"\nProcessing window: {row[0]} to {row[1]}")
        print(f"Total processed: {row[2]}")
    
    conn.close()
else:
    print("Database not found!")
EOF

echo ""
echo "================================"
echo "Load test completed at: $(date)"
echo "================================"

# Summary
echo ""
echo "Test Summary:"
echo "- Notifications sent: 100"
echo "- Send rate: ~10 notifications/second"
echo "- Test duration: ~10 seconds"
echo ""
echo "Check daemon.log for any errors or warnings."
