"""
Pytest configuration and fixtures for Mac Notifications tests
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json
import random

from mac_notifications.src.database.connection import DatabaseConnection
from mac_notifications.src.database.models import Notification


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create notifications table with all columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rec_id INTEGER UNIQUE NOT NULL,
            app_identifier TEXT NOT NULL,
            delivered_time TEXT NOT NULL,
            title TEXT,
            subtitle TEXT,
            body TEXT,
            category TEXT,
            thread TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            priority_score REAL DEFAULT 0,
            priority_level TEXT DEFAULT 'MEDIUM',
            priority_factors TEXT DEFAULT '[]',
            is_read INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0,
            archived_at REAL,
            batch_id TEXT
        )
    ''')
    
    # Create daemon metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daemon_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_delivered_time ON notifications(delivered_time DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_identifier ON notifications(app_identifier)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority_score ON notifications(priority_score DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_read ON notifications(is_read)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archived ON notifications(is_archived)')
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def db_connection(temp_db):
    """Create a database connection for testing"""
    return DatabaseConnection(temp_db)


@pytest.fixture
def sample_notifications():
    """Provide sample notification data"""
    now = datetime.now()
    notifications = []
    
    # Critical notifications
    notifications.extend([
        {
            "rec_id": 1,
            "app_identifier": "com.apple.mail",
            "title": "Urgent: Server Down",
            "subtitle": "Production server is not responding",
            "body": "The main production server has been down for 10 minutes",
            "delivered_time": (now - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": 95,
            "priority_level": "CRITICAL",
            "priority_factors": json.dumps(["urgent_keyword", "downtime_alert"]),
            "is_read": 0
        },
        {
            "rec_id": 2,
            "app_identifier": "com.apple.mobilesms",
            "title": "John Doe",
            "subtitle": None,
            "body": "Emergency! Call me ASAP",
            "delivered_time": (now - timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": 90,
            "priority_level": "CRITICAL",
            "priority_factors": json.dumps(["urgent_keyword", "personal_message"]),
            "is_read": 0
        }
    ])
    
    # High priority notifications
    notifications.extend([
        {
            "rec_id": 3,
            "app_identifier": "com.microsoft.teams",
            "title": "Meeting Starting",
            "subtitle": "Team Standup",
            "body": "Your team standup meeting is starting now",
            "delivered_time": (now - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": 75,
            "priority_level": "HIGH",
            "priority_factors": json.dumps(["meeting_reminder"]),
            "is_read": 0
        },
        {
            "rec_id": 4,
            "app_identifier": "com.apple.passbook",
            "title": "Payment Due",
            "subtitle": "Credit Card Payment",
            "body": "Your credit card payment of $500 is due tomorrow",
            "delivered_time": (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": 80,
            "priority_level": "HIGH",
            "priority_factors": json.dumps(["financial", "deadline"]),
            "is_read": 1
        }
    ])
    
    # Medium priority notifications
    for i in range(5, 15):
        notifications.append({
            "rec_id": i,
            "app_identifier": random.choice([
                "com.apple.mail", 
                "com.microsoft.outlook",
                "com.slack.slack",
                "com.apple.news"
            ]),
            "title": f"Update {i}",
            "subtitle": f"New content available",
            "body": f"Check out the latest updates in your feed",
            "delivered_time": (now - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": random.randint(40, 60),
            "priority_level": "MEDIUM",
            "priority_factors": json.dumps(["regular_update"]),
            "is_read": random.choice([0, 1])
        })
    
    # Low priority notifications (security cameras)
    for i in range(15, 30):
        notifications.append({
            "rec_id": i,
            "app_identifier": "com.security.batterycam",
            "title": "Motion Detected",
            "subtitle": None,
            "body": f"Backyard: Vehicle detected at {(now - timedelta(minutes=i*5)).strftime('%I:%M %p')}",
            "delivered_time": (now - timedelta(minutes=i*5)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": 20,
            "priority_level": "LOW",
            "priority_factors": json.dumps(["routine_motion"]),
            "is_read": 1
        })
    
    return notifications


@pytest.fixture
def populated_db(temp_db, sample_notifications):
    """Create a populated test database"""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Insert sample notifications
    for notif in sample_notifications:
        cursor.execute('''
            INSERT INTO notifications (
                rec_id, app_identifier, delivered_time, title, subtitle, body,
                priority_score, priority_level, priority_factors, is_read
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notif['rec_id'],
            notif['app_identifier'],
            notif['delivered_time'],
            notif.get('title'),
            notif.get('subtitle'),
            notif.get('body'),
            notif.get('priority_score', 50),
            notif.get('priority_level', 'MEDIUM'),
            notif.get('priority_factors', '[]'),
            notif.get('is_read', 0)
        ))
    
    # Add daemon metadata
    cursor.execute(
        "INSERT INTO daemon_metadata (key, value) VALUES (?, ?)",
        ('last_update', datetime.now().isoformat())
    )
    cursor.execute(
        "INSERT INTO daemon_metadata (key, value) VALUES (?, ?)",
        ('last_rec_id', str(len(sample_notifications)))
    )
    
    conn.commit()
    conn.close()
    
    return temp_db


@pytest.fixture
def mock_mcp_server(populated_db):
    """Create a mock MCP server for testing"""
    from mac_notifications.src.mcp_server.server import NotificationMCPServer
    return NotificationMCPServer(populated_db)


@pytest.fixture
def conversation_notifications():
    """Create notifications that represent conversations"""
    now = datetime.now()
    notifications = []
    
    # Messages from Alice
    for i in range(5):
        notifications.append({
            "rec_id": 100 + i,
            "app_identifier": "com.apple.mobilesms",
            "title": "Alice Smith",
            "subtitle": None,
            "body": [
                "Hey, are you free for lunch?",
                "How about that new Italian place?",
                "12:30 works for me",
                "Great! See you there",
                "Actually, can we make it 1pm instead?"
            ][i],
            "delivered_time": (now - timedelta(minutes=30-i*5)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": 60,
            "priority_level": "MEDIUM",
            "is_read": 0 if i >= 3 else 1
        })
    
    # Email thread
    for i in range(3):
        notifications.append({
            "rec_id": 200 + i,
            "app_identifier": "com.apple.mail",
            "title": "Project Update",
            "subtitle": f"Re: Q4 Planning - Message {i+1}",
            "body": "Please review the attached documents",
            "thread": "q4-planning-2024",
            "delivered_time": (now - timedelta(hours=i+1)).strftime('%Y-%m-%d %H:%M:%S'),
            "priority_score": 70,
            "priority_level": "HIGH",
            "is_read": 0
        })
    
    return notifications
