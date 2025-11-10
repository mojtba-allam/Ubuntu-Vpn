"""
Subscription Manager for V2Ray Client

Handles fetching, parsing, and managing V2Ray server subscriptions.
"""

import json
import os
import base64
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime


class SubscriptionManager:
    """Manages V2Ray subscription URLs and server lists"""
    
    def __init__(self, config_dir: str = "~/.config/v2ray-client"):
        """
        Initialize subscription manager
        
        Args:
            config_dir: Directory to store subscription configuration
        """
        self.config_dir = os.path.expanduser(config_dir)
        self.subscriptions_file = os.path.join(self.config_dir, "subscriptions.json")
        self.subscriptions = []
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load existing subscriptions
        self._load_subscriptions()
    
    def _load_subscriptions(self) -> None:
        """Load subscriptions from config file"""
        if os.path.exists(self.subscriptions_file):
            try:
                with open(self.subscriptions_file, 'r') as f:
                    self.subscriptions = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading subscriptions: {e}")
                self.subscriptions = []
        else:
            self.subscriptions = []
    
    def _save_subscriptions(self) -> None:
        """Save subscriptions to config file"""
        try:
            with open(self.subscriptions_file, 'w') as f:
                json.dump(self.subscriptions, f, indent=2)
        except IOError as e:
            print(f"Error saving subscriptions: {e}")
    
    def add_subscription(self, url: str, name: str = "") -> bool:
        """
        Add new subscription URL
        
        Args:
            url: Subscription URL
            name: Optional user-defined name
            
        Returns:
            True if subscription was added successfully
        """
        # Check if URL already exists
        for sub in self.subscriptions:
            if sub["url"] == url:
                return False
        
        # Create subscription entry
        subscription = {
            "url": url,
            "name": name or url,
            "last_update": None,
            "server_count": 0,
            "enabled": True
        }
        
        self.subscriptions.append(subscription)
        self._save_subscriptions()
        return True
    
    def remove_subscription(self, url: str) -> bool:
        """
        Remove subscription URL
        
        Args:
            url: Subscription URL to remove
            
        Returns:
            True if subscription was removed successfully
        """
        initial_count = len(self.subscriptions)
        self.subscriptions = [sub for sub in self.subscriptions if sub["url"] != url]
        
        if len(self.subscriptions) < initial_count:
            self._save_subscriptions()
            return True
        return False
    
    def get_subscriptions(self) -> List[Dict]:
        """
        Get list of configured subscriptions
        
        Returns:
            List of subscription dictionaries
        """
        return self.subscriptions.copy()
    
    def fetch_subscription(self, url: str) -> List[Dict]:
        """
        Fetch and parse servers from subscription URL
        
        Args:
            url: Subscription URL to fetch
            
        Returns:
            List of server configuration dictionaries
        """
        print(f"\n📡 Fetching subscription from: {url}")
        
        try:
            # Fetch content with shorter timeout
            print("⏳ Sending HTTP request...")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            content = response.text
            print(f"✅ Received {len(content)} bytes")
            
            # Try to decode Base64 if content looks encoded
            try:
                print("🔓 Attempting Base64 decode...")
                decoded = base64.b64decode(content).decode('utf-8')
                content = decoded
                print("✅ Base64 decoded successfully")
            except Exception:
                # Not Base64 encoded, use as-is
                print("ℹ️  Content is not Base64 encoded, using as-is")
                pass
            
            # Parse server links
            servers = []
            lines = content.strip().split('\n')
            print(f"📋 Parsing {len(lines)} lines...")
            
            vmess_count = 0
            vless_count = 0
            trojan_count = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('vmess://'):
                    server = ServerParser.parse_vmess(line)
                    if server:
                        servers.append(server)
                        vmess_count += 1
                elif line.startswith('vless://'):
                    server = ServerParser.parse_vless(line)
                    if server:
                        servers.append(server)
                        vless_count += 1
                elif line.startswith('trojan://'):
                    server = ServerParser.parse_trojan(line)
                    if server:
                        servers.append(server)
                        trojan_count += 1
            
            print(f"✅ Parsed {len(servers)} servers:")
            print(f"   - VMess: {vmess_count}")
            print(f"   - VLess: {vless_count}")
            print(f"   - Trojan: {trojan_count}")
            
            # Update subscription metadata
            for sub in self.subscriptions:
                if sub["url"] == url:
                    sub["last_update"] = datetime.now().isoformat()
                    sub["server_count"] = len(servers)
                    self._save_subscriptions()
                    break
            
            return servers
            
        except requests.RequestException as e:
            print(f"❌ Error fetching subscription: {e}")
            return []
        except Exception as e:
            print(f"❌ Error parsing subscription: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_all_subscriptions(self) -> List[Dict]:
        """
        Fetch all subscriptions and merge servers
        
        Returns:
            Merged and deduplicated list of server configurations
        """
        all_servers = []
        
        for subscription in self.subscriptions:
            if not subscription.get("enabled", True):
                continue
            
            servers = self.fetch_subscription(subscription["url"])
            all_servers.extend(servers)
        
        # Load manual servers
        manual_servers = self._load_manual_servers()
        all_servers.extend(manual_servers)
        
        # Deduplicate servers
        deduplicated = ServerParser.deduplicate_servers(all_servers)
        
        return deduplicated
    
    def _load_manual_servers(self) -> List[Dict]:
        """
        Load manually added servers from file.
        
        Returns:
            List of manually added server configurations
        """
        manual_servers_file = os.path.join(self.config_dir, "manual_servers.json")
        
        if not os.path.exists(manual_servers_file):
            return []
        
        try:
            with open(manual_servers_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading manual servers: {e}")
            return []



class ServerParser:
    """Parses different V2Ray server protocol formats"""
    
    @staticmethod
    def parse_vmess(link: str) -> Optional[Dict]:
        """
        Parse vmess:// link to configuration dict
        
        Args:
            link: vmess:// protocol link
            
        Returns:
            Server configuration dictionary or None if parsing fails
        """
        try:
            # Remove vmess:// prefix
            if not link.startswith('vmess://'):
                return None
            
            encoded = link[8:]
            
            # Fix base64 padding if needed
            padding = len(encoded) % 4
            if padding:
                encoded += '=' * (4 - padding)
            
            # Decode Base64
            decoded = base64.b64decode(encoded).decode('utf-8')
            config = json.loads(decoded)
            
            # Extract server information
            server = {
                "name": config.get("ps", "Unknown"),
                "type": "vmess",
                "ip": config.get("add", ""),
                "port": int(config.get("port", 0)),
                "uuid": config.get("id", ""),
                "alterId": int(config.get("aid", 0)),
                "security": config.get("scy", "auto"),
                "network": config.get("net", "tcp"),
                "tls": config.get("tls", "") == "tls",
                "sni": config.get("sni", ""),
                "path": config.get("path", ""),
                "ping": -1,
                "country_code": ""
            }
            
            return server
            
        except Exception:
            # Silently skip invalid vmess links
            return None
    
    @staticmethod
    def parse_vless(link: str) -> Optional[Dict]:
        """
        Parse vless:// link to configuration dict
        
        Args:
            link: vless:// protocol link
            
        Returns:
            Server configuration dictionary or None if parsing fails
        """
        try:
            # Remove vless:// prefix
            if not link.startswith('vless://'):
                return None
            
            link = link[8:]
            
            # Parse URL structure: uuid@host:port?params#name
            if '@' not in link:
                return None
            
            uuid, rest = link.split('@', 1)
            
            if ':' not in rest:
                return None
            
            # Extract host and port
            host_port, rest = rest.split('?', 1) if '?' in rest else (rest, '')
            host, port = host_port.rsplit(':', 1)
            
            # Parse query parameters
            params = {}
            name = ""
            
            if rest:
                if '#' in rest:
                    query_part, name = rest.split('#', 1)
                    name = unquote(name)
                else:
                    query_part = rest
                
                params = parse_qs(query_part)
                # Convert lists to single values
                params = {k: v[0] if v else "" for k, v in params.items()}
            
            server = {
                "name": name or "Unknown",
                "type": "vless",
                "ip": host,
                "port": int(port),
                "uuid": uuid,
                "alterId": 0,
                "security": params.get("security", "none"),
                "network": params.get("type", "tcp"),
                "tls": params.get("security", "") == "tls",
                "sni": params.get("sni", ""),
                "path": params.get("path", ""),
                "ping": -1,
                "country_code": ""
            }
            
            return server
            
        except Exception as e:
            print(f"Error parsing vless link: {e}")
            return None
    
    @staticmethod
    def parse_trojan(link: str) -> Optional[Dict]:
        """
        Parse trojan:// link to configuration dict
        
        Args:
            link: trojan:// protocol link
            
        Returns:
            Server configuration dictionary or None if parsing fails
        """
        try:
            # Remove trojan:// prefix
            if not link.startswith('trojan://'):
                return None
            
            link = link[9:]
            
            # Parse URL structure: password@host:port?params#name
            if '@' not in link:
                return None
            
            password, rest = link.split('@', 1)
            
            if ':' not in rest:
                return None
            
            # Extract host and port
            host_port, rest = rest.split('?', 1) if '?' in rest else (rest, '')
            host, port = host_port.rsplit(':', 1)
            
            # Parse query parameters
            params = {}
            name = ""
            
            if rest:
                if '#' in rest:
                    query_part, name = rest.split('#', 1)
                    name = unquote(name)
                else:
                    query_part = rest
                
                params = parse_qs(query_part)
                # Convert lists to single values
                params = {k: v[0] if v else "" for k, v in params.items()}
            
            server = {
                "name": name or "Unknown",
                "type": "trojan",
                "ip": host,
                "port": int(port),
                "uuid": password,  # Trojan uses password field
                "alterId": 0,
                "security": "tls",  # Trojan always uses TLS
                "network": params.get("type", "tcp"),
                "tls": True,
                "sni": params.get("sni", ""),
                "path": params.get("path", ""),
                "ping": -1,
                "country_code": ""
            }
            
            return server
            
        except Exception as e:
            print(f"Error parsing trojan link: {e}")
            return None
    
    @staticmethod
    def deduplicate_servers(servers: List[Dict]) -> List[Dict]:
        """
        Remove duplicate servers based on IP, port, and UUID
        
        Args:
            servers: List of server configurations
            
        Returns:
            Deduplicated list of servers
        """
        seen = set()
        unique_servers = []
        
        for server in servers:
            # Create unique key from protocol, ip, port, and uuid
            key = (
                server.get("type", ""),
                server.get("ip", ""),
                server.get("port", 0),
                server.get("uuid", "")
            )
            
            if key not in seen:
                seen.add(key)
                unique_servers.append(server)
        
        return unique_servers
