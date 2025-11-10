"""
V2Ray Connection Manager

Manages V2Ray process lifecycle, configuration, and connection state.
"""

import os
import json
import subprocess
import threading
from pathlib import Path
from typing import Optional, Callable
import requests


class V2RayManager:
    """Manages V2Ray process lifecycle and connection state."""
    
    def __init__(self, config_dir: str = "~/.config/v2ray-client"):
        """
        Initialize V2Ray manager with configuration directory.
        
        Args:
            config_dir: Directory path for storing V2Ray configurations
        """
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_config_path = self.config_dir / "temp_config.json"
        self.process: Optional[subprocess.Popen] = None
        self.log_buffer = []
        self.log_lock = threading.Lock()
        self.log_thread: Optional[threading.Thread] = None
        self.log_callback: Optional[Callable] = None
        self._stop_logging = threading.Event()
    
    def connect(self, server_config: dict) -> tuple[bool, str]:
        """
        Start V2Ray with given server configuration.
        
        Args:
            server_config: Dictionary containing server configuration
            
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        # Disconnect if already connected
        if self.is_connected():
            self.disconnect()
        
        try:
            print("\n" + "="*60)
            print("🚀 CONNECTING TO V2RAY SERVER")
            print("="*60)
            
            # Save configuration to temp file
            print(f"📝 Saving config to: {self.temp_config_path}")
            with open(self.temp_config_path, 'w') as f:
                json.dump(server_config, f, indent=2)
            print("✅ Config saved successfully")
            
            # Check if v2ray binary exists
            import shutil
            v2ray_path = shutil.which('v2ray')
            if not v2ray_path:
                error_msg = "V2Ray binary not found. Please install V2Ray first."
                print(f"❌ ERROR: {error_msg}")
                return False, error_msg
            
            print(f"✅ V2Ray binary found at: {v2ray_path}")
            
            # Start V2Ray process
            print("🔄 Starting V2Ray process...")
            self.process = subprocess.Popen(
                ['v2ray', 'run', '-config', str(self.temp_config_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print(f"✅ Process started with PID: {self.process.pid}")
            
            # Start log streaming
            self._stop_logging.clear()
            self.log_thread = threading.Thread(target=self._stream_logs_internal, daemon=True)
            self.log_thread.start()
            print("✅ Log streaming started")
            
            # Give process a moment to start
            import time
            print("⏳ Waiting for V2Ray to initialize...")
            time.sleep(1.0)
            
            # Check if process is still running
            if self.process.poll() is not None:
                # Process died, get error output
                stderr_output = ""
                if self.process.stderr:
                    stderr_output = self.process.stderr.read()
                
                error_msg = f"V2Ray process terminated unexpectedly.\n{stderr_output}"
                print(f"❌ ERROR: {error_msg}")
                print("="*60 + "\n")
                return False, error_msg
            
            print("✅ V2Ray is running successfully!")
            print("="*60 + "\n")
            return True, ""
            
        except FileNotFoundError as e:
            error_msg = f"V2Ray binary not found: {e}"
            print(f"❌ ERROR: {error_msg}")
            print("="*60 + "\n")
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to start V2Ray: {str(e)}"
            print(f"❌ ERROR: {error_msg}")
            print("="*60 + "\n")
            return False, error_msg
    
    def disconnect(self) -> bool:
        """
        Stop V2Ray process and cleanup configuration.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            # Stop log streaming
            self._stop_logging.set()
            if self.log_thread and self.log_thread.is_alive():
                self.log_thread.join(timeout=1.0)
            
            # Terminate process
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
            
            # Delete temporary config file
            if self.temp_config_path.exists():
                self.temp_config_path.unlink()
            
            # Clear log buffer
            with self.log_lock:
                self.log_buffer.clear()
            
            return True
            
        except Exception as e:
            return False
    
    def is_connected(self) -> bool:
        """
        Check if V2Ray process is currently running.
        
        Returns:
            True if process is running, False otherwise
        """
        if self.process is None:
            return False
        
        # Check if process is still running
        return self.process.poll() is None

    def get_public_ip(self) -> dict:
        """
        Fetch public IP information from ipinfo.io API.
        
        Returns:
            Dictionary with keys: 'ip', 'country', 'city'
            Returns empty dict on error
        """
        try:
            response = requests.get('https://ipinfo.io/json', timeout=3)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'ip': data.get('ip', ''),
                'country': data.get('country', ''),
                'city': data.get('city', '')
            }
            
        except requests.RequestException:
            return {}
        except Exception:
            return {}

    def get_logs(self) -> str:
        """
        Get recent V2Ray process logs.
        
        Returns:
            String containing recent log output
        """
        with self.log_lock:
            return '\n'.join(self.log_buffer)
    
    def stream_logs(self, callback: Callable[[str], None]) -> None:
        """
        Set callback for real-time log updates.
        
        Args:
            callback: Function to call with each new log line
        """
        self.log_callback = callback
    
    def _stream_logs_internal(self) -> None:
        """
        Internal method to stream logs from V2Ray process.
        Runs in a separate thread.
        """
        if not self.process:
            return
        
        # Read from both stdout and stderr
        import select
        
        while not self._stop_logging.is_set() and self.process:
            # Check if process is still running
            if self.process.poll() is not None:
                break
            
            try:
                # Read stdout
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        line = line.rstrip()
                        self._add_log_line(line)
                
                # Read stderr
                if self.process.stderr:
                    line = self.process.stderr.readline()
                    if line:
                        line = line.rstrip()
                        self._add_log_line(line)
                
            except Exception:
                break
    
    def _add_log_line(self, line: str) -> None:
        """
        Add a log line to buffer and call callback if set.
        
        Args:
            line: Log line to add
        """
        with self.log_lock:
            self.log_buffer.append(line)
            
            # Limit buffer to 10,000 lines
            if len(self.log_buffer) > 10000:
                self.log_buffer.pop(0)
        
        # Call callback if set
        if self.log_callback:
            try:
                self.log_callback(line)
            except Exception:
                pass
