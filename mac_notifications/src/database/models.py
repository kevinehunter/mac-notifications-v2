"""
Database Models
Defines the data structures for notifications and related entities
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class Notification:
    """Notification model representing a macOS notification"""
    
    # Core fields
    rec_id: int
    app_identifier: str
    delivered_time: datetime
    
    # Content fields
    title: str = ""
    subtitle: str = ""
    body: str = ""
    category: str = ""
    thread: str = ""
    
    # Priority fields
    priority_score: float = 0.0
    priority_level: str = "UNKNOWN"
    priority_factors: List[str] = field(default_factory=list)
    
    # Status fields
    is_read: bool = False
    is_archived: bool = False
    
    # Metadata
    raw_data: Optional[bytes] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # MCP compatibility fields (computed)
    id: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Generate MCP-compatible ID
        if self.id is None:
            self.id = f"notif_{self.rec_id}"
        
        # Ensure datetime objects
        if isinstance(self.delivered_time, str):
            self.delivered_time = datetime.fromisoformat(self.delivered_time)
        
        if self.created_at and isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
            
        if self.updated_at and isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        if isinstance(data['delivered_time'], datetime):
            data['delivered_time'] = data['delivered_time'].isoformat()
        
        if data.get('created_at') and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
            
        if data.get('updated_at') and isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        
        # Ensure priority_factors is JSON string for database
        if isinstance(data['priority_factors'], list):
            data['priority_factors_json'] = json.dumps(data['priority_factors'])
        
        # Remove raw_data for JSON serialization (it's bytes)
        if 'raw_data' in data:
            data.pop('raw_data', None)
        
        return data
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Convert to MCP server compatible format"""
        return {
            "id": self.id,
            "rec_id": self.rec_id,
            "app_identifier": self.app_identifier,
            "delivered_time": self.delivered_time.isoformat() if isinstance(self.delivered_time, datetime) else self.delivered_time,
            "timestamp": self.delivered_time.isoformat() if isinstance(self.delivered_time, datetime) else self.delivered_time,
            "title": self.title,
            "subtitle": self.subtitle,
            "body": self.body,
            "informative_text": self.body,  # MCP compatibility
            "category": self.category,
            "thread": self.thread,
            "activated": False,  # MCP compatibility
            "delivery_date": self.delivered_time.isoformat() if isinstance(self.delivered_time, datetime) else self.delivered_time,
            "sound_name": "default",  # MCP compatibility
            "has_action_button": False,  # MCP compatibility
            "action_button_title": "",  # MCP compatibility
            "priority_score": self.priority_score,
            "priority_level": self.priority_level,
            "priority_factors": self.priority_factors,
            "is_read": self.is_read,
            "is_archived": self.is_archived
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create notification from dictionary"""
        # Handle priority_factors
        if 'priority_factors_json' in data:
            data['priority_factors'] = json.loads(data['priority_factors_json'])
            data.pop('priority_factors_json')
        elif 'priority_factors' in data and isinstance(data['priority_factors'], str):
            try:
                data['priority_factors'] = json.loads(data['priority_factors'])
            except json.JSONDecodeError:
                data['priority_factors'] = []
        
        # Remove any None values
        data = {k: v for k, v in data.items() if v is not None}
        
        return cls(**data)
    
    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> 'Notification':
        """Create notification from database row"""
        # SQLite returns string dates, convert them
        if 'delivered_time' in row and isinstance(row['delivered_time'], str):
            row['delivered_time'] = datetime.fromisoformat(row['delivered_time'])
        
        return cls.from_dict(row)
    
    def matches_search(self, query: str) -> bool:
        """Check if notification matches search query"""
        query_lower = query.lower()
        searchable_text = f"{self.title} {self.subtitle} {self.body} {self.app_identifier}".lower()
        return query_lower in searchable_text
    
    def __str__(self) -> str:
        """String representation"""
        return f"Notification({self.app_identifier}: {self.title or 'No title'})"


@dataclass 
class DaemonMetadata:
    """Metadata stored by the daemon"""
    key: str
    value: str
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DaemonMetadata':
        """Create from dictionary"""
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class NotificationStats:
    """Statistics about notifications"""
    total_count: int = 0
    unread_count: int = 0
    archived_count: int = 0
    
    by_app: Dict[str, int] = field(default_factory=dict)
    by_priority: Dict[str, int] = field(default_factory=dict)
    by_date: Dict[str, int] = field(default_factory=dict)
    
    date_range: Dict[str, Optional[datetime]] = field(default_factory=lambda: {"oldest": None, "newest": None})
    
    top_priority_notifications: List[Notification] = field(default_factory=list)
    recent_notifications: List[Notification] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        
        # Convert date_range datetimes
        if data['date_range']['oldest']:
            data['date_range']['oldest'] = data['date_range']['oldest'].isoformat()
        if data['date_range']['newest']:
            data['date_range']['newest'] = data['date_range']['newest'].isoformat()
        
        # Convert notification lists
        data['top_priority_notifications'] = [n.to_dict() for n in self.top_priority_notifications]
        data['recent_notifications'] = [n.to_dict() for n in self.recent_notifications]
        
        return data


# Type aliases for clarity
NotificationID = int
AppIdentifier = str
PriorityLevel = str  # CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN