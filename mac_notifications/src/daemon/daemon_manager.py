"""
Daemon Manager Module
Handles daemon lifecycle management and process control
"""

import os
import subprocess
import signal
import time
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging


class DaemonManager:
    """Manages daemon process lifecycle"""
    
    def __init__(self, daemon_script: str = "notification_daemon.py", 
                 pid_file: str = "notification_daemon.pid",
                 log_file: str = "notification_daemon.log"):
        self.daemon_script = daemon_script
        self.pid_file = Path(pid_file)
        self.log_file = Path(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def is_running(self) -> bool:
        """Check if daemon is currently running"""
        pid = self._read_pid()
        if pid is None:
            return False
        
        try:
            # Check if process exists
            process = psutil.Process(pid)
            # Verify it's our daemon
            cmdline = ' '.join(process.cmdline())
            return self.daemon_script in cmdline
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process doesn't exist or we can't access it
            self._cleanup_pid_file()
            return False
    
    def start(self, db_path: str = "notifications.db", 
              interval: int = 10,
              background: bool = True) -> bool:
        """Start the daemon process"""
        if self.is_running():
            self.logger.warning("Daemon is already running")
            return False
        
        # Build command
        cmd = [
            "python3", "-m", "mac_notifications.src.daemon.notification_daemon",
            "--db", str(db_path),
            "--interval", str(interval),
            "--log-file", str(self.log_file)
        ]
        
        try:
            if background:
                # Start in background
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                
                # Wait a moment to ensure it started
                time.sleep(2)
                
                # Check if it's running
                if self.is_running():
                    self.logger.info(f"Daemon started successfully (PID: {process.pid})")
                    return True
                else:
                    self.logger.error("Daemon failed to start")
                    return False
            else:
                # Run in foreground
                subprocess.run(cmd)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
            return False
    
    def stop(self, timeout: int = 10) -> bool:
        """Stop the daemon process gracefully"""
        if not self.is_running():
            self.logger.warning("Daemon is not running")
            return False
        
        pid = self._read_pid()
        if pid is None:
            return False
        
        try:
            # Send SIGTERM for graceful shutdown
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to terminate
            start_time = time.time()
            while time.time() - start_time < timeout:
                if not self.is_running():
                    self.logger.info("Daemon stopped successfully")
                    return True
                time.sleep(0.5)
            
            # Force kill if still running
            self.logger.warning("Daemon did not stop gracefully, forcing...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)
            
            if not self.is_running():
                self.logger.info("Daemon force-stopped")
                return True
            else:
                self.logger.error("Failed to stop daemon")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping daemon: {e}")
            return False
    
    def restart(self, db_path: str = "notifications.db", 
                interval: int = 10) -> bool:
        """Restart the daemon"""
        self.logger.info("Restarting daemon...")
        
        # Stop if running
        if self.is_running():
            if not self.stop():
                self.logger.error("Failed to stop daemon for restart")
                return False
        
        # Wait a moment
        time.sleep(2)
        
        # Start again
        return self.start(db_path, interval)
    
    def status(self) -> Dict[str, Any]:
        """Get daemon status information"""
        status = {
            "running": False,
            "pid": None,
            "uptime": None,
            "memory_usage": None,
            "cpu_percent": None
        }
        
        if not self.is_running():
            return status
        
        pid = self._read_pid()
        if pid is None:
            return status
        
        try:
            process = psutil.Process(pid)
            status["running"] = True
            status["pid"] = pid
            status["uptime"] = time.time() - process.create_time()
            status["memory_usage"] = process.memory_info().rss / 1024 / 1024  # MB
            status["cpu_percent"] = process.cpu_percent(interval=1.0)
            
            # Add command line
            status["command"] = ' '.join(process.cmdline())
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return status
    
    def cleanup_stale_processes(self) -> int:
        """Clean up any stale daemon processes"""
        cleaned = 0
        
        # Find all Python processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and self.daemon_script in ' '.join(cmdline):
                    # Check if it's not the current daemon
                    if proc.pid != self._read_pid():
                        self.logger.warning(f"Found stale daemon process {proc.pid}, terminating...")
                        proc.terminate()
                        proc.wait(timeout=5)
                        cleaned += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        
        return cleaned
    
    def _read_pid(self) -> Optional[int]:
        """Read PID from file"""
        if not self.pid_file.exists():
            return None
        
        try:
            return int(self.pid_file.read_text().strip())
        except (ValueError, IOError):
            return None
    
    def _cleanup_pid_file(self):
        """Remove stale PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()


class DaemonMonitor:
    """Monitor daemon health and restart if needed"""
    
    def __init__(self, manager: DaemonManager, check_interval: int = 60):
        self.manager = manager
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.monitoring = False
    
    def start_monitoring(self):
        """Start monitoring daemon health"""
        self.monitoring = True
        
        while self.monitoring:
            try:
                if not self.manager.is_running():
                    self.logger.warning("Daemon not running, attempting restart...")
                    if self.manager.start():
                        self.logger.info("Daemon restarted successfully")
                    else:
                        self.logger.error("Failed to restart daemon")
                else:
                    # Check daemon health
                    status = self.manager.status()
                    
                    # Restart if using too much memory (> 500MB)
                    if status.get("memory_usage", 0) > 500:
                        self.logger.warning(f"Daemon using {status['memory_usage']:.1f}MB, restarting...")
                        self.manager.restart()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False


# Convenience functions for command-line usage
def start_daemon(db_path: str = "notifications.db", interval: int = 10) -> bool:
    """Start the notification daemon"""
    manager = DaemonManager()
    return manager.start(db_path, interval)


def stop_daemon() -> bool:
    """Stop the notification daemon"""
    manager = DaemonManager()
    return manager.stop()


def restart_daemon(db_path: str = "notifications.db", interval: int = 10) -> bool:
    """Restart the notification daemon"""
    manager = DaemonManager()
    return manager.restart(db_path, interval)


def daemon_status() -> Dict[str, Any]:
    """Get daemon status"""
    manager = DaemonManager()
    return manager.status()