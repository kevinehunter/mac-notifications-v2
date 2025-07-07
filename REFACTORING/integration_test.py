#!/usr/bin/env python3
"""Complete system integration test"""

import subprocess
import time
import json
import sqlite3
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_full_system():
    """Run a complete end-to-end system test"""
    print("=" * 60)
    print("Starting Full System Integration Test")
    print("=" * 60)
    
    test_db = "test_notifications.db"
    daemon_proc = None
    success = True
    
    try:
        # Clean up any existing test database
        if Path(test_db).exists():
            Path(test_db).unlink()
            
        # 1. Start daemon
        print("\n1. Starting daemon...")
        daemon_proc = subprocess.Popen([
            sys.executable, "-m", "mac_notifications.daemon.notification_daemon",
            "--db", test_db
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
        
        # Give daemon time to initialize
        time.sleep(5)
        
        # Check if daemon is running
        if daemon_proc.poll() is not None:
            stdout, stderr = daemon_proc.communicate()
            print(f"❌ Daemon failed to start!")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
        print("✅ Daemon started successfully")
        
        # 2. Create test notification
        print("\n2. Creating test notification...")
        result = subprocess.run([
            "osascript", "-e", 
            'display notification "Integration Test Message" with title "Test" subtitle "Integration"'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to create notification: {result.stderr}")
            return False
            
        print("✅ Test notification created")
        time.sleep(3)  # Give daemon time to capture
        
        # 3. Check database
        print("\n3. Checking database...")
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Check if notifications table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        if not cursor.fetchone():
            print("❌ Notifications table not found")
            return False
            
        # Check for our test notification
        cursor.execute("""
            SELECT COUNT(*) FROM notifications 
            WHERE title = 'Test' AND subtitle = 'Integration'
        """)
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("❌ Test notification not found in database")
            # Let's see what's in there
            cursor.execute("SELECT title, subtitle, body FROM notifications ORDER BY created_at DESC LIMIT 5")
            rows = cursor.fetchall()
            print("Recent notifications in DB:")
            for row in rows:
                print(f"  - {row}")
            return False
        else:
            print(f"✅ Test notification found in database (count: {count})")
            
        # 4. Test priority scoring
        print("\n4. Testing priority scoring...")
        cursor.execute("""
            SELECT priority, priority_score FROM notifications 
            WHERE title = 'Test' AND subtitle = 'Integration'
            ORDER BY created_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            priority, score = row
            print(f"✅ Priority scoring working - Priority: {priority}, Score: {score}")
        else:
            print("❌ Could not retrieve priority information")
            
        # 5. Test MCP server (import only, don't start)
        print("\n5. Testing MCP server imports...")
        try:
            from mac_notifications.mcp_server import server
            print("✅ MCP server module imports successfully")
        except Exception as e:
            print(f"❌ MCP server import failed: {e}")
            success = False
            
        # 6. Test feature imports
        print("\n6. Testing feature imports...")
        features = [
            "features.priority_scoring",
            "features.enhanced_search", 
            "features.templates",
            "features.smart_summaries",
            "features.analytics",
            "features.grouping",
            "features.batch_actions"
        ]
        
        for feature in features:
            try:
                module = __import__(f"mac_notifications.{feature}", fromlist=[''])
                print(f"✅ {feature} imports successfully")
            except Exception as e:
                print(f"❌ {feature} import failed: {e}")
                success = False
                
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
        
    finally:
        # Cleanup
        print("\n7. Cleaning up...")
        if daemon_proc and daemon_proc.poll() is None:
            daemon_proc.terminate()
            daemon_proc.wait()
            print("✅ Daemon stopped")
            
        if Path(test_db).exists():
            Path(test_db).unlink()
            print("✅ Test database removed")
            
    print("\n" + "=" * 60)
    if success:
        print("✅ Integration test PASSED!")
    else:
        print("❌ Integration test FAILED!")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = test_full_system()
    sys.exit(0 if success else 1)
