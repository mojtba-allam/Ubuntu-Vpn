"""
Unit tests for V2RayManager class.
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from v2ray_manager import V2RayManager


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temporary config directory."""
    return str(tmp_path / "v2ray-test")


@pytest.fixture
def manager(temp_config_dir):
    """Provide a V2RayManager instance with temp directory."""
    return V2RayManager(config_dir=temp_config_dir)


@pytest.fixture
def sample_config():
    """Provide a sample server configuration."""
    return {
        "inbounds": [{"port": 1080, "protocol": "socks"}],
        "outbounds": [{
            "protocol": "vmess",
            "settings": {
                "vnext": [{
                    "address": "example.com",
                    "port": 443,
                    "users": [{"id": "test-uuid"}]
                }]
            }
        }]
    }


class TestV2RayManagerInit:
    """Test V2RayManager initialization."""
    
    def test_init_creates_config_directory(self, temp_config_dir):
        """Test that __init__ creates the config directory."""
        manager = V2RayManager(config_dir=temp_config_dir)
        
        assert manager.config_dir.exists()
        assert manager.config_dir.is_dir()
    
    def test_init_sets_temp_config_path(self, manager, temp_config_dir):
        """Test that __init__ sets the temp config path correctly."""
        expected_path = Path(temp_config_dir).expanduser() / "temp_config.json"
        assert manager.temp_config_path == expected_path
    
    def test_init_process_is_none(self, manager):
        """Test that process is None on initialization."""
        assert manager.process is None


class TestV2RayManagerConnect:
    """Test V2RayManager connect functionality."""
    
    @patch('subprocess.Popen')
    def test_connect_creates_config_file(self, mock_popen, manager, sample_config):
        """Test that connect() creates a config file."""
        # Mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process
        
        result = manager.connect(sample_config)
        
        assert result is True
        assert manager.temp_config_path.exists()
        
        # Verify config content
        with open(manager.temp_config_path, 'r') as f:
            saved_config = json.load(f)
        assert saved_config == sample_config
    
    @patch('subprocess.Popen')
    def test_connect_starts_process(self, mock_popen, manager, sample_config):
        """Test that connect() starts V2Ray process."""
        # Mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        result = manager.connect(sample_config)
        
        assert result is True
        mock_popen.assert_called_once()
        
        # Verify command arguments
        call_args = mock_popen.call_args
        assert 'v2ray' in call_args[0][0]
        assert '-config' in call_args[0][0]
    
    @patch('subprocess.Popen')
    def test_connect_returns_false_on_process_failure(self, mock_popen, manager, sample_config):
        """Test that connect() returns False if process fails to start."""
        # Mock process that exits immediately
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process exited
        mock_popen.return_value = mock_process
        
        result = manager.connect(sample_config)
        
        assert result is False
    
    @patch('subprocess.Popen')
    def test_connect_handles_v2ray_not_found(self, mock_popen, manager, sample_config):
        """Test that connect() handles V2Ray binary not found."""
        mock_popen.side_effect = FileNotFoundError()
        
        result = manager.connect(sample_config)
        
        assert result is False


class TestV2RayManagerDisconnect:
    """Test V2RayManager disconnect functionality."""
    
    @patch('subprocess.Popen')
    def test_disconnect_terminates_process(self, mock_popen, manager, sample_config):
        """Test that disconnect() terminates the V2Ray process."""
        # Mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        manager.connect(sample_config)
        result = manager.disconnect()
        
        assert result is True
        mock_process.terminate.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_disconnect_removes_config_file(self, mock_popen, manager, sample_config):
        """Test that disconnect() removes the temp config file."""
        # Mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        manager.connect(sample_config)
        assert manager.temp_config_path.exists()
        
        manager.disconnect()
        assert not manager.temp_config_path.exists()
    
    def test_disconnect_when_not_connected(self, manager):
        """Test that disconnect() works when not connected."""
        result = manager.disconnect()
        assert result is True


class TestV2RayManagerIsConnected:
    """Test V2RayManager is_connected functionality."""
    
    def test_is_connected_returns_false_when_no_process(self, manager):
        """Test that is_connected() returns False when no process."""
        assert manager.is_connected() is False
    
    @patch('subprocess.Popen')
    def test_is_connected_returns_true_when_running(self, mock_popen, manager, sample_config):
        """Test that is_connected() returns True when process is running."""
        # Mock running process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process
        
        manager.connect(sample_config)
        assert manager.is_connected() is True
    
    @patch('subprocess.Popen')
    def test_is_connected_returns_false_when_process_exited(self, mock_popen, manager, sample_config):
        """Test that is_connected() returns False when process has exited."""
        # Mock process that exits
        mock_process = MagicMock()
        # First call during connect check (returns None = running), 
        # second call in is_connected (returns 0 = exited)
        mock_process.poll.return_value = 0  # Process has exited
        mock_popen.return_value = mock_process
        
        # Manually set process to simulate it was connected
        manager.process = mock_process
        
        assert manager.is_connected() is False


class TestV2RayManagerPublicIP:
    """Test V2RayManager public IP functionality."""
    
    @patch('requests.get')
    def test_get_public_ip_returns_valid_data(self, mock_get, manager):
        """Test that get_public_ip() returns valid IP data."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ip': '1.2.3.4',
            'country': 'US',
            'city': 'New York'
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = manager.get_public_ip()
        
        assert result['ip'] == '1.2.3.4'
        assert result['country'] == 'US'
        assert result['city'] == 'New York'
    
    @patch('requests.get')
    def test_get_public_ip_handles_network_error(self, mock_get, manager):
        """Test that get_public_ip() handles network errors gracefully."""
        mock_get.side_effect = Exception("Network error")
        
        result = manager.get_public_ip()
        
        assert result == {}


class TestV2RayManagerLogs:
    """Test V2RayManager log functionality."""
    
    def test_get_logs_returns_empty_initially(self, manager):
        """Test that get_logs() returns empty string initially."""
        logs = manager.get_logs()
        assert logs == ''
    
    def test_stream_logs_sets_callback(self, manager):
        """Test that stream_logs() sets the callback."""
        callback = Mock()
        manager.stream_logs(callback)
        
        assert manager.log_callback == callback
    
    @patch('subprocess.Popen')
    def test_log_streaming_captures_output(self, mock_popen, manager, sample_config):
        """Test that log streaming captures process output."""
        # Mock process with output
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, None, 0]  # Running then exit
        mock_process.stdout.readline.side_effect = [
            "Log line 1\n",
            "Log line 2\n",
            ""
        ]
        mock_process.stderr.readline.return_value = ""
        mock_popen.return_value = mock_process
        
        callback = Mock()
        manager.stream_logs(callback)
        manager.connect(sample_config)
        
        # Give thread time to process
        time.sleep(0.2)
        
        # Check that logs were captured
        logs = manager.get_logs()
        assert "Log line 1" in logs or "Log line 2" in logs
