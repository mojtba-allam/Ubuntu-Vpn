"""
Unit tests for ServerUpdater class.
"""

import pytest
import socket
import time
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtCore import QTimer
from server_updater import ServerUpdater


@pytest.fixture
def mock_subscription_manager():
    """Provide a mock SubscriptionManager."""
    manager = MagicMock()
    manager.fetch_all_subscriptions.return_value = []
    return manager


@pytest.fixture
def updater(mock_subscription_manager, qtbot):
    """Provide a ServerUpdater instance."""
    return ServerUpdater(mock_subscription_manager, interval=10)


@pytest.fixture
def sample_servers():
    """Provide sample server configurations."""
    return [
        {
            "name": "Server 1",
            "type": "vmess",
            "ip": "1.2.3.4",
            "port": 443,
            "uuid": "uuid1",
            "ping": -1
        },
        {
            "name": "Server 2",
            "type": "vless",
            "ip": "5.6.7.8",
            "port": 8443,
            "uuid": "uuid2",
            "ping": -1
        },
        {
            "name": "Server 3",
            "type": "trojan",
            "ip": "9.10.11.12",
            "port": 443,
            "uuid": "uuid3",
            "ping": -1
        }
    ]


class TestServerUpdaterInit:
    """Test ServerUpdater initialization."""
    
    def test_init_sets_subscription_manager(self, mock_subscription_manager, qtbot):
        """Test that __init__ sets the subscription manager."""
        updater = ServerUpdater(mock_subscription_manager, interval=10)
        
        assert updater.subscription_manager == mock_subscription_manager
    
    def test_init_sets_interval(self, mock_subscription_manager, qtbot):
        """Test that __init__ sets the refresh interval."""
        updater = ServerUpdater(mock_subscription_manager, interval=15)
        
        assert updater.interval == 15
    
    def test_init_creates_timer(self, mock_subscription_manager, qtbot):
        """Test that __init__ creates a QTimer."""
        updater = ServerUpdater(mock_subscription_manager, interval=10)
        
        assert isinstance(updater.timer, QTimer)
    
    def test_init_timer_not_active(self, updater):
        """Test that timer is not active on initialization."""
        assert updater.timer.isActive() is False
    
    def test_init_empty_servers_list(self, updater):
        """Test that servers list is empty on initialization."""
        assert updater.servers == []


class TestServerUpdaterStartStop:
    """Test ServerUpdater start and stop functionality."""
    
    def test_start_activates_timer(self, updater, qtbot):
        """Test that start() activates the timer."""
        updater.start()
        
        assert updater.timer.isActive() is True
    
    def test_start_triggers_immediate_refresh(self, updater, mock_subscription_manager, qtbot):
        """Test that start() triggers an immediate refresh."""
        updater.start()
        
        # Should call fetch_all_subscriptions
        mock_subscription_manager.fetch_all_subscriptions.assert_called()
    
    def test_stop_deactivates_timer(self, updater, qtbot):
        """Test that stop() deactivates the timer."""
        updater.start()
        updater.stop()
        
        assert updater.timer.isActive() is False
    
    def test_stop_when_not_started(self, updater, qtbot):
        """Test that stop() works when timer is not active."""
        updater.stop()  # Should not raise error
        assert updater.timer.isActive() is False


class TestServerUpdaterInterval:
    """Test ServerUpdater interval management."""
    
    def test_set_interval_changes_interval(self, updater, qtbot):
        """Test that set_interval() changes the refresh interval."""
        updater.set_interval(20)
        
        assert updater.interval == 20
    
    def test_set_interval_enforces_minimum(self, updater, qtbot):
        """Test that set_interval() enforces minimum of 5 seconds."""
        updater.set_interval(2)
        
        assert updater.interval == 5
    
    def test_set_interval_restarts_timer_if_active(self, updater, qtbot):
        """Test that set_interval() restarts timer if it's running."""
        updater.start()
        initial_interval = updater.timer.interval()
        
        updater.set_interval(15)
        
        assert updater.timer.isActive() is True
        assert updater.timer.interval() == 15000  # 15 seconds in milliseconds
    
    def test_set_interval_does_not_start_timer_if_inactive(self, updater, qtbot):
        """Test that set_interval() doesn't start timer if it's not running."""
        updater.set_interval(15)
        
        assert updater.timer.isActive() is False


class TestServerUpdaterRefresh:
    """Test ServerUpdater refresh functionality."""
    
    def test_refresh_now_calls_fetch_all_subscriptions(self, updater, mock_subscription_manager, qtbot):
        """Test that refresh_now() calls fetch_all_subscriptions."""
        updater.refresh_now()
        
        mock_subscription_manager.fetch_all_subscriptions.assert_called()
    
    def test_refresh_now_updates_servers(self, updater, mock_subscription_manager, sample_servers, qtbot):
        """Test that refresh_now() updates the servers list."""
        mock_subscription_manager.fetch_all_subscriptions.return_value = sample_servers.copy()
        
        updater.refresh_now()
        
        assert len(updater.servers) == 3
    
    def test_refresh_now_emits_signal(self, updater, mock_subscription_manager, sample_servers, qtbot):
        """Test that refresh_now() emits servers_updated signal."""
        mock_subscription_manager.fetch_all_subscriptions.return_value = sample_servers.copy()
        
        with qtbot.waitSignal(updater.servers_updated, timeout=1000) as blocker:
            updater.refresh_now()
        
        # Verify signal was emitted with servers
        assert len(blocker.args[0]) == 3
    
    @patch.object(ServerUpdater, 'ping_server')
    def test_refresh_updates_ping_for_each_server(self, mock_ping, updater, mock_subscription_manager, sample_servers, qtbot):
        """Test that refresh updates ping for each server."""
        mock_subscription_manager.fetch_all_subscriptions.return_value = sample_servers.copy()
        mock_ping.return_value = 50
        
        updater.refresh_now()
        
        # Should call ping_server for each server
        assert mock_ping.call_count == 3
        
        # Verify ping was updated in servers
        for server in updater.servers:
            assert server["ping"] == 50


class TestServerUpdaterPing:
    """Test ServerUpdater ping functionality."""
    
    @patch('socket.socket')
    def test_ping_server_returns_latency(self, mock_socket_class, updater, qtbot):
        """Test that ping_server() returns latency in milliseconds."""
        # Mock socket
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0  # Success
        mock_socket_class.return_value = mock_socket
        
        latency = updater.ping_server("1.2.3.4", 443)
        
        assert latency >= 0
        mock_socket.connect_ex.assert_called_once_with(("1.2.3.4", 443))
        mock_socket.close.assert_called_once()
    
    @patch('socket.socket')
    def test_ping_server_returns_negative_on_failure(self, mock_socket_class, updater, qtbot):
        """Test that ping_server() returns -1 on connection failure."""
        # Mock socket with connection failure
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 1  # Connection refused
        mock_socket_class.return_value = mock_socket
        
        latency = updater.ping_server("1.2.3.4", 443)
        
        assert latency == -1
    
    @patch('socket.socket')
    def test_ping_server_handles_timeout(self, mock_socket_class, updater, qtbot):
        """Test that ping_server() handles timeout gracefully."""
        # Mock socket with timeout
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.timeout()
        mock_socket_class.return_value = mock_socket
        
        latency = updater.ping_server("1.2.3.4", 443, timeout=0.5)
        
        assert latency == -1
    
    @patch('socket.socket')
    def test_ping_server_handles_dns_error(self, mock_socket_class, updater, qtbot):
        """Test that ping_server() handles DNS resolution errors."""
        # Mock socket with DNS error
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.gaierror()
        mock_socket_class.return_value = mock_socket
        
        latency = updater.ping_server("invalid.domain", 443)
        
        assert latency == -1
    
    def test_ping_server_invalid_ip(self, updater, qtbot):
        """Test that ping_server() returns -1 for empty IP."""
        latency = updater.ping_server("", 443)
        
        assert latency == -1
    
    def test_ping_server_invalid_port(self, updater, qtbot):
        """Test that ping_server() returns -1 for invalid port."""
        latency = updater.ping_server("1.2.3.4", 0)
        
        assert latency == -1
    
    @patch('socket.socket')
    def test_ping_server_sets_timeout(self, mock_socket_class, updater, qtbot):
        """Test that ping_server() sets socket timeout."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket
        
        updater.ping_server("1.2.3.4", 443, timeout=3.0)
        
        mock_socket.settimeout.assert_called_once_with(3.0)


class TestServerUpdaterSort:
    """Test ServerUpdater sorting functionality."""
    
    def test_sort_servers_by_ping(self, updater, qtbot):
        """Test that sort_servers() sorts by ping latency."""
        servers = [
            {"name": "Server 1", "ping": 100},
            {"name": "Server 2", "ping": 50},
            {"name": "Server 3", "ping": 75}
        ]
        
        sorted_servers = updater.sort_servers(servers, by="ping")
        
        assert sorted_servers[0]["ping"] == 50
        assert sorted_servers[1]["ping"] == 75
        assert sorted_servers[2]["ping"] == 100
    
    def test_sort_servers_by_name(self, updater, qtbot):
        """Test that sort_servers() sorts alphabetically by name."""
        servers = [
            {"name": "Charlie", "ping": 50},
            {"name": "Alice", "ping": 100},
            {"name": "Bob", "ping": 75}
        ]
        
        sorted_servers = updater.sort_servers(servers, by="name")
        
        assert sorted_servers[0]["name"] == "Alice"
        assert sorted_servers[1]["name"] == "Bob"
        assert sorted_servers[2]["name"] == "Charlie"
    
    def test_sort_servers_unreachable_at_end(self, updater, qtbot):
        """Test that unreachable servers (-1 ping) are sorted to the end."""
        servers = [
            {"name": "Server 1", "ping": 100},
            {"name": "Server 2", "ping": -1},
            {"name": "Server 3", "ping": 50},
            {"name": "Server 4", "ping": -1}
        ]
        
        sorted_servers = updater.sort_servers(servers, by="ping")
        
        # First two should have valid pings
        assert sorted_servers[0]["ping"] == 50
        assert sorted_servers[1]["ping"] == 100
        # Last two should be unreachable
        assert sorted_servers[2]["ping"] == -1
        assert sorted_servers[3]["ping"] == -1
    
    def test_sort_servers_unknown_key_returns_unchanged(self, updater, qtbot):
        """Test that sort_servers() returns unchanged list for unknown key."""
        servers = [
            {"name": "Server 1", "ping": 100},
            {"name": "Server 2", "ping": 50}
        ]
        
        sorted_servers = updater.sort_servers(servers, by="unknown")
        
        # Should return in original order
        assert sorted_servers[0]["name"] == "Server 1"
        assert sorted_servers[1]["name"] == "Server 2"
    
    def test_sort_servers_empty_list(self, updater, qtbot):
        """Test that sort_servers() handles empty list."""
        sorted_servers = updater.sort_servers([], by="ping")
        
        assert sorted_servers == []
    
    def test_sort_servers_case_insensitive_name_sort(self, updater, qtbot):
        """Test that name sorting is case-insensitive."""
        servers = [
            {"name": "zebra", "ping": 50},
            {"name": "Apple", "ping": 100},
            {"name": "banana", "ping": 75}
        ]
        
        sorted_servers = updater.sort_servers(servers, by="name")
        
        assert sorted_servers[0]["name"] == "Apple"
        assert sorted_servers[1]["name"] == "banana"
        assert sorted_servers[2]["name"] == "zebra"
