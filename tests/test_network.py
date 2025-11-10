"""
Network integration tests for V2Ray Client.

Tests real network operations including subscription fetching,
IP info API, ping measurements, and timeout handling.
"""

import pytest
import time
import socket
import requests
from unittest.mock import patch, MagicMock
from subscription_manager import SubscriptionManager, ServerParser
from server_updater import ServerUpdater
from v2ray_manager import V2RayManager


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temporary config directory."""
    return str(tmp_path / "v2ray-test")


@pytest.fixture
def subscription_manager(temp_config_dir):
    """Provide a SubscriptionManager instance."""
    return SubscriptionManager(config_dir=temp_config_dir)


@pytest.fixture
def server_updater(subscription_manager, qtbot):
    """Provide a ServerUpdater instance."""
    return ServerUpdater(subscription_manager, interval=10)


@pytest.fixture
def v2ray_manager(temp_config_dir):
    """Provide a V2RayManager instance."""
    return V2RayManager(config_dir=temp_config_dir)


class TestSubscriptionFetching:
    """Test fetching from real subscription URLs."""
    
    @patch('requests.get')
    def test_fetch_from_test_subscription_url(self, mock_get, subscription_manager):
        """Test fetching subscription from a test URL."""
        # Create a realistic test response with vmess links
        import base64
        import json
        
        # Create sample vmess configurations
        vmess_configs = []
        for i in range(3):
            config = {
                "ps": f"Test Server {i+1}",
                "add": f"test{i+1}.example.com",
                "port": "443",
                "id": f"test-uuid-{i+1}",
                "aid": "0",
                "scy": "auto",
                "net": "ws",
                "tls": "tls"
            }
            json_str = json.dumps(config)
            encoded = base64.b64encode(json_str.encode()).decode()
            vmess_configs.append(f"vmess://{encoded}")
        
        # Join with newlines
        subscription_content = "\n".join(vmess_configs)
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = subscription_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Add test subscription
        subscription_manager.add_subscription(
            "http://test.example.com/subscription",
            "Test Subscription"
        )
        
        # Fetch subscription
        servers = subscription_manager.fetch_subscription(
            "http://test.example.com/subscription"
        )
        
        # Verify servers were parsed correctly
        assert len(servers) == 3
        assert servers[0]["name"] == "Test Server 1"
        assert servers[0]["type"] == "vmess"
        assert servers[0]["ip"] == "test1.example.com"
        assert servers[1]["name"] == "Test Server 2"
        assert servers[2]["name"] == "Test Server 3"
    
    @patch('requests.get')
    def test_fetch_base64_encoded_subscription(self, mock_get, subscription_manager):
        """Test fetching Base64 encoded subscription content."""
        import base64
        import json
        
        # Create vmess link
        config = {
            "ps": "Encoded Server",
            "add": "encoded.example.com",
            "port": "8443",
            "id": "encoded-uuid",
            "aid": "0",
            "scy": "auto",
            "net": "tcp",
            "tls": ""
        }
        json_str = json.dumps(config)
        vmess_link = f"vmess://{base64.b64encode(json_str.encode()).decode()}"
        
        # Encode the entire content in Base64
        encoded_content = base64.b64encode(vmess_link.encode()).decode()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = encoded_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch subscription
        subscription_manager.add_subscription("http://test.com/sub", "Test")
        servers = subscription_manager.fetch_subscription("http://test.com/sub")
        
        # Verify server was decoded and parsed
        assert len(servers) == 1
        assert servers[0]["name"] == "Encoded Server"
        assert servers[0]["ip"] == "encoded.example.com"
    
    @patch('requests.get')
    def test_fetch_multiple_protocol_types(self, mock_get, subscription_manager):
        """Test fetching subscription with mixed protocol types."""
        import base64
        import json
        
        # Create vmess link
        vmess_config = {
            "ps": "VMess Server",
            "add": "vmess.example.com",
            "port": "443",
            "id": "vmess-uuid",
            "aid": "0",
            "scy": "auto",
            "net": "ws",
            "tls": "tls"
        }
        vmess_link = f"vmess://{base64.b64encode(json.dumps(vmess_config).encode()).decode()}"
        
        # Create vless link
        vless_link = "vless://vless-uuid@vless.example.com:443?type=ws&security=tls#VLess%20Server"
        
        # Create trojan link
        trojan_link = "trojan://trojan-pass@trojan.example.com:443?type=tcp#Trojan%20Server"
        
        # Combine all links
        subscription_content = f"{vmess_link}\n{vless_link}\n{trojan_link}"
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = subscription_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch subscription
        subscription_manager.add_subscription("http://test.com/sub", "Test")
        servers = subscription_manager.fetch_subscription("http://test.com/sub")
        
        # Verify all protocol types were parsed
        assert len(servers) == 3
        
        # Check each server type
        server_types = [s["type"] for s in servers]
        assert "vmess" in server_types
        assert "vless" in server_types
        assert "trojan" in server_types
    
    @patch('requests.get')
    def test_fetch_handles_empty_subscription(self, mock_get, subscription_manager):
        """Test handling of empty subscription content."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch subscription
        subscription_manager.add_subscription("http://test.com/sub", "Test")
        servers = subscription_manager.fetch_subscription("http://test.com/sub")
        
        # Should return empty list
        assert servers == []
    
    @patch('requests.get')
    def test_fetch_handles_invalid_links(self, mock_get, subscription_manager):
        """Test handling of invalid server links in subscription."""
        # Mock response with invalid links
        mock_response = MagicMock()
        mock_response.text = "invalid://link\nhttp://not-a-server\nvmess://invalid-base64!!!"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch subscription
        subscription_manager.add_subscription("http://test.com/sub", "Test")
        servers = subscription_manager.fetch_subscription("http://test.com/sub")
        
        # Should return empty list (all links invalid)
        assert servers == []


class TestIPInfoAPI:
    """Test ipinfo.io API reachability."""
    
    @patch('requests.get')
    def test_ipinfo_api_returns_valid_data(self, mock_get, v2ray_manager):
        """Test that ipinfo.io API returns valid IP information."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ip': '203.0.113.42',
            'country': 'US',
            'city': 'San Francisco',
            'region': 'California',
            'org': 'AS15169 Google LLC'
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch public IP
        ip_info = v2ray_manager.get_public_ip()
        
        # Verify data structure
        assert 'ip' in ip_info
        assert 'country' in ip_info
        assert 'city' in ip_info
        assert ip_info['ip'] == '203.0.113.42'
        assert ip_info['country'] == 'US'
        assert ip_info['city'] == 'San Francisco'
    
    @patch('requests.get')
    def test_ipinfo_api_handles_network_error(self, mock_get, v2ray_manager):
        """Test handling of network errors when fetching IP info."""
        # Mock network error
        mock_get.side_effect = requests.RequestException("Network error")
        
        # Fetch public IP
        ip_info = v2ray_manager.get_public_ip()
        
        # Should return empty dict on error
        assert ip_info == {}
    
    @patch('requests.get')
    def test_ipinfo_api_handles_timeout(self, mock_get, v2ray_manager):
        """Test handling of timeout when fetching IP info."""
        # Mock timeout
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        # Fetch public IP
        ip_info = v2ray_manager.get_public_ip()
        
        # Should return empty dict on timeout
        assert ip_info == {}
    
    @patch('requests.get')
    def test_ipinfo_api_handles_invalid_json(self, mock_get, v2ray_manager):
        """Test handling of invalid JSON response."""
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch public IP
        ip_info = v2ray_manager.get_public_ip()
        
        # Should return empty dict on JSON error
        assert ip_info == {}
    
    @patch('requests.get')
    def test_ipinfo_api_handles_http_error(self, mock_get, v2ray_manager):
        """Test handling of HTTP errors (4xx, 5xx)."""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Fetch public IP
        ip_info = v2ray_manager.get_public_ip()
        
        # Should return empty dict on HTTP error
        assert ip_info == {}


class TestPingMeasurement:
    """Test ping measurement accuracy."""
    
    @patch('socket.socket')
    def test_ping_measurement_returns_positive_latency(self, mock_socket_class, server_updater):
        """Test that ping measurement returns positive latency for reachable server."""
        # Mock successful connection
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0  # Success
        mock_socket_class.return_value = mock_socket
        
        # Measure ping
        latency = server_updater.ping_server("8.8.8.8", 443)
        
        # Should return non-negative latency
        assert latency >= 0
        
        # Verify socket was used correctly
        mock_socket.settimeout.assert_called_once()
        mock_socket.connect_ex.assert_called_once_with(("8.8.8.8", 443))
        mock_socket.close.assert_called_once()
    
    @patch('socket.socket')
    def test_ping_measurement_returns_negative_for_unreachable(self, mock_socket_class, server_updater):
        """Test that ping measurement returns -1 for unreachable server."""
        # Mock connection failure
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 1  # Connection refused
        mock_socket_class.return_value = mock_socket
        
        # Measure ping
        latency = server_updater.ping_server("192.0.2.1", 443)
        
        # Should return -1 for unreachable
        assert latency == -1
    
    @patch('socket.socket')
    def test_ping_measurement_respects_timeout(self, mock_socket_class, server_updater):
        """Test that ping measurement respects timeout parameter."""
        # Mock socket
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket
        
        # Measure ping with custom timeout
        server_updater.ping_server("8.8.8.8", 443, timeout=5.0)
        
        # Verify timeout was set
        mock_socket.settimeout.assert_called_once_with(5.0)
    
    @patch('socket.socket')
    def test_ping_measurement_handles_dns_failure(self, mock_socket_class, server_updater):
        """Test that ping measurement handles DNS resolution failures."""
        # Mock DNS error
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.gaierror("Name or service not known")
        mock_socket_class.return_value = mock_socket
        
        # Measure ping
        latency = server_updater.ping_server("invalid.domain.test", 443)
        
        # Should return -1 for DNS error
        assert latency == -1
    
    @patch('socket.socket')
    def test_ping_measurement_handles_socket_timeout(self, mock_socket_class, server_updater):
        """Test that ping measurement handles socket timeout."""
        # Mock timeout
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.timeout()
        mock_socket_class.return_value = mock_socket
        
        # Measure ping
        latency = server_updater.ping_server("192.0.2.1", 443, timeout=1.0)
        
        # Should return -1 for timeout
        assert latency == -1
    
    def test_ping_measurement_validates_input(self, server_updater):
        """Test that ping measurement validates input parameters."""
        # Test empty IP
        assert server_updater.ping_server("", 443) == -1
        
        # Test invalid port
        assert server_updater.ping_server("8.8.8.8", 0) == -1
        assert server_updater.ping_server("8.8.8.8", -1) == -1
    
    @patch('socket.socket')
    def test_ping_measurement_latency_is_reasonable(self, mock_socket_class, server_updater):
        """Test that measured latency is within reasonable bounds."""
        # Mock successful connection with realistic timing
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket
        
        # Measure ping
        latency = server_updater.ping_server("8.8.8.8", 443)
        
        # Latency should be non-negative and less than timeout (2000ms default)
        assert 0 <= latency < 2000


class TestNetworkTimeouts:
    """Test handling of network timeouts."""
    
    @patch('requests.get')
    def test_subscription_fetch_handles_timeout(self, mock_get, subscription_manager):
        """Test that subscription fetch handles timeout gracefully."""
        # Mock timeout
        mock_get.side_effect = requests.Timeout("Connection timeout")
        
        # Add subscription
        subscription_manager.add_subscription("http://slow.example.com/sub", "Slow Sub")
        
        # Fetch subscription
        servers = subscription_manager.fetch_subscription("http://slow.example.com/sub")
        
        # Should return empty list on timeout
        assert servers == []
    
    @patch('requests.get')
    def test_subscription_fetch_timeout_parameter(self, mock_get, subscription_manager):
        """Test that subscription fetch uses timeout parameter."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch subscription
        subscription_manager.add_subscription("http://test.com/sub", "Test")
        subscription_manager.fetch_subscription("http://test.com/sub")
        
        # Verify timeout was used
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert 'timeout' in call_kwargs
        assert call_kwargs['timeout'] == 10
    
    @patch('requests.get')
    def test_ipinfo_fetch_handles_timeout(self, mock_get, v2ray_manager):
        """Test that IP info fetch handles timeout gracefully."""
        # Mock timeout
        mock_get.side_effect = requests.Timeout("Connection timeout")
        
        # Fetch IP info
        ip_info = v2ray_manager.get_public_ip()
        
        # Should return empty dict on timeout
        assert ip_info == {}
    
    @patch('requests.get')
    def test_ipinfo_fetch_timeout_parameter(self, mock_get, v2ray_manager):
        """Test that IP info fetch uses timeout parameter."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {'ip': '1.2.3.4', 'country': 'US', 'city': 'NYC'}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch IP info
        v2ray_manager.get_public_ip()
        
        # Verify timeout was used
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert 'timeout' in call_kwargs
        assert call_kwargs['timeout'] == 10
    
    @patch('requests.get')
    def test_subscription_fetch_handles_connection_error(self, mock_get, subscription_manager):
        """Test that subscription fetch handles connection errors."""
        # Mock connection error
        mock_get.side_effect = requests.ConnectionError("Failed to establish connection")
        
        # Fetch subscription
        subscription_manager.add_subscription("http://unreachable.com/sub", "Test")
        servers = subscription_manager.fetch_subscription("http://unreachable.com/sub")
        
        # Should return empty list on connection error
        assert servers == []


class TestSubscriptionRefreshInterval:
    """Test subscription refresh on interval."""
    
    @patch('requests.get')
    def test_server_updater_refreshes_on_interval(self, mock_get, server_updater, qtbot):
        """Test that server updater refreshes subscriptions on timer interval."""
        import base64
        import json
        
        # Mock subscription response
        config = {
            "ps": "Test Server",
            "add": "test.example.com",
            "port": "443",
            "id": "test-uuid",
            "aid": "0",
            "scy": "auto",
            "net": "ws",
            "tls": "tls"
        }
        vmess_link = f"vmess://{base64.b64encode(json.dumps(config).encode()).decode()}"
        
        mock_response = MagicMock()
        mock_response.text = vmess_link
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Add subscription
        server_updater.subscription_manager.add_subscription("http://test.com/sub", "Test")
        
        # Wait for signal and start updater (start() triggers immediate refresh)
        with qtbot.waitSignal(server_updater.servers_updated, timeout=2000) as blocker:
            server_updater.start()
        
        # Verify servers were updated
        assert len(blocker.args[0]) > 0
        
        # Stop updater
        server_updater.stop()
    
    @patch('requests.get')
    def test_server_updater_interval_can_be_changed(self, mock_get, server_updater, qtbot):
        """Test that refresh interval can be changed."""
        # Set new interval
        server_updater.set_interval(15)
        
        # Verify interval was updated
        assert server_updater.interval == 15
    
    @patch('requests.get')
    def test_server_updater_enforces_minimum_interval(self, mock_get, server_updater, qtbot):
        """Test that minimum interval of 5 seconds is enforced."""
        # Try to set interval below minimum
        server_updater.set_interval(2)
        
        # Should be clamped to minimum
        assert server_updater.interval == 5
    
    @patch('requests.get')
    def test_server_updater_manual_refresh(self, mock_get, server_updater, qtbot):
        """Test that manual refresh works without starting timer."""
        import base64
        import json
        
        # Mock subscription response
        config = {
            "ps": "Manual Test",
            "add": "manual.example.com",
            "port": "443",
            "id": "manual-uuid",
            "aid": "0",
            "scy": "auto",
            "net": "tcp",
            "tls": ""
        }
        vmess_link = f"vmess://{base64.b64encode(json.dumps(config).encode()).decode()}"
        
        mock_response = MagicMock()
        mock_response.text = vmess_link
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Add subscription
        server_updater.subscription_manager.add_subscription("http://test.com/sub", "Test")
        
        # Trigger manual refresh
        with qtbot.waitSignal(server_updater.servers_updated, timeout=2000) as blocker:
            server_updater.refresh_now()
        
        # Verify servers were updated
        assert len(blocker.args[0]) > 0
        assert blocker.args[0][0]["name"] == "Manual Test"
    
    @patch('requests.get')
    @patch('socket.socket')
    def test_server_updater_updates_ping_on_refresh(self, mock_socket_class, mock_get, server_updater, qtbot):
        """Test that server updater measures ping on each refresh."""
        import base64
        import json
        
        # Mock subscription response
        config = {
            "ps": "Ping Test",
            "add": "ping.example.com",
            "port": "443",
            "id": "ping-uuid",
            "aid": "0",
            "scy": "auto",
            "net": "ws",
            "tls": "tls"
        }
        vmess_link = f"vmess://{base64.b64encode(json.dumps(config).encode()).decode()}"
        
        mock_response = MagicMock()
        mock_response.text = vmess_link
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Mock ping
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket
        
        # Add subscription
        server_updater.subscription_manager.add_subscription("http://test.com/sub", "Test")
        
        # Trigger refresh
        with qtbot.waitSignal(server_updater.servers_updated, timeout=2000) as blocker:
            server_updater.refresh_now()
        
        # Verify ping was measured
        servers = blocker.args[0]
        assert len(servers) > 0
        assert servers[0]["ping"] >= 0  # Ping should be measured
