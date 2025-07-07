#!/usr/bin/env python3
"""Performance benchmarking for Mac Notifications system"""

import time
import sqlite3
import random
import string
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mac_notifications', 'src'))

from features.enhanced_search import EnhancedSearch
from features.priority_scoring import PriorityScorer
from features.grouping import NotificationGrouper
from features.analytics import NotificationAnalytics
from database.connection import DatabaseConnection

def generate_test_notification():
    """Generate a random test notification"""
    apps = ['Mail', 'Slack', 'Chrome', 'Calendar', 'Messages', 'System', 'Finder', 'Terminal']
    titles = ['Meeting reminder', 'New message', 'Update available', 'Task completed', 
              'Alert', 'Notification', 'Reminder', 'Status update']
    bodies = [''.join(random.choices(string.ascii_letters + string.digits + ' ', k=50)) 
              for _ in range(10)]
    
    return {
        'app': random.choice(apps),
        'title': random.choice(titles),
        'subtitle': f"Test {random.randint(1, 1000)}",
        'body': random.choice(bodies),
        'created_at': datetime.now() - timedelta(minutes=random.randint(0, 10000))
    }

def populate_test_database(db_path, num_notifications):
    """Create a test database with sample notifications"""
    print(f"Creating test database with {num_notifications} notifications...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app TEXT,
            title TEXT,
            subtitle TEXT,
            body TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            priority TEXT DEFAULT 'MEDIUM',
            priority_score REAL DEFAULT 50.0,
            is_read INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0
        )
    ''')
    
    # Generate and insert notifications
    notifications = []
    for i in range(num_notifications):
        notif = generate_test_notification()
        notifications.append((
            notif['app'],
            notif['title'],
            notif['subtitle'],
            notif['body'],
            notif['created_at'],
            random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            random.uniform(0, 100),
            random.choice([0, 1]),
            0
        ))
        
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1} notifications...")
    
    cursor.executemany('''
        INSERT INTO notifications 
        (app, title, subtitle, body, created_at, priority, priority_score, is_read, is_archived)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', notifications)
    
    conn.commit()
    return conn

def benchmark_search_performance(conn, num_queries=20):
    """Benchmark search performance"""
    print("\n" + "=" * 60)
    print("Search Performance Benchmark")
    print("=" * 60)
    
    search = EnhancedSearch()
    
    # Test queries of varying complexity
    queries = [
        "email from john",
        "urgent meeting tomorrow",
        "project deadline",
        "system alert critical",
        "slack message",
        "calendar event",
        "mail attachment",
        "notification today",
        "unread messages",
        "high priority tasks",
        "meeting AND project",
        "email OR slack",
        "NOT archived",
        "from:Mail subject:important",
        "priority:high unread",
        "app:Slack yesterday",
        "title:reminder body:task",
        "last 24 hours",
        "this week important",
        "chrome update"
    ]
    
    results = []
    print(f"\nRunning {len(queries)} search queries...")
    print("-" * 60)
    print(f"{'Query':<30} {'Results':<10} {'Time (ms)':<10} {'ms/result':<10}")
    print("-" * 60)
    
    total_time = 0
    total_results = 0
    
    for query in queries:
        start = time.time()
        result = search.search(query, conn, limit=100)
        duration = (time.time() - start) * 1000  # Convert to ms
        
        num_results = len(result.get('notifications', []))
        ms_per_result = duration / num_results if num_results > 0 else 0
        
        print(f"{query:<30} {num_results:<10} {duration:>8.2f} {ms_per_result:>8.2f}")
        
        total_time += duration
        total_results += num_results
        results.append({
            'query': query,
            'results': num_results,
            'duration_ms': duration,
            'ms_per_result': ms_per_result
        })
    
    print("-" * 60)
    avg_time = total_time / len(queries)
    print(f"{'AVERAGE':<30} {total_results/len(queries):<10.1f} {avg_time:>8.2f}")
    print(f"\nTotal queries: {len(queries)}")
    print(f"Total time: {total_time:.2f}ms")
    print(f"Queries per second: {1000 * len(queries) / total_time:.2f}")
    
    return results

def benchmark_batch_operations(conn):
    """Benchmark batch operation performance"""
    print("\n" + "=" * 60)
    print("Batch Operations Performance Benchmark")
    print("=" * 60)
    
    cursor = conn.cursor()
    
    # Test different batch sizes
    batch_sizes = [10, 50, 100, 500, 1000]
    operations = ['mark_read', 'mark_unread', 'archive', 'update_priority']
    
    print(f"\n{'Operation':<20} {'Batch Size':<12} {'Time (ms)':<12} {'Items/sec':<12}")
    print("-" * 56)
    
    for operation in operations:
        for size in batch_sizes:
            # Get random IDs for batch operation
            cursor.execute(f"SELECT id FROM notifications ORDER BY RANDOM() LIMIT {size}")
            ids = [row[0] for row in cursor.fetchall()]
            
            start = time.time()
            
            if operation == 'mark_read':
                cursor.execute(f"UPDATE notifications SET is_read = 1 WHERE id IN ({','.join('?' * len(ids))})", ids)
            elif operation == 'mark_unread':
                cursor.execute(f"UPDATE notifications SET is_read = 0 WHERE id IN ({','.join('?' * len(ids))})", ids)
            elif operation == 'archive':
                cursor.execute(f"UPDATE notifications SET is_archived = 1 WHERE id IN ({','.join('?' * len(ids))})", ids)
            elif operation == 'update_priority':
                cursor.execute(f"UPDATE notifications SET priority = 'HIGH' WHERE id IN ({','.join('?' * len(ids))})", ids)
            
            conn.commit()
            duration = (time.time() - start) * 1000
            items_per_sec = size / (duration / 1000) if duration > 0 else 0
            
            print(f"{operation:<20} {size:<12} {duration:>10.2f} {items_per_sec:>10.2f}")

def benchmark_priority_scoring():
    """Benchmark priority scoring performance"""
    print("\n" + "=" * 60)
    print("Priority Scoring Performance Benchmark")
    print("=" * 60)
    
    scorer = PriorityScorer()
    
    # Generate test notifications
    test_notifications = []
    for _ in range(1000):
        notif = generate_test_notification()
        test_notifications.append({
            'app': notif['app'],
            'title': notif['title'],
            'body': notif['body'],
            'subtitle': notif['subtitle']
        })
    
    print(f"\nScoring {len(test_notifications)} notifications...")
    
    start = time.time()
    scores = []
    for notif in test_notifications:
        score_info = scorer.calculate_priority(
            notif['app'],
            notif['title'],
            notif.get('body', ''),
            notif.get('subtitle', '')
        )
        scores.append(score_info)
    
    duration = time.time() - start
    
    print(f"Total time: {duration:.3f} seconds")
    print(f"Notifications per second: {len(test_notifications) / duration:.2f}")
    print(f"Average time per notification: {duration / len(test_notifications) * 1000:.3f}ms")
    
    # Analyze score distribution
    priority_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for score in scores:
        priority_counts[score['priority']] += 1
    
    print("\nPriority Distribution:")
    for priority, count in priority_counts.items():
        percentage = (count / len(scores)) * 100
        print(f"  {priority}: {count} ({percentage:.1f}%)")

def benchmark_grouping_performance(conn):
    """Benchmark notification grouping performance"""
    print("\n" + "=" * 60)
    print("Notification Grouping Performance Benchmark")
    print("=" * 60)
    
    grouper = NotificationGrouper()
    
    # Test with different time windows
    time_windows = [5, 15, 30, 60]  # minutes
    
    print(f"\n{'Time Window':<15} {'Groups Found':<15} {'Time (ms)':<12}")
    print("-" * 42)
    
    for window in time_windows:
        start = time.time()
        groups = grouper.group_notifications(conn, time_window_minutes=window)
        duration = (time.time() - start) * 1000
        
        total_groups = sum(len(app_groups) for app_groups in groups.values())
        print(f"{f'{window} min':<15} {total_groups:<15} {duration:>10.2f}")

def run_all_benchmarks():
    """Run all performance benchmarks"""
    print("Mac Notifications Performance Benchmark Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create test database
    test_db = "benchmark_test.db"
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    # Different database sizes to test
    db_sizes = [1000, 5000, 10000]
    
    for size in db_sizes:
        print(f"\n\n{'#' * 60}")
        print(f"Testing with database size: {size} notifications")
        print('#' * 60)
        
        conn = populate_test_database(test_db, size)
        
        try:
            # Run benchmarks
            benchmark_search_performance(conn)
            benchmark_batch_operations(conn)
            benchmark_priority_scoring()
            benchmark_grouping_performance(conn)
            
        finally:
            conn.close()
    
    # Cleanup
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    print(f"\n\nBenchmark completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    run_all_benchmarks()
