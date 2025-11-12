"""
Hysteria2 Client Manager

Handles Hysteria2 connections for VPN functionality.
"""

import os
import subprocess
import threading
import time
import json
import tempfile
from typing import Dict, Optional, Tuple


class Hysteria2Manager:
    """Manages Hysteria2 client connections"""

    def __init__(self, config_dir: str):
        """
        Initialize Hysteria2 manager.

        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = os.path.expanduser(config_dir)
        self.config_file = ""
        self.process = None
        self.is_running = False
        self.logs = []

        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)

        # Check for Hysteria2 client
        self.hysteria_client = self._find_hysteria_client()

    def _find_hysteria_client(self) -> Optional[str]:
        """
        Find Hysteria2 client binary.

        Returns:
            Path to Hysteria2 client or None if not found
        """
        # Check common locations
        possible_paths = [
            "/usr/local/bin/hysteria",
            "/usr/bin/hysteria",
            os.path.expanduser("~/bin/hysteria"),
            "./hysteria",
            "./hysteria-linux-amd64"
        ]

        for path in possible_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path

        return None

    def parse_hysteria2_url(self, url: str) -> Dict:
        """
        Parse Hysteria2 URL into configuration.

        Args:
            url: Hysteria2 URL (hysteria2://password@server:port?params)

        Returns:
            Configuration dictionary
        """
        from urllib.parse import urlparse, parse_qs, unquote

        try:
            parsed = urlparse(url)

            config = {
                "type": "hysteria2",
                "server": parsed.hostname,
                "port": parsed.port,
                "password": parsed.username,
                "sni": None,
                "obfs": None,
                "obfs_password": None,
                "insecure": False,
                "name": unquote(parsed.fragment) if parsed.fragment else "Hysteria2 Server"
            }

            # Parse query parameters
            params = parse_qs(parsed.query)

            if "sni" in params:
                config["sni"] = params["sni"][0]

            if "obfs" in params:
                config["obfs"] = params["obfs"][0]

            if "obfs-password" in params:
                config["obfs_password"] = params["obfs-password"][0]

            if "insecure" in params:
                config["insecure"] = params["insecure"][0] in ("1", "true", "yes")

            return config

        except Exception as e:
            raise ValueError(f"Invalid Hysteria2 URL: {e}")

    def generate_config(self, server_config: Dict) -> str:
        """
        Generate Hysteria2 configuration file.

        Args:
            server_config: Server configuration dictionary

        Returns:
            Path to generated config file
        """
        config = {
            "server": f"{server_config['server']}:{server_config['port']}",
            "auth": server_config["password"],
            "bandwidth": {
                "up": "50 mbps",
                "down": "50 mbps"
            },
            "socks5": {
                "listen": "127.0.0.1:1080"
            },
            "http": {
                "listen": "127.0.0.1:1081"
            }
        }

        # Add optional parameters
        if server_config.get("sni"):
            config["sni"] = server_config["sni"]

        if server_config.get("insecure"):
            config["insecure"] = server_config["insecure"]

        if server_config.get("obfs") and server_config.get("obfs_password"):
            config["obfs"] = f"{server_config['obfs']}:{server_config['obfs_password']}"

        # Create temporary config file
        fd, config_file = tempfile.mkstemp(suffix='.json', prefix='hysteria_', dir=self.config_dir)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            os.close(fd)
            if os.path.exists(config_file):
                os.unlink(config_file)
            raise

        self.config_file = config_file
        return config_file

    def connect(self, server_config: Dict) -> Tuple[bool, str]:
        """
        Connect to Hysteria2 server.

        Args:
            server_config: Server configuration dictionary

        Returns:
            Tuple of (success, error_message)
        """
        if not self.hysteria_client:
            return False, "Hysteria2 client not found. Please install Hysteria2."

        if self.is_running:
            return False, "Already connected to a server."

        try:
            # Generate configuration file
            config_file = self.generate_config(server_config)

            # Start Hysteria2 client
            cmd = [self.hysteria_client, "-c", config_file, "client"]

            print(f"🚀 Starting Hysteria2 client...")
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Config: {config_file}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Start log monitoring thread
            log_thread = threading.Thread(target=self._monitor_logs, daemon=True)
            log_thread.start()

            # Wait a moment to check if process starts successfully
            time.sleep(2)

            if self.process.poll() is None:  # Process still running
                self.is_running = True
                print("✅ Hysteria2 client started successfully")
                return True, ""
            else:
                # Process exited immediately - get error
                stdout, _ = self.process.communicate()
                return False, f"Hysteria2 client failed to start: {stdout}"

        except Exception as e:
            return False, f"Failed to start Hysteria2 client: {str(e)}"

    def disconnect(self) -> bool:
        """
        Disconnect from Hysteria2 server.

        Returns:
            True if disconnected successfully
        """
        if not self.is_running or not self.process:
            return True

        try:
            print("🛑 Stopping Hysteria2 client...")
            self.process.terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()  # Force kill if doesn't stop gracefully
                self.process.wait()

            self.is_running = False
            self.process = None

            # Clean up config file
            if self.config_file and os.path.exists(self.config_file):
                os.unlink(self.config_file)
                self.config_file = ""

            print("✅ Hysteria2 client stopped")
            return True

        except Exception as e:
            print(f"❌ Error stopping Hysteria2 client: {e}")
            return False

    def is_connected(self) -> bool:
        """
        Check if connected to Hysteria2 server.

        Returns:
            True if connected
        """
        if self.is_running and self.process:
            # Check if process is still alive
            if self.process.poll() is None:
                return True
            else:
                # Process died
                self.is_running = False
                self.process = None
                return False
        return False

    def get_logs(self) -> str:
        """
        Get Hysteria2 client logs.

        Returns:
            Log output string
        """
        return "\\n".join(self.logs)

    def _monitor_logs(self):
        """Monitor Hysteria2 client output and store logs"""
        if not self.process:
            return

        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    log_line = line.strip()
                    self.logs.append(log_line)
                    print(f"[Hysteria2] {log_line}")

                    # Keep only last 1000 log lines
                    if len(self.logs) > 1000:
                        self.logs = self.logs[-1000:]

        except Exception as e:
            print(f"Error monitoring Hysteria2 logs: {e}")

    def get_public_ip(self) -> Optional[Dict]:
        """
        Get public IP information when connected.

        Returns:
            Dictionary with IP info or None if failed
        """
        try:
            import requests

            # Use ipinfo.io through HTTP proxy
            proxies = {
                'http': 'http://127.0.0.1:1081',
                'https': 'http://127.0.0.1:1081'
            }

            response = requests.get(
                'https://ipinfo.io/json',
                proxies=proxies,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'ip': data.get('ip', 'N/A'),
                    'country': data.get('country', 'N/A'),
                    'city': data.get('city', 'N/A'),
                    'org': data.get('org', 'N/A')
                }

        except Exception as e:
            print(f"Failed to get public IP: {e}")

        return None