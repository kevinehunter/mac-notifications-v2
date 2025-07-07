#!/usr/bin/env python3
"""
Notification Analytics Dashboard Module

Provides visual insights into notification patterns through charts,
metrics, and actionable recommendations.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics
from pathlib import Path


class NotificationAnalytics:
    """Generate analytics and insights from notification data."""
    
    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        
    def get_analytics_dashboard(
        self, 
        days: int = 7,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics dashboard.
        
        Args:
            days: Number of days to analyze
            output_format: "html", "json", or "text"
            
        Returns:
            Dashboard data and formatted output
        """
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Collect all analytics
        metrics = self.get_key_metrics(start_date, end_date)
        hourly_pattern = self.get_hourly_pattern(start_date, end_date)
        daily_trend = self.get_daily_trend(start_date, end_date)
        app_analytics = self.get_app_analytics(start_date, end_date)
        priority_analysis = self.get_priority_analysis(start_date, end_date)
        productivity = self.get_productivity_metrics(start_date, end_date)
        patterns = self.detect_patterns(start_date, end_date, metrics, hourly_pattern, app_analytics, productivity)
        recommendations = self.generate_recommendations(
            metrics, hourly_pattern, app_analytics, productivity, patterns
        )
        
        dashboard_data = {
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "metrics": metrics,
            "hourly_pattern": hourly_pattern,
            "daily_trend": daily_trend,
            "app_analytics": app_analytics,
            "priority_analysis": priority_analysis,
            "productivity": productivity,
            "patterns": patterns,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
        # Format output based on requested format
        if output_format == "html":
            dashboard_data["html"] = self._generate_html_dashboard(dashboard_data)
        elif output_format == "text":
            dashboard_data["text"] = self._generate_text_dashboard(dashboard_data)
            
        return dashboard_data
        
    def get_key_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate key metrics for the period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Convert dates to SQL format
            start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Total notifications
            cursor.execute("""
                SELECT COUNT(*) FROM notifications 
                WHERE delivered_time >= ? AND delivered_time <= ?
            """, (start_str, end_str))
            total = cursor.fetchone()[0]
            
            # Calculate hourly average
            hours = (end_date - start_date).total_seconds() / 3600
            avg_per_hour = total / hours if hours > 0 else 0
            
            # Get peak hour
            cursor.execute("""
                SELECT 
                    strftime('%H', delivered_time) as hour,
                    COUNT(*) as count
                FROM notifications
                WHERE delivered_time >= ? AND delivered_time <= ?
                GROUP BY hour
                ORDER BY count DESC
                LIMIT 1
            """, (start_str, end_str))
            
            peak_data = cursor.fetchone()
            peak_hour = f"{peak_data[0]}:00" if peak_data else "N/A"
            peak_count = peak_data[1] if peak_data else 0
            
            # Check if priority columns exist
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [col[1] for col in cursor.fetchall()]
            has_priority = 'priority_level' in columns
            
            # Critical rate
            if has_priority:
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN priority_level = 'CRITICAL' THEN 1 END),
                        COUNT(CASE WHEN priority_level = 'HIGH' THEN 1 END)
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                """, (start_str, end_str))
                
                critical, high = cursor.fetchone()
                critical_rate = ((critical + high) / total * 100) if total > 0 else 0
            else:
                critical_rate = 0
            
            # Check if is_read column exists
            has_read = 'is_read' in columns
            
            # Unread count
            if has_read:
                cursor.execute("""
                    SELECT COUNT(*) FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    AND is_read = 0
                """, (start_str, end_str))
                unread = cursor.fetchone()[0]
            else:
                unread = 0
            
            # App count
            cursor.execute("""
                SELECT COUNT(DISTINCT app_identifier) FROM notifications
                WHERE delivered_time >= ? AND delivered_time <= ?
            """, (start_str, end_str))
            app_count = cursor.fetchone()[0]
            
            # Calculate days analyzed
            days = (end_date - start_date).days + 1
            
            return {
                "total_notifications": total,
                "avg_per_hour": round(avg_per_hour, 1),
                "peak_hour": peak_hour,
                "peak_hour_count": peak_count,
                "critical_rate": round(critical_rate, 1),
                "unread_count": unread,
                "unread_rate": round(unread / total * 100, 1) if total > 0 else 0,
                "app_count": app_count,
                "days_analyzed": days
            }
            
        finally:
            conn.close()
            
    def get_hourly_pattern(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze hourly notification patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Get hourly counts for each day of week
            cursor.execute("""
                SELECT 
                    CAST(strftime('%w', delivered_time) AS INTEGER) as dow,
                    CAST(strftime('%H', delivered_time) AS INTEGER) as hour,
                    COUNT(*) as count
                FROM notifications
                WHERE delivered_time >= ? AND delivered_time <= ?
                GROUP BY dow, hour
            """, (start_str, end_str))
            
            # Build heatmap data
            heatmap = defaultdict(lambda: defaultdict(int))
            for row in cursor.fetchall():
                dow = row[0]  # 0=Sunday, 1=Monday, etc.
                hour = row[1]
                count = row[2]
                heatmap[hour][dow] = count
                
            # Check if priority columns exist
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [col[1] for col in cursor.fetchall()]
            has_priority = 'priority_level' in columns
            
            # Calculate hourly averages
            if has_priority:
                cursor.execute("""
                    SELECT 
                        CAST(strftime('%H', delivered_time) AS INTEGER) as hour,
                        COUNT(*) as count,
                        AVG(CASE WHEN priority_level = 'CRITICAL' THEN 1 ELSE 0 END) as critical_rate
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    GROUP BY hour
                    ORDER BY hour
                """, (start_str, end_str))
            else:
                cursor.execute("""
                    SELECT 
                        CAST(strftime('%H', delivered_time) AS INTEGER) as hour,
                        COUNT(*) as count,
                        0 as critical_rate
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    GROUP BY hour
                    ORDER BY hour
                """, (start_str, end_str))
            
            hourly_data = []
            for row in cursor.fetchall():
                hourly_data.append({
                    "hour": row[0],
                    "count": row[1],
                    "critical_rate": round(row[2] * 100, 1)
                })
                
            # Find quiet hours (less than 25% of average)
            avg_hourly = sum(h["count"] for h in hourly_data) / 24 if hourly_data else 0
            quiet_hours = [h["hour"] for h in hourly_data if h["count"] < avg_hourly * 0.25]
            busy_hours = [h["hour"] for h in hourly_data if h["count"] > avg_hourly * 1.5]
            
            return {
                "heatmap": dict(heatmap),
                "hourly_breakdown": hourly_data,
                "quiet_hours": quiet_hours,
                "busy_hours": busy_hours,
                "avg_per_hour": round(avg_hourly, 1)
            }
            
        finally:
            conn.close()
            
    def get_daily_trend(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily notification trend."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if priority and is_read columns exist
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [col[1] for col in cursor.fetchall()]
            has_priority = 'priority_level' in columns
            has_read = 'is_read' in columns
            
            if has_priority and has_read:
                cursor.execute("""
                    SELECT 
                        date(delivered_time) as day,
                        COUNT(*) as total,
                        COUNT(CASE WHEN priority_level = 'CRITICAL' THEN 1 END) as critical,
                        COUNT(CASE WHEN priority_level = 'HIGH' THEN 1 END) as high,
                        COUNT(CASE WHEN is_read = 0 THEN 1 END) as unread
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    GROUP BY day
                    ORDER BY day
                """, (start_str, end_str))
            else:
                cursor.execute("""
                    SELECT 
                        date(delivered_time) as day,
                        COUNT(*) as total,
                        0 as critical,
                        0 as high,
                        0 as unread
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    GROUP BY day
                    ORDER BY day
                """, (start_str, end_str))
            
            daily_data = []
            for row in cursor.fetchall():
                daily_data.append({
                    "date": row[0],
                    "total": row[1],
                    "critical": row[2],
                    "high": row[3],
                    "unread": row[4],
                    "important": row[2] + row[3]
                })
                
            return daily_data
            
        finally:
            conn.close()
            
    def get_app_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze notifications by app."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if priority columns exist
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [col[1] for col in cursor.fetchall()]
            has_priority = 'priority_score' in columns and 'priority_level' in columns
            has_read = 'is_read' in columns
            
            # Get app distribution
            if has_priority and has_read:
                cursor.execute("""
                    SELECT 
                        app_identifier,
                        COUNT(*) as count,
                        AVG(priority_score) as avg_priority,
                        COUNT(CASE WHEN priority_level = 'CRITICAL' THEN 1 END) as critical_count,
                        COUNT(CASE WHEN is_read = 0 THEN 1 END) as unread_count
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    GROUP BY app_identifier
                    ORDER BY count DESC
                """, (start_str, end_str))
            else:
                cursor.execute("""
                    SELECT 
                        app_identifier,
                        COUNT(*) as count,
                        0 as avg_priority,
                        0 as critical_count,
                        0 as unread_count
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    GROUP BY app_identifier
                    ORDER BY count DESC
                """, (start_str, end_str))
            
            apps = []
            total = 0
            for row in cursor.fetchall():
                app_data = {
                    "app": row[0],
                    "count": row[1],
                    "avg_priority": round(row[2], 2) if row[2] else 0,
                    "critical_count": row[3],
                    "unread_count": row[4],
                    "readable_name": self._humanize_app_name(row[0])
                }
                apps.append(app_data)
                total += row[1]
                
            # Calculate percentages
            for app in apps:
                app["percentage"] = round(app["count"] / total * 100, 1) if total > 0 else 0
                
            # Get app time patterns
            top_apps = [app["app"] for app in apps[:5]]
            app_patterns = {}
            
            for app_id in top_apps:
                cursor.execute("""
                    SELECT 
                        strftime('%H', delivered_time) as hour,
                        COUNT(*) as count
                    FROM notifications
                    WHERE delivered_time >= ? AND delivered_time <= ?
                    AND app_identifier = ?
                    GROUP BY hour
                    ORDER BY count DESC
                    LIMIT 3
                """, (start_str, end_str, app_id))
                
                peak_hours = [f"{row[0]}:00" for row in cursor.fetchall()]
                app_patterns[app_id] = peak_hours
                
            return {
                "app_distribution": apps,
                "top_interrupters": apps[:5],
                "app_time_patterns": app_patterns,
                "total_apps": len(apps)
            }
            
        finally:
            conn.close()
            
    def get_priority_analysis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze priority patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if priority columns exist
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [col[1] for col in cursor.fetchall()]
            has_priority = 'priority_level' in columns
            
            if not has_priority:
                # Return default values if no priority data
                return {
                    "distribution": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                    "percentages": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                    "critical_response_time": "N/A",
                    "high_response_time": "N/A",
                    "priority_balance": "No priority data available"
                }
            
            # Priority distribution
            cursor.execute("""
                SELECT 
                    priority_level,
                    COUNT(*) as count
                FROM notifications
                WHERE delivered_time >= ? AND delivered_time <= ?
                GROUP BY priority_level
            """, (start_str, end_str))
            
            priority_dist = {}
            total = 0
            for row in cursor.fetchall():
                priority_dist[row[0]] = row[1]
                total += row[1]
                
            # Ensure all levels are present
            for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if level not in priority_dist:
                    priority_dist[level] = 0
                    
            # Calculate percentages
            priority_percentages = {}
            for level, count in priority_dist.items():
                priority_percentages[level] = round(count / total * 100, 1) if total > 0 else 0
                
            return {
                "distribution": priority_dist,
                "percentages": priority_percentages,
                "critical_response_time": "N/A",
                "high_response_time": "N/A",
                "priority_balance": self._assess_priority_balance(priority_percentages)
            }
            
        finally:
            conn.close()
            
    def get_productivity_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate productivity-related metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Get all notification timestamps
            cursor.execute("""
                SELECT delivered_time
                FROM notifications
                WHERE delivered_time >= ? AND delivered_time <= ?
                ORDER BY delivered_time
            """, (start_str, end_str))
            
            timestamps = []
            for row in cursor.fetchall():
                try:
                    dt = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                    timestamps.append(dt)
                except:
                    pass
            
            # Calculate focus time windows
            focus_windows = []
            if len(timestamps) > 1:
                for i in range(1, len(timestamps)):
                    gap = (timestamps[i] - timestamps[i-1]).total_seconds()
                    if gap > 1800:  # 30+ minute gap
                        focus_windows.append(gap / 60)  # Convert to minutes
                        
            # Calculate metrics
            if focus_windows:
                avg_focus = statistics.mean(focus_windows)
                max_focus = max(focus_windows)
                total_focus = sum(focus_windows)
            else:
                avg_focus = max_focus = total_focus = 0
                
            # Calculate interruption rate (notifications per productive hour)
            productive_hours = total_focus / 60
            interruption_rate = len(timestamps) / productive_hours if productive_hours > 0 else 0
            
            # Find best focus times
            cursor.execute("""
                SELECT 
                    strftime('%H', delivered_time) as hour,
                    COUNT(*) as count
                FROM notifications
                WHERE delivered_time >= ? AND delivered_time <= ?
                GROUP BY hour
                ORDER BY count
                LIMIT 3
            """, (start_str, end_str))
            
            best_focus_hours = [f"{row[0]}:00" for row in cursor.fetchall()]
            
            # Calculate focus score (0-10)
            focus_score = self._calculate_focus_score(
                avg_focus, max_focus, interruption_rate, len(focus_windows)
            )
            
            return {
                "avg_focus_time": round(avg_focus, 1),
                "max_focus_time": round(max_focus, 1),
                "total_focus_hours": round(total_focus / 60, 1),
                "interruption_rate": round(interruption_rate, 1),
                "focus_windows_count": len(focus_windows),
                "best_focus_hours": best_focus_hours,
                "focus_score": focus_score,
                "focus_assessment": self._assess_focus_score(focus_score)
            }
            
        finally:
            conn.close()
            
    def detect_patterns(
        self, 
        start_date: datetime, 
        end_date: datetime,
        metrics: Dict[str, Any],
        hourly: Dict[str, Any],
        apps: Dict[str, Any],
        productivity: Dict[str, Any]
    ) -> List[str]:
        """Detect interesting patterns in notification data."""
        patterns = []
        
        # High volume pattern
        if metrics["avg_per_hour"] > 40:
            patterns.append(f"High notification volume: {metrics['avg_per_hour']}/hour average")
            
        # Peak hour pattern
        if hourly["busy_hours"]:
            hours_str = ", ".join([f"{h}:00" for h in hourly["busy_hours"]])
            patterns.append(f"Peak notification hours: {hours_str}")
            
        # Quiet hours pattern
        if len(hourly["quiet_hours"]) >= 6:
            patterns.append(f"You have {len(hourly['quiet_hours'])} quiet hours daily")
            
        # Dominant app pattern
        if apps["app_distribution"] and apps["app_distribution"][0]["percentage"] > 50:
            top_app = apps["app_distribution"][0]
            patterns.append(
                f"{top_app['readable_name']} dominates with {top_app['percentage']}% of notifications"
            )
            
        # Low priority balance
        priority_analysis = self.get_priority_analysis(start_date, end_date)
        if priority_analysis["percentages"].get("LOW", 0) > 80:
            patterns.append(
                f"{priority_analysis['percentages']['LOW']}% are low priority - good for batch cleanup"
            )
            
        # Poor focus time
        if productivity["avg_focus_time"] < 45:
            patterns.append(
                f"Short focus windows: {productivity['avg_focus_time']} minutes average"
            )
            
        # Weekend pattern
        daily = self.get_daily_trend(start_date, end_date)
        weekend_avg = self._calculate_weekend_average(daily)
        weekday_avg = self._calculate_weekday_average(daily)
        if weekend_avg < weekday_avg * 0.5:
            patterns.append("Significantly fewer notifications on weekends")
            
        return patterns
        
    def generate_recommendations(
        self,
        metrics: Dict[str, Any],
        hourly: Dict[str, Any],
        apps: Dict[str, Any],
        productivity: Dict[str, Any],
        patterns: List[str]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analytics."""
        recommendations = []
        
        # High volume recommendation
        if metrics["avg_per_hour"] > 30:
            recommendations.append({
                "priority": "high",
                "category": "volume",
                "recommendation": "Reduce notification volume",
                "action": f"Your {metrics['avg_per_hour']}/hour rate is high. Consider batch checking instead.",
                "impact": "Could save 1-2 hours daily"
            })
            
        # App-specific recommendations
        if apps["app_distribution"]:
            top_app = apps["app_distribution"][0]
            if top_app["percentage"] > 40:
                recommendations.append({
                    "priority": "high",
                    "category": "app",
                    "recommendation": f"Manage {top_app['readable_name']} notifications",
                    "action": f"This app generates {top_app['percentage']}% of all notifications. Consider adjusting settings.",
                    "impact": f"Could reduce notifications by {top_app['count']} ({top_app['percentage']}%)"
                })
                
        # Focus time recommendation
        if productivity["avg_focus_time"] < 60:
            recommendations.append({
                "priority": "medium",
                "category": "productivity",
                "recommendation": "Protect your focus time",
                "action": f"Enable Do Not Disturb during {', '.join(productivity['best_focus_hours'])}",
                "impact": "Could increase focus time by 2-3x"
            })
            
        # Quiet hours recommendation
        if hourly["quiet_hours"]:
            quiet_start = min(hourly["quiet_hours"])
            quiet_end = max(hourly["quiet_hours"])
            recommendations.append({
                "priority": "low",
                "category": "schedule",
                "recommendation": "Leverage natural quiet hours",
                "action": f"Schedule deep work during {quiet_start}:00-{quiet_end}:00",
                "impact": "Align work with natural notification lulls"
            })
            
        # Cleanup recommendation
        if metrics["unread_rate"] > 50:
            recommendations.append({
                "priority": "medium",
                "category": "maintenance",
                "recommendation": "Clean up unread notifications",
                "action": f"You have {metrics['unread_count']} unread ({metrics['unread_rate']}%). Use batch actions.",
                "impact": "Reduce mental clutter"
            })
            
        return recommendations[:5]  # Top 5 recommendations
        
    def _generate_html_dashboard(self, data: Dict[str, Any]) -> str:
        """Generate HTML dashboard with charts and visualizations."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notification Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            color: #007AFF;
            margin: 10px 0;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
        }}
        .recommendations {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .recommendation {{
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #007AFF;
            background: #f8f9fa;
        }}
        .recommendation.high {{
            border-left-color: #ff3b30;
        }}
        .recommendation.medium {{
            border-left-color: #ff9500;
        }}
        .chart-wrapper {{
            position: relative;
            height: 300px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>Notification Analytics Dashboard</h1>
            <p>Analysis period: {data['date_range']['days']} days</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Notifications</div>
                <div class="metric-value">{data['metrics']['total_notifications']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Per Hour Average</div>
                <div class="metric-value">{data['metrics']['avg_per_hour']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Peak Hour</div>
                <div class="metric-value">{data['metrics']['peak_hour']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Focus Score</div>
                <div class="metric-value">{data['productivity']['focus_score']}/10</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Daily Notification Trend</div>
            <div class="chart-wrapper">
                <canvas id="dailyChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">App Distribution</div>
            <div class="chart-wrapper">
                <canvas id="appChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Hourly Pattern</div>
            <div class="chart-wrapper">
                <canvas id="hourlyChart"></canvas>
            </div>
        </div>
        
        <div class="recommendations">
            <h2>Recommendations</h2>
            {self._format_recommendations_html(data['recommendations'])}
        </div>
    </div>
    
    <script>
        // Daily Trend Chart
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        new Chart(dailyCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps([d['date'] for d in data['daily_trend']])},
                datasets: [{{
                    label: 'Total',
                    data: {json.dumps([d['total'] for d in data['daily_trend']])},
                    borderColor: '#007AFF',
                    tension: 0.4
                }}, {{
                    label: 'Critical',
                    data: {json.dumps([d['critical'] for d in data['daily_trend']])},
                    borderColor: '#ff3b30',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
        
        // App Distribution Chart
        const appCtx = document.getElementById('appChart').getContext('2d');
        new Chart(appCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps([app['readable_name'] for app in data['app_analytics']['app_distribution'][:5]])},
                datasets: [{{
                    data: {json.dumps([app['count'] for app in data['app_analytics']['app_distribution'][:5]])},
                    backgroundColor: ['#007AFF', '#34c759', '#ff9500', '#ff3b30', '#af52de']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
        
        // Hourly Pattern Chart
        const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
        new Chart(hourlyCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([f"{h['hour']:02d}:00" for h in data['hourly_pattern']['hourly_breakdown']])},
                datasets: [{{
                    label: 'Notifications',
                    data: {json.dumps([h['count'] for h in data['hourly_pattern']['hourly_breakdown']])},
                    backgroundColor: '#007AFF'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
    </script>
</body>
</html>
"""
        return html
        
    def _generate_text_dashboard(self, data: Dict[str, Any]) -> str:
        """Generate text-based dashboard."""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("NOTIFICATION ANALYTICS DASHBOARD")
        lines.append(f"Period: Last {data['date_range']['days']} days")
        lines.append("=" * 60)
        
        # Key Metrics
        lines.append("\nKEY METRICS:")
        lines.append(f"  Total Notifications: {data['metrics']['total_notifications']}")
        lines.append(f"  Average per Hour: {data['metrics']['avg_per_hour']}")
        lines.append(f"  Peak Hour: {data['metrics']['peak_hour']} ({data['metrics']['peak_hour_count']} notifications)")
        lines.append(f"  Critical Rate: {data['metrics']['critical_rate']}%")
        lines.append(f"  Focus Score: {data['productivity']['focus_score']}/10")
        
        # Top Apps
        lines.append("\nTOP APPS:")
        for i, app in enumerate(data['app_analytics']['app_distribution'][:5], 1):
            lines.append(f"  {i}. {app['readable_name']}: {app['count']} ({app['percentage']}%)")
            
        # Patterns
        if data['patterns']:
            lines.append("\nDETECTED PATTERNS:")
            for pattern in data['patterns']:
                lines.append(f"  • {pattern}")
                
        # Recommendations
        lines.append("\nRECOMMENDATIONS:")
        for i, rec in enumerate(data['recommendations'], 1):
            lines.append(f"  {i}. {rec['recommendation']}")
            lines.append(f"     Action: {rec['action']}")
            lines.append(f"     Impact: {rec['impact']}")
            
        return "\n".join(lines)
        
    def _format_recommendations_html(self, recommendations: List[Dict[str, str]]) -> str:
        """Format recommendations as HTML."""
        html_parts = []
        for rec in recommendations:
            priority_class = rec['priority']
            html_parts.append(f"""
                <div class="recommendation {priority_class}">
                    <strong>{rec['recommendation']}</strong><br>
                    {rec['action']}<br>
                    <small>Impact: {rec['impact']}</small>
                </div>
            """)
        return "".join(html_parts)
        
    def _humanize_app_name(self, app_id: str) -> str:
        """Convert app identifier to human-readable name."""
        app_names = {
            'com.apple.mobilesms': 'Messages',
            'com.apple.MobileSMS': 'Messages',
            'com.apple.mail': 'Mail',
            'com.microsoft.outlook': 'Outlook',
            'com.microsoft.teams': 'Teams',
            'com.microsoft.teams2': 'Teams',
            'com.apple.facetime': 'FaceTime',
            'com.security.batterycam': 'Security Camera',
            'com.apple.news': 'News',
            'com.apple.passbook': 'Wallet',
            'com.apple.scripteditor2': 'Script Editor',
            'com.weather.twc': 'Weather',
            'com.apple.home': 'Home',
            'com.firewalla.firewalla': 'Firewalla',
            'com.flightyapp.flighty': 'Flighty',
            'com.eero.eero-ios': 'Eero'
        }
        return app_names.get(app_id, app_id.split('.')[-1].title())
        
    def _assess_priority_balance(self, percentages: Dict[str, float]) -> str:
        """Assess if priority distribution is healthy."""
        critical = percentages.get('CRITICAL', 0)
        low = percentages.get('LOW', 0)
        
        if critical > 10:
            return "Too many critical notifications"
        elif low > 85:
            return "Good - mostly low priority"
        else:
            return "Balanced distribution"
            
    def _calculate_focus_score(
        self, 
        avg_focus: float, 
        max_focus: float, 
        interruption_rate: float,
        window_count: int
    ) -> float:
        """Calculate focus score from 0-10."""
        score = 5.0  # Base score
        
        # Bonus for good average focus time
        if avg_focus >= 90:
            score += 2
        elif avg_focus >= 60:
            score += 1
        elif avg_focus < 30:
            score -= 2
            
        # Bonus for long max focus
        if max_focus >= 120:
            score += 1
        elif max_focus < 45:
            score -= 1
            
        # Penalty for high interruption rate
        if interruption_rate > 10:
            score -= 2
        elif interruption_rate > 5:
            score -= 1
        elif interruption_rate < 2:
            score += 1
            
        # Bonus for many focus windows
        if window_count >= 10:
            score += 1
            
        return max(0, min(10, round(score, 1)))
        
    def _assess_focus_score(self, score: float) -> str:
        """Provide assessment of focus score."""
        if score >= 8:
            return "Excellent focus time"
        elif score >= 6:
            return "Good focus time"
        elif score >= 4:
            return "Average focus time"
        else:
            return "Poor focus time - needs improvement"
            
    def _calculate_weekend_average(self, daily_data: List[Dict[str, Any]]) -> float:
        """Calculate average notifications on weekends."""
        weekend_counts = []
        for day in daily_data:
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            if date_obj.weekday() >= 5:  # Saturday or Sunday
                weekend_counts.append(day['total'])
        return statistics.mean(weekend_counts) if weekend_counts else 0
        
    def _calculate_weekday_average(self, daily_data: List[Dict[str, Any]]) -> float:
        """Calculate average notifications on weekdays."""
        weekday_counts = []
        for day in daily_data:
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            if date_obj.weekday() < 5:  # Monday to Friday
                weekday_counts.append(day['total'])
        return statistics.mean(weekday_counts) if weekday_counts else 0


# Convenience functions
def generate_analytics_dashboard(
    days: int = 7, 
    output_format: str = "html",
    db_path: str = "notifications.db"
) -> Dict[str, Any]:
    """Generate analytics dashboard."""
    analytics = NotificationAnalytics(db_path)
    return analytics.get_analytics_dashboard(days, output_format)


def get_notification_metrics(db_path: str = "notifications.db") -> Dict[str, Any]:
    """Get key notification metrics."""
    analytics = NotificationAnalytics(db_path)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return analytics.get_key_metrics(start_date, end_date)


def get_productivity_report(db_path: str = "notifications.db") -> Dict[str, Any]:
    """Get productivity metrics and recommendations."""
    analytics = NotificationAnalytics(db_path)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return analytics.get_productivity_metrics(start_date, end_date)
