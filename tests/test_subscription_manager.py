"""
Unit tests for SubscriptionManager and ServerParser classes.
"""

import pytest
import json
import base64
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from subscription_manager import SubscriptionManager, ServerParser


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temporary config directory."""
    return str(tmp_path / "v2ray-test")


@pytest.fixture
def manager(temp_config_dir):
    """Provide a SubscriptionManager instance with temp directory."""
    return SubscriptionManager(config_dir=temp_config_dir)


@pytest.fixture
def sample_vmess_config():
    """Provide a sample vmess configuration."""
    return {
        "ps": "Test Server",
        "add": "example.com",
        "port": "443",
        "id": "test-uuid-1234",
        "aid": "0",
        "scy": "auto",
        "net": "ws",
        "tls": "tls",
        "sni": "example.com",
        "path": "/path"
    }


@pytest.fixture
def sample_vmess_link(sample_vmess_config):
    """Provide a sample vmess:// link."""
    json_str = json.dumps(sample_vmess_config)
    encoded = base64.b64encode(json_str.encode()).decode()
    return f"vmess://{encoded}"


class TestSubscriptionManagerInit:
    """Test SubscriptionManager initialization."""
    
    def test_init_creates_config_directory(self, temp_config_dir):
        """Test that __init__ creates the config directory."""
        manager = SubscriptionManager(config_dir=temp_config_dir)
        
        config_path = Path(temp_config_dir).expanduser()
        assert config_path.exists()
        assert config_path.is_dir()
    
    def test_init_loads_empty_subscriptions(self, manager):
        """Test that __init__ initializes empty subscriptions list."""
        assert manager.subscriptions == []
    
    def test_init_loads_existing_subscriptions(self, temp_config_dir):
        """Test that __init__ loads existing subscriptions from file."""
        # Create subscriptions file
        config_path = Path(temp_config_dir).expanduser()
        config_path.mkdir(parents=True, exist_ok=True)
        
        subscriptions_file = config_path / "subscriptions.json"
        test_subs = [
            {"url": "http://test.com", "name": "Test", "enabled": True}
        ]
        
        with open(subscriptions_file, 'w') as f:
            json.dump(test_subs, f)
        
        manager = SubscriptionManager(config_dir=temp_config_dir)
        assert len(manager.subscriptions) == 1
        assert manager.subscriptions[0]["url"] == "http://test.com"


class TestSubscriptionManagerAddRemove:
    """Test subscription URL addition and removal."""
    
    def test_add_subscription_success(self, manager):
        """Test adding a new subscription URL."""
        result = manager.add_subscription("http://example.com/sub", "Test Sub")
        
        assert result is True
        assert len(manager.subscriptions) == 1
        assert manager.subscriptions[0]["url"] == "http://example.com/sub"
        assert manager.subscriptions[0]["name"] == "Test Sub"
        assert manager.subscriptions[0]["enabled"] is True
    
    def test_add_subscription_duplicate_returns_false(self, manager):
        """Test that adding duplicate URL returns False."""
        manager.add_subscription("http://example.com/sub", "Test")
        result = manager.add_subscription("http://example.com/sub", "Test2")
        
        assert result is False
        assert len(manager.subscriptions) == 1
    
    def test_add_subscription_without_name(self, manager):
        """Test adding subscription without custom name uses URL."""
        result = manager.add_subscription("http://example.com/sub")
        
        assert result is True
        assert manager.subscriptions[0]["name"] == "http://example.com/sub"
    
    def test_remove_subscription_success(self, manager):
        """Test removing an existing subscription."""
        manager.add_subscription("http://example.com/sub", "Test")
        result = manager.remove_subscription("http://example.com/sub")
        
        assert result is True
        assert len(manager.subscriptions) == 0
    
    def test_remove_subscription_not_found(self, manager):
        """Test removing non-existent subscription returns False."""
        result = manager.remove_subscription("http://notfound.com")
        
        assert result is False
    
    def test_get_subscriptions_returns_copy(self, manager):
        """Test that get_subscriptions returns a copy of the list."""
        manager.add_subscription("http://example.com/sub", "Test")
        subs = manager.get_subscriptions()
        
        # Modify returned list
        subs.append({"url": "fake"})
        
        # Original should be unchanged
        assert len(manager.subscriptions) == 1


class TestSubscriptionManagerFetch:
    """Test subscription fetching and parsing."""
    
    @patch('requests.get')
    def test_fetch_subscription_plain_text(self, mock_get, manager, sample_vmess_link):
        """Test fetching subscription with plain text content."""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = sample_vmess_link
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        manager.add_subscription("http://example.com/sub", "Test")
        servers = manager.fetch_subscription("http://example.com/sub")
        
        assert len(servers) == 1
        assert servers[0]["name"] == "Test Server"
        assert servers[0]["type"] == "vmess"
        assert servers[0]["ip"] == "example.com"
    
    @patch('requests.get')
    def test_fetch_subscription_base64_encoded(self, mock_get, manager, sample_vmess_link):
        """Test fetching subscription with Base64 encoded content."""
        # Encode the link in Base64
        encoded_content = base64.b64encode(sample_vmess_link.encode()).decode()
        
        mock_response = MagicMock()
        mock_response.text = encoded_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        manager.add_subscription("http://example.com/sub", "Test")
        servers = manager.fetch_subscription("http://example.com/sub")
        
        assert len(servers) == 1
        assert servers[0]["type"] == "vmess"
    
    @patch('requests.get')
    def test_fetch_subscription_multiple_servers(self, mock_get, manager, sample_vmess_link):
        """Test fetching subscription with multiple server links."""
        # Create multiple links
        content = f"{sample_vmess_link}\n{sample_vmess_link}"
        
        mock_response = MagicMock()
        mock_response.text = content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        manager.add_subscription("http://example.com/sub", "Test")
        servers = manager.fetch_subscription("http://example.com/sub")
        
        assert len(servers) == 2
    
    @patch('requests.get')
    def test_fetch_subscription_handles_network_error(self, mock_get, manager):
        """Test that fetch handles network errors gracefully."""
        mock_get.side_effect = Exception("Network error")
        
        manager.add_subscription("http://example.com/sub", "Test")
        servers = manager.fetch_subscription("http://example.com/sub")
        
        assert servers == []
    
    @patch('requests.get')
    def test_fetch_subscription_updates_metadata(self, mock_get, manager, sample_vmess_link):
        """Test that fetch updates subscription metadata."""
        mock_response = MagicMock()
        mock_response.text = sample_vmess_link
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        manager.add_subscription("http://example.com/sub", "Test")
        servers = manager.fetch_subscription("http://example.com/sub")
        
        sub = manager.subscriptions[0]
        assert sub["last_update"] is not None
        assert sub["server_count"] == 1
    
    @patch('requests.get')
    def test_fetch_all_subscriptions_merges_servers(self, mock_get, manager, sample_vmess_link):
        """Test that fetch_all_subscriptions merges all sources."""
        mock_response = MagicMock()
        mock_response.text = sample_vmess_link
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        manager.add_subscription("http://example1.com/sub", "Test1")
        manager.add_subscription("http://example2.com/sub", "Test2")
        
        servers = manager.fetch_all_subscriptions()
        
        # Should have servers from both subscriptions (deduplicated)
        assert len(servers) >= 1
    
    @patch('requests.get')
    def test_fetch_all_subscriptions_skips_disabled(self, mock_get, manager, sample_vmess_link):
        """Test that fetch_all_subscriptions skips disabled subscriptions."""
        mock_response = MagicMock()
        mock_response.text = sample_vmess_link
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        manager.add_subscription("http://example.com/sub", "Test")
        manager.subscriptions[0]["enabled"] = False
        
        servers = manager.fetch_all_subscriptions()
        
        assert len(servers) == 0


class TestServerParserVmess:
    """Test vmess:// link parsing."""
    
    def test_parse_vmess_valid_link(self, sample_vmess_link):
        """Test parsing valid vmess:// link."""
        server = ServerParser.parse_vmess(sample_vmess_link)
        
        assert server is not None
        assert server["name"] == "Test Server"
        assert server["type"] == "vmess"
        assert server["ip"] == "example.com"
        assert server["port"] == 443
        assert server["uuid"] == "test-uuid-1234"
        assert server["network"] == "ws"
        assert server["tls"] is True
    
    def test_parse_vmess_invalid_prefix(self):
        """Test parsing link without vmess:// prefix."""
        server = ServerParser.parse_vmess("invalid://link")
        
        assert server is None
    
    def test_parse_vmess_invalid_base64(self):
        """Test parsing link with invalid Base64."""
        server = ServerParser.parse_vmess("vmess://invalid-base64!!!")
        
        assert server is None
    
    def test_parse_vmess_invalid_json(self):
        """Test parsing link with invalid JSON."""
        encoded = base64.b64encode(b"not json").decode()
        server = ServerParser.parse_vmess(f"vmess://{encoded}")
        
        assert server is None


class TestServerParserVless:
    """Test vless:// link parsing."""
    
    def test_parse_vless_valid_link(self):
        """Test parsing valid vless:// link."""
        link = "vless://uuid-1234@example.com:443?type=ws&security=tls&sni=example.com&path=/path#Test%20Server"
        server = ServerParser.parse_vless(link)
        
        assert server is not None
        assert server["name"] == "Test Server"
        assert server["type"] == "vless"
        assert server["ip"] == "example.com"
        assert server["port"] == 443
        assert server["uuid"] == "uuid-1234"
        assert server["network"] == "ws"
        assert server["tls"] is True
        assert server["sni"] == "example.com"
    
    def test_parse_vless_without_params(self):
        """Test parsing vless:// link without query parameters."""
        link = "vless://uuid-1234@example.com:443"
        server = ServerParser.parse_vless(link)
        
        assert server is not None
        assert server["uuid"] == "uuid-1234"
        assert server["ip"] == "example.com"
        assert server["port"] == 443
    
    def test_parse_vless_invalid_format(self):
        """Test parsing malformed vless:// link."""
        server = ServerParser.parse_vless("vless://invalid")
        
        assert server is None
    
    def test_parse_vless_invalid_prefix(self):
        """Test parsing link without vless:// prefix."""
        server = ServerParser.parse_vless("vmess://uuid@host:443")
        
        assert server is None


class TestServerParserTrojan:
    """Test trojan:// link parsing."""
    
    def test_parse_trojan_valid_link(self):
        """Test parsing valid trojan:// link."""
        link = "trojan://password123@example.com:443?type=ws&sni=example.com&path=/path#Test%20Server"
        server = ServerParser.parse_trojan(link)
        
        assert server is not None
        assert server["name"] == "Test Server"
        assert server["type"] == "trojan"
        assert server["ip"] == "example.com"
        assert server["port"] == 443
        assert server["uuid"] == "password123"
        assert server["security"] == "tls"
        assert server["tls"] is True
    
    def test_parse_trojan_without_params(self):
        """Test parsing trojan:// link without query parameters."""
        link = "trojan://password123@example.com:443"
        server = ServerParser.parse_trojan(link)
        
        assert server is not None
        assert server["uuid"] == "password123"
        assert server["tls"] is True  # Trojan always uses TLS
    
    def test_parse_trojan_invalid_format(self):
        """Test parsing malformed trojan:// link."""
        server = ServerParser.parse_trojan("trojan://invalid")
        
        assert server is None
    
    def test_parse_trojan_invalid_prefix(self):
        """Test parsing link without trojan:// prefix."""
        server = ServerParser.parse_trojan("vmess://password@host:443")
        
        assert server is None


class TestServerParserDeduplication:
    """Test server deduplication logic."""
    
    def test_deduplicate_removes_exact_duplicates(self):
        """Test that exact duplicate servers are removed."""
        servers = [
            {"type": "vmess", "ip": "1.2.3.4", "port": 443, "uuid": "uuid1"},
            {"type": "vmess", "ip": "1.2.3.4", "port": 443, "uuid": "uuid1"},
        ]
        
        result = ServerParser.deduplicate_servers(servers)
        
        assert len(result) == 1
    
    def test_deduplicate_keeps_different_servers(self):
        """Test that different servers are kept."""
        servers = [
            {"type": "vmess", "ip": "1.2.3.4", "port": 443, "uuid": "uuid1"},
            {"type": "vmess", "ip": "5.6.7.8", "port": 443, "uuid": "uuid2"},
        ]
        
        result = ServerParser.deduplicate_servers(servers)
        
        assert len(result) == 2
    
    def test_deduplicate_different_ports(self):
        """Test that same IP with different ports are kept."""
        servers = [
            {"type": "vmess", "ip": "1.2.3.4", "port": 443, "uuid": "uuid1"},
            {"type": "vmess", "ip": "1.2.3.4", "port": 8443, "uuid": "uuid1"},
        ]
        
        result = ServerParser.deduplicate_servers(servers)
        
        assert len(result) == 2
    
    def test_deduplicate_different_protocols(self):
        """Test that same server with different protocols are kept."""
        servers = [
            {"type": "vmess", "ip": "1.2.3.4", "port": 443, "uuid": "uuid1"},
            {"type": "vless", "ip": "1.2.3.4", "port": 443, "uuid": "uuid1"},
        ]
        
        result = ServerParser.deduplicate_servers(servers)
        
        assert len(result) == 2
    
    def test_deduplicate_empty_list(self):
        """Test deduplication with empty list."""
        result = ServerParser.deduplicate_servers([])
        
        assert result == []
