"""
Server Updater for V2Ray Client

Handles periodic server list updates and ping measurements.
"""

import socket
import time
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, QThread


class RefreshWorker(QThread):
    """Worker thread for fetching and pinging servers"""
    
    finished = pyqtSignal(list)  # Emits servers when done
    
    def __init__(self, subscription_manager, do_ping=True):
        super().__init__()
        self.subscription_manager = subscription_manager
        self.do_ping = do_ping
        self.servers = []
    
    def run(self):
        """Run the refresh operation in background thread"""
        try:
            # Fetch all subscriptions
            servers = self.subscription_manager.fetch_all_subscriptions()
            
            # Set initial ping to -1 for all servers
            for server in servers:
                server["ping"] = -1
            
            # Emit servers immediately so UI shows them right away
            self.finished.emit(servers)
            
            if self.do_ping and servers:
                # Update ping for each server in parallel (max 100 concurrent threads for speed)
                with ThreadPoolExecutor(max_workers=100) as executor:
                    # Submit all ping tasks
                    future_to_server = {
                        executor.submit(self.ping_server, server.get("ip", ""), server.get("port", 0)): server
                        for server in servers
                    }
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_server):
                        server = future_to_server[future]
                        try:
                            ping = future.result()
                            server["ping"] = ping
                        except Exception:
                            server["ping"] = -1
                
                # Sort servers by ping after all pings complete
                servers = sorted(servers, key=lambda s: (s.get("ping", -1) == -1, s.get("ping", -1)))
                
                # Emit updated servers with ping results
                self.finished.emit(servers)
        except Exception as e:
            print(f"Error in refresh worker: {e}")
            self.finished.emit([])
    
    def ping_server(self, ip: str, port: int, timeout: float = 0.5) -> int:
        """
        Measure ping latency to server using socket connection timing
        
        Args:
            ip: Server IP address
            port: Server port
            timeout: Connection timeout in seconds (default: 0.5)
            
        Returns:
            Latency in milliseconds, -1 if unreachable
        """
        if not ip or port <= 0:
            return -1
        
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Measure connection time
            start_time = time.time()
            result = sock.connect_ex((ip, port))
            end_time = time.time()
            
            # Close socket
            sock.close()
            
            # Check if connection was successful
            if result == 0:
                # Calculate latency in milliseconds
                latency_ms = int((end_time - start_time) * 1000)
                return latency_ms
            else:
                return -1
                
        except socket.gaierror:
            # DNS resolution failed
            return -1
        except socket.timeout:
            # Connection timeout
            return -1
        except Exception:
            # Other errors
            return -1


class ServerUpdater(QObject):
    """Manages periodic server list updates and ping measurements"""
    
    # Signal emitted when servers are updated
    servers_updated = pyqtSignal(list)
    
    def __init__(self, subscription_manager, interval: int = 10):
        """
        Initialize server updater with periodic refresh
        
        Args:
            subscription_manager: SubscriptionManager instance
            interval: Refresh interval in seconds (default: 10)
        """
        super().__init__()
        self.subscription_manager = subscription_manager
        self.interval = interval
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick)
        self.servers = []
        self.initial_ping_done = False
        self.worker = None
        
    def start(self) -> None:
        """Start periodic updates"""
        if not self.timer.isActive():
            self.timer.start(self.interval * 1000)  # Convert to milliseconds
            # Trigger immediate refresh with ping on first start (in background)
            if not self.initial_ping_done:
                self.refresh_with_ping()
            else:
                self.refresh_now()
    
    def stop(self) -> None:
        """Stop periodic updates"""
        if self.timer.isActive():
            self.timer.stop()
    
    def set_interval(self, seconds: int) -> None:
        """
        Change refresh frequency
        
        Args:
            seconds: New interval in seconds (minimum 5)
        """
        # Enforce minimum interval of 5 seconds
        self.interval = max(5, seconds)
        
        # Restart timer with new interval if it's running
        if self.timer.isActive():
            self.timer.stop()
            self.timer.start(self.interval * 1000)
    
    def refresh_now(self) -> None:
        """Trigger manual refresh immediately"""
        self._on_timer_tick()
    
    def _on_timer_tick(self) -> None:
        """Internal method called on timer tick - refreshes without pinging"""
        # Fetch all subscriptions
        servers = self.subscription_manager.fetch_all_subscriptions()
        
        # Keep existing ping values if we already have them
        if self.servers:
            # Create a lookup dict for existing pings
            ping_lookup = {
                (s.get("ip"), s.get("port"), s.get("uuid")): s.get("ping", -1)
                for s in self.servers
            }
            
            # Apply existing pings to new server list
            for server in servers:
                key = (server.get("ip"), server.get("port"), server.get("uuid"))
                if key in ping_lookup:
                    server["ping"] = ping_lookup[key]
                else:
                    server["ping"] = -1
        else:
            # No existing pings, set all to -1
            for server in servers:
                server["ping"] = -1
        
        # Store servers
        self.servers = servers
        
        # Emit signal with updated servers
        self.servers_updated.emit(servers)
    
    def refresh_with_ping(self) -> None:
        """Refresh servers and measure ping for all servers (in background thread)"""
        # Don't start a new worker if one is already running
        if self.worker and self.worker.isRunning():
            return
        
        # Create and start worker thread
        self.worker = RefreshWorker(self.subscription_manager, do_ping=True)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()
    
    def _on_worker_finished(self, servers: List[Dict]) -> None:
        """Handle worker thread completion"""
        self.servers = servers
        self.initial_ping_done = True
        self.servers_updated.emit(servers)
    
    def sort_servers(self, servers: List[Dict], by: str = "ping") -> List[Dict]:
        """
        Sort servers by ping or name
        
        Args:
            servers: List of server configuration dictionaries
            by: Sort key - "ping" or "name" (default: "ping")
            
        Returns:
            Sorted list of servers
        """
        if by == "ping":
            # Sort by ping, putting unreachable servers (-1) at the end
            return sorted(servers, key=lambda s: (s.get("ping", -1) == -1, s.get("ping", -1)))
        elif by == "name":
            # Sort alphabetically by name
            return sorted(servers, key=lambda s: s.get("name", "").lower())
        else:
            # Unknown sort key, return as-is
            return servers
