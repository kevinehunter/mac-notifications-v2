"""
Configuration Settings Module
Centralized configuration for the Mac Notifications system
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
import logging


class Settings:
    """Application settings and configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = DATA_DIR / "logs"
    CONFIG_DIR = BASE_DIR / "config"
    
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Database settings
    DEFAULT_DB_NAME = "notifications.db"
    DEFAULT_DB_PATH = DATA_DIR / DEFAULT_DB_NAME
    DB_TIMEOUT = 30.0
    DB_BACKUP_DIR = DATA_DIR / "backups"
    
    # macOS notification database
    MACOS_DB_PATH = os.path.expanduser("~/Library/Group Containers/group.com.apple.usernoted/db2/db")
    
    # Daemon settings
    DAEMON_UPDATE_INTERVAL = 10  # seconds
    DAEMON_BATCH_SIZE = 100
    DAEMON_PID_FILE = DATA_DIR / "notification_daemon.pid"
    DAEMON_LOG_FILE = LOG_DIR / "notification_daemon.log"
    
    # Cleanup settings
    MAX_NOTIFICATION_AGE_DAYS = 30
    CLEANUP_INTERVAL_UPDATES = 100  # Run cleanup every N updates
    
    # MCP Server settings
    MCP_SERVER_NAME = "mac-notifications"
    MCP_SERVER_VERSION = "2.0.0"
    MCP_DEFAULT_LIMIT = 10
    
    # Feature flags
    FEATURES = {
        "priority_scoring": True,
        "smart_templates": True,
        "enhanced_search": True,
        "notification_grouping": True,
        "batch_actions": True,
        "smart_summaries": True,
        "analytics": True
    }
    
    # Priority scoring settings
    PRIORITY_TIME_DECAY_HOURS = 24
    PRIORITY_RECENT_BOOST_HOURS = 1
    PRIORITY_LEVELS = {
        "CRITICAL": 15,
        "HIGH": 10,
        "MEDIUM": 5,
        "LOW": 0
    }
    
    # Search settings
    SEARCH_DEFAULT_LIMIT = 50
    SEARCH_MAX_LIMIT = 1000
    
    # Grouping settings
    GROUPING_TIME_WINDOW_MINUTES = 30
    GROUPING_MIN_SIZE = 2
    GROUPING_DEFAULT_HOURS = 4
    
    # Summary settings
    SUMMARY_TIME_RANGES = {
        "1h": 1,
        "4h": 4,
        "12h": 12,
        "24h": 24,
        "7d": 168,
        "30d": 720
    }
    
    # Analytics settings
    ANALYTICS_DEFAULT_DAYS = 7
    ANALYTICS_MAX_DAYS = 90
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Performance settings
    CACHE_ENABLED = True
    CACHE_TTL = 300  # seconds
    
    @classmethod
    def load_from_file(cls, config_file: Optional[Path] = None) -> "Settings":
        """Load settings from JSON configuration file"""
        if config_file is None:
            config_file = cls.CONFIG_DIR / "settings.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update class attributes with loaded config
                for key, value in config_data.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)
                
                logging.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logging.warning(f"Failed to load config from {config_file}: {e}")
        
        return cls()
    
    @classmethod
    def load_from_env(cls) -> "Settings":
        """Load settings from environment variables"""
        # Database
        if db_path := os.getenv("MAC_NOTIFICATIONS_DB_PATH"):
            cls.DEFAULT_DB_PATH = Path(db_path)
        
        # Daemon
        if interval := os.getenv("MAC_NOTIFICATIONS_UPDATE_INTERVAL"):
            cls.DAEMON_UPDATE_INTERVAL = int(interval)
        
        if cleanup_days := os.getenv("MAC_NOTIFICATIONS_CLEANUP_DAYS"):
            cls.MAX_NOTIFICATION_AGE_DAYS = int(cleanup_days)
        
        # Logging
        if log_level := os.getenv("MAC_NOTIFICATIONS_LOG_LEVEL"):
            cls.LOG_LEVEL = log_level.upper()
        
        # Features
        for feature in cls.FEATURES:
            env_key = f"MAC_NOTIFICATIONS_FEATURE_{feature.upper()}"
            if env_value := os.getenv(env_key):
                cls.FEATURES[feature] = env_value.lower() in ('true', '1', 'yes', 'on')
        
        return cls()
    
    @classmethod
    def save_to_file(cls, config_file: Optional[Path] = None):
        """Save current settings to JSON file"""
        if config_file is None:
            config_file = cls.CONFIG_DIR / "settings.json"
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect saveable settings
        config_data = {
            "DAEMON_UPDATE_INTERVAL": cls.DAEMON_UPDATE_INTERVAL,
            "MAX_NOTIFICATION_AGE_DAYS": cls.MAX_NOTIFICATION_AGE_DAYS,
            "FEATURES": cls.FEATURES,
            "PRIORITY_LEVELS": cls.PRIORITY_LEVELS,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "SEARCH_DEFAULT_LIMIT": cls.SEARCH_DEFAULT_LIMIT,
            "GROUPING_TIME_WINDOW_MINUTES": cls.GROUPING_TIME_WINDOW_MINUTES,
            "ANALYTICS_DEFAULT_DAYS": cls.ANALYTICS_DEFAULT_DAYS
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logging.info(f"Saved configuration to {config_file}")
    
    @classmethod
    def get_feature(cls, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return cls.FEATURES.get(feature_name, False)
    
    @classmethod
    def get_db_path(cls, name: Optional[str] = None) -> Path:
        """Get database path, optionally with custom name"""
        if name:
            return cls.DATA_DIR / name
        return cls.DEFAULT_DB_PATH
    
    @classmethod
    def get_log_path(cls, name: str) -> Path:
        """Get log file path"""
        return cls.LOG_DIR / name
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export settings as dictionary"""
        return {
            "BASE_DIR": str(cls.BASE_DIR),
            "DATA_DIR": str(cls.DATA_DIR),
            "DEFAULT_DB_PATH": str(cls.DEFAULT_DB_PATH),
            "DAEMON_UPDATE_INTERVAL": cls.DAEMON_UPDATE_INTERVAL,
            "MAX_NOTIFICATION_AGE_DAYS": cls.MAX_NOTIFICATION_AGE_DAYS,
            "FEATURES": cls.FEATURES,
            "LOG_LEVEL": cls.LOG_LEVEL
        }


# Create default settings instance
settings = Settings()

# Try to load from environment first, then from file
settings.load_from_env()
settings.load_from_file()
