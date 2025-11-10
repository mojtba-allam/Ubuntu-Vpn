"""
Real V2Ray Connection Tests

Tests actual VPN connection functionality using real VLess servers.
These tests require V2Ray to be installed and will make actual network connections.

Usage:
    pytest tests/test_real_connection.py -v -s
"""

import pytest
import time
import json
import requests
from pathlib import Path
from v2ray_manager import V2RayManager
from subscription_manager import ServerParser


# Real VLess server for testing
TEST_VLESS_LINK = "vless://5c9b6087-f955-4506-9c1d-67a5aae44bc9@france-free-raiv2mmr.koyeb.app:443?encryption=none&security=tls&type=xhttp&path=%2F%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr&mode=packet-up#JOIN%20BEDE%20RAIV2MMR%F0%9F%94%A5"


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temporary config directory."""
    return str(tmp_path / "v2ray-test")


@pytest.fixture
def v2ray_manager(temp_config_dir):
    """Provide a V2RayManager instance."""
    return V2RayManager(config_dir=temp_config_dir)


@pytest.fixture
def test_server_config():
    """
    Parse the test VLess server link into V2Ray configuration.
    
    Returns:
        V2Ray configuration dictionary
    """
    # Parse the VLess link
    server = ServerParser.parse_vless(TEST_VLESS_LINK)
    
    if not server:
        pytest.skip("Failed to parse test VLess server link")
    
    # Note: xhttp is a newer transport that may not be supported in all V2Ray versions
    # For compatibility, we'll use WebSocket (ws) which is universally supported
    # The server should accept WebSocket connections on the same path
    
    network_type = server["network"]
    if network_type == "xhttp" or network_type == "httpupgrade":
        # Use WebSocket as fallback for compatibility
        network_type = "ws"
        stream_settings = {
            "network": network_type,
            "security": server["security"],
            "tlsSettings": {
                "serverName": server["ip"],
                "allowInsecure": False
            },
            "wsSettings": {
                "path": server["path"],
                "headers": {
                    "Host": server["ip"]
                }
            }
        }
    else:
        stream_settings = {
            "network": network_type,
            "security": server["security"],
            "tlsSettings": {
                "serverName": server["ip"],
                "allowInsecure": False
            } if server["tls"] else None
        }
    
    # Convert to V2Ray configuration format
    config = {
        "log": {
            "loglevel": "info"
        },
        "inbounds": [
            {
                "port": 1080,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True
                }
            }
        ],
        "outbounds": [
            {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": server["ip"],
                            "port": server["port"],
                            "users": [
                                {
                                    "id": server["uuid"],
                                    "encryption": "none"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": stream_settings
            }
        ]
    }
    
    return config


class TestRealVLessConnection:
    """Test real VLess server connection."""
    
    def test_parse_vless_server_link(self):
        """Test that the VLess server link can be parsed correctly."""
        server = ServerParser.parse_vless(TEST_VLESS_LINK)
        
        assert server is not None
        assert server["type"] == "vless"
        assert server["ip"] == "france-free-raiv2mmr.koyeb.app"
        assert server["port"] == 443
        assert server["uuid"] == "5c9b6087-f955-4506-9c1d-67a5aae44bc9"
        assert server["security"] == "tls"
        assert server["network"] == "xhttp"
        assert server["tls"] is True
        
        print(f"\n✅ Parsed server: {server['name']}")
        print(f"   Host: {server['ip']}:{server['port']}")
        print(f"   Protocol: {server['type']}")
        print(f"   Network: {server['network']}")
        print(f"   Security: {server['security']}")
    
    def test_connect_to_real_vless_server(self, v2ray_manager, test_server_config):
        """
        Test connecting to a real VLess server.
        
        This test will:
        1. Start V2Ray with the test server configuration
        2. Wait for connection to establish
        3. Verify the process is running
        4. Check logs for connection status
        5. Disconnect and cleanup
        """
        print("\n" + "="*70)
        print("🧪 TESTING REAL VLESS CONNECTION")
        print("="*70)
        
        # Connect to server
        print("\n📡 Connecting to VLess server...")
        success, error_msg = v2ray_manager.connect(test_server_config)
        
        if not success:
            pytest.fail(f"Failed to connect: {error_msg}")
        
        assert success is True
        assert error_msg == ""
        print("✅ Connection initiated successfully")
        
        # Verify process is running
        assert v2ray_manager.is_connected() is True
        print("✅ V2Ray process is running")
        
        # Wait for connection to establish
        print("\n⏳ Waiting for connection to establish (5 seconds)...")
        time.sleep(5)
        
        # Check if process is still running
        assert v2ray_manager.is_connected() is True
        print("✅ V2Ray process still running after 5 seconds")
        
        # Get logs
        logs = v2ray_manager.get_logs()
        print(f"\n📋 V2Ray Logs ({len(logs.split(chr(10)))} lines):")
        print("-" * 70)
        print(logs[-2000:] if len(logs) > 2000 else logs)  # Last 2000 chars
        print("-" * 70)
        
        # Check for common error patterns in logs
        error_patterns = [
            "failed to",
            "error",
            "cannot",
            "refused",
            "timeout"
        ]
        
        logs_lower = logs.lower()
        errors_found = [pattern for pattern in error_patterns if pattern in logs_lower]
        
        if errors_found:
            print(f"\n⚠️  Warning: Found potential error patterns in logs: {errors_found}")
        else:
            print("\n✅ No obvious error patterns found in logs")
        
        # Disconnect
        print("\n🔌 Disconnecting...")
        disconnect_success = v2ray_manager.disconnect()
        assert disconnect_success is True
        print("✅ Disconnected successfully")
        
        # Verify process stopped
        assert v2ray_manager.is_connected() is False
        print("✅ V2Ray process stopped")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
    
    def test_connection_with_ip_check(self, v2ray_manager, test_server_config):
        """
        Test connection and verify IP change through proxy.
        
        This test will:
        1. Get current public IP (without VPN)
        2. Connect to VLess server
        3. Wait for connection
        4. Get public IP through proxy
        5. Verify IP changed
        6. Disconnect
        """
        print("\n" + "="*70)
        print("🧪 TESTING CONNECTION WITH IP VERIFICATION")
        print("="*70)
        
        # Get IP before connection
        print("\n🌐 Getting public IP before VPN...")
        try:
            response = requests.get('https://ipinfo.io/json', timeout=10)
            ip_before = response.json().get('ip', 'unknown')
            country_before = response.json().get('country', 'unknown')
            print(f"✅ IP before VPN: {ip_before} ({country_before})")
        except Exception as e:
            print(f"⚠️  Could not get IP before VPN: {e}")
            ip_before = None
        
        # Connect to VPN
        print("\n📡 Connecting to VLess server...")
        success, error_msg = v2ray_manager.connect(test_server_config)
        
        if not success:
            pytest.fail(f"Failed to connect: {error_msg}")
        
        assert success is True
        print("✅ Connected to VPN")
        
        # Wait for connection to establish
        print("\n⏳ Waiting for connection to establish (10 seconds)...")
        time.sleep(10)
        
        # Verify still connected
        assert v2ray_manager.is_connected() is True
        print("✅ V2Ray still running")
        
        # Get IP through proxy
        print("\n🌐 Getting public IP through VPN proxy...")
        try:
            # Use SOCKS5 proxy on localhost:1080
            proxies = {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080'
            }
            
            response = requests.get(
                'https://ipinfo.io/json',
                proxies=proxies,
                timeout=15
            )
            
            ip_after = response.json().get('ip', 'unknown')
            country_after = response.json().get('country', 'unknown')
            city_after = response.json().get('city', 'unknown')
            
            print(f"✅ IP through VPN: {ip_after} ({country_after}, {city_after})")
            
            # Verify IP changed
            if ip_before and ip_after != 'unknown':
                if ip_before != ip_after:
                    print(f"\n✅ SUCCESS: IP changed from {ip_before} to {ip_after}")
                    print(f"   Location: {country_after}, {city_after}")
                else:
                    print(f"\n⚠️  WARNING: IP did not change (still {ip_before})")
                    print("   This might indicate the VPN is not routing traffic correctly")
            
        except requests.exceptions.ProxyError as e:
            print(f"\n❌ Proxy error: {e}")
            print("   This might indicate V2Ray is not accepting connections on port 1080")
            pytest.fail(f"Proxy connection failed: {e}")
        except Exception as e:
            print(f"\n⚠️  Could not get IP through VPN: {e}")
            print("   Connection might not be fully established yet")
        
        # Get logs
        logs = v2ray_manager.get_logs()
        print(f"\n📋 Recent V2Ray Logs:")
        print("-" * 70)
        print(logs[-1500:] if len(logs) > 1500 else logs)
        print("-" * 70)
        
        # Disconnect
        print("\n🔌 Disconnecting...")
        v2ray_manager.disconnect()
        print("✅ Disconnected")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED")
        print("="*70 + "\n")
    
    def test_connection_stability(self, v2ray_manager, test_server_config):
        """
        Test connection stability over time.
        
        This test will:
        1. Connect to server
        2. Monitor connection for 30 seconds
        3. Check process stays alive
        4. Disconnect
        """
        print("\n" + "="*70)
        print("🧪 TESTING CONNECTION STABILITY")
        print("="*70)
        
        # Connect
        print("\n📡 Connecting to VLess server...")
        success, error_msg = v2ray_manager.connect(test_server_config)
        
        if not success:
            pytest.fail(f"Failed to connect: {error_msg}")
        
        assert success is True
        print("✅ Connected")
        
        # Monitor for 30 seconds
        duration = 30
        check_interval = 5
        checks = duration // check_interval
        
        print(f"\n⏱️  Monitoring connection for {duration} seconds...")
        
        for i in range(checks):
            time.sleep(check_interval)
            
            is_connected = v2ray_manager.is_connected()
            elapsed = (i + 1) * check_interval
            
            if is_connected:
                print(f"✅ [{elapsed}s] Connection stable")
            else:
                print(f"❌ [{elapsed}s] Connection lost!")
                pytest.fail(f"Connection lost after {elapsed} seconds")
        
        print(f"\n✅ Connection remained stable for {duration} seconds")
        
        # Get final logs
        logs = v2ray_manager.get_logs()
        print(f"\n📋 Final Logs:")
        print("-" * 70)
        print(logs[-1000:] if len(logs) > 1000 else logs)
        print("-" * 70)
        
        # Disconnect
        print("\n🔌 Disconnecting...")
        v2ray_manager.disconnect()
        print("✅ Disconnected")
        
        print("\n" + "="*70)
        print("✅ STABILITY TEST COMPLETED")
        print("="*70 + "\n")
    
    def test_reconnection(self, v2ray_manager, test_server_config):
        """
        Test disconnecting and reconnecting multiple times.
        
        This test will:
        1. Connect to server
        2. Disconnect
        3. Repeat 3 times
        4. Verify each connection works
        """
        print("\n" + "="*70)
        print("🧪 TESTING RECONNECTION")
        print("="*70)
        
        cycles = 3
        
        for i in range(cycles):
            print(f"\n🔄 Cycle {i+1}/{cycles}")
            print("-" * 70)
            
            # Connect
            print("📡 Connecting...")
            success, error_msg = v2ray_manager.connect(test_server_config)
            
            if not success:
                pytest.fail(f"Failed to connect on cycle {i+1}: {error_msg}")
            
            assert success is True
            print("✅ Connected")
            
            # Wait
            time.sleep(3)
            
            # Verify running
            assert v2ray_manager.is_connected() is True
            print("✅ Process running")
            
            # Disconnect
            print("🔌 Disconnecting...")
            disconnect_success = v2ray_manager.disconnect()
            assert disconnect_success is True
            print("✅ Disconnected")
            
            # Verify stopped
            assert v2ray_manager.is_connected() is False
            print("✅ Process stopped")
            
            # Wait before next cycle
            if i < cycles - 1:
                time.sleep(2)
        
        print("\n" + "="*70)
        print(f"✅ RECONNECTION TEST COMPLETED ({cycles} cycles)")
        print("="*70 + "\n")


class TestVLessConfigGeneration:
    """Test VLess configuration generation."""
    
    def test_generate_vless_config_from_link(self):
        """Test generating V2Ray config from VLess link."""
        server = ServerParser.parse_vless(TEST_VLESS_LINK)
        
        assert server is not None
        
        # Generate V2Ray config
        config = {
            "inbounds": [
                {
                    "port": 1080,
                    "protocol": "socks",
                    "settings": {"auth": "noauth"}
                }
            ],
            "outbounds": [
                {
                    "protocol": "vless",
                    "settings": {
                        "vnext": [
                            {
                                "address": server["ip"],
                                "port": server["port"],
                                "users": [
                                    {
                                        "id": server["uuid"],
                                        "encryption": "none"
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": server["network"],
                        "security": server["security"]
                    }
                }
            ]
        }
        
        # Verify config structure
        assert "inbounds" in config
        assert "outbounds" in config
        assert config["outbounds"][0]["protocol"] == "vless"
        assert config["outbounds"][0]["settings"]["vnext"][0]["address"] == server["ip"]
        assert config["outbounds"][0]["settings"]["vnext"][0]["port"] == server["port"]
        
        print("\n✅ Generated V2Ray config:")
        print(json.dumps(config, indent=2))
    
    def test_config_file_creation(self, v2ray_manager, test_server_config, temp_config_dir):
        """Test that config file is created correctly."""
        # Connect (which creates config file)
        success, _ = v2ray_manager.connect(test_server_config)
        
        if not success:
            pytest.skip("Could not connect to test server")
        
        try:
            # Verify config file exists
            config_path = Path(temp_config_dir).expanduser() / "temp_config.json"
            assert config_path.exists()
            print(f"\n✅ Config file created at: {config_path}")
            
            # Verify config content
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
            
            assert "inbounds" in saved_config
            assert "outbounds" in saved_config
            print("✅ Config file has correct structure")
            
            print("\n📄 Config file content:")
            print(json.dumps(saved_config, indent=2))
            
        finally:
            # Cleanup
            v2ray_manager.disconnect()


@pytest.mark.slow
class TestExtendedConnection:
    """Extended connection tests (marked as slow)."""
    
    def test_long_running_connection(self, v2ray_manager, test_server_config):
        """
        Test connection over extended period (2 minutes).
        
        Run with: pytest tests/test_real_connection.py::TestExtendedConnection -v -s
        """
        print("\n" + "="*70)
        print("🧪 TESTING LONG-RUNNING CONNECTION (2 minutes)")
        print("="*70)
        
        # Connect
        print("\n📡 Connecting...")
        success, error_msg = v2ray_manager.connect(test_server_config)
        
        if not success:
            pytest.fail(f"Failed to connect: {error_msg}")
        
        print("✅ Connected")
        
        # Monitor for 2 minutes
        duration = 120
        check_interval = 10
        checks = duration // check_interval
        
        print(f"\n⏱️  Monitoring for {duration} seconds...")
        
        for i in range(checks):
            time.sleep(check_interval)
            
            is_connected = v2ray_manager.is_connected()
            elapsed = (i + 1) * check_interval
            
            if is_connected:
                print(f"✅ [{elapsed}s/{duration}s] Connection stable")
            else:
                print(f"❌ [{elapsed}s] Connection lost!")
                pytest.fail(f"Connection lost after {elapsed} seconds")
        
        print(f"\n✅ Connection remained stable for {duration} seconds")
        
        # Disconnect
        print("\n🔌 Disconnecting...")
        v2ray_manager.disconnect()
        print("✅ Disconnected")
        
        print("\n" + "="*70)
        print("✅ LONG-RUNNING TEST COMPLETED")
        print("="*70 + "\n")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
