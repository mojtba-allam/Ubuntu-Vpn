#!/usr/bin/env python3
"""
Test Hysteria2 Connection Script

Tests Hysteria2 connection with the provided server configuration.
"""

import sys
import os

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hysteria2_manager import Hysteria2Manager
import time


def test_hysteria2_connection():
    """Test Hysteria2 connection with the provided server"""

    print("🔧 Testing Hysteria2 Connection")
    print("="*50)

    # Hysteria2 server URL provided by user
    hysteria2_url = "hysteria2://YwuvGJk36B@81.168.83.89:2083?sni=kotlet.arshiacomplus.dpdns.org&obfs=salamander&obfs-password=khameniiko%40smad%40ret&insecure=1#%40Daily_Configs"

    # Create Hysteria2 manager
    config_dir = "~/.config/hysteria2-test"
    manager = Hysteria2Manager(config_dir)

    # Check if Hysteria2 client is available
    if not manager.hysteria_client:
        print("❌ Hysteria2 client not found!")
        print("   Please install Hysteria2 client:")
        print("   - Download from: https://github.com/apernet/hysteria/releases")
        print("   - Or use: go install github.com/apernet/hysteria/cmd/hysteria@latest")
        return False

    print(f"✅ Hysteria2 client found: {manager.hysteria_client}")

    # Parse the Hysteria2 URL
    try:
        server_config = manager.parse_hysteria2_url(hysteria2_url)
        print("\n📋 Server Configuration:")
        print(f"   Name: {server_config['name']}")
        print(f"   Server: {server_config['server']}:{server_config['port']}")
        print(f"   Password: {server_config['password']}")
        print(f"   SNI: {server_config['sni']}")
        print(f"   Obfuscation: {server_config['obfs']}")
        print(f"   Insecure: {server_config['insecure']}")
    except Exception as e:
        print(f"❌ Failed to parse Hysteria2 URL: {e}")
        return False

    # Test connection
    print("\n🚀 Connecting to Hysteria2 server...")
    success, error_message = manager.connect(server_config)

    if not success:
        print(f"❌ Connection failed: {error_message}")
        return False

    print("✅ Connected successfully!")

    # Wait for connection to establish
    print("⏳ Waiting 5 seconds for connection to stabilize...")
    time.sleep(5)

    # Test IP change
    print("\n🌍 Testing IP change detection...")
    ip_info = manager.get_public_ip()

    if ip_info:
        print("✅ IP information retrieved through Hysteria2!")
        print(f"   IP: {ip_info.get('ip', 'N/A')}")
        print(f"   Country: {ip_info.get('country', 'N/A')}")
        print(f"   City: {ip_info.get('city', 'N/A')}")
        print(f"   Organization: {ip_info.get('org', 'N/A')}")

        # Test connectivity through VPN
        print("\n🔗 Testing connectivity through Hysteria2...")
        try:
            import requests
            proxies = {
                'http': 'http://127.0.0.1:1081',
                'https': 'http://127.0.0.1:1081'
            }

            # Test HTTP request through proxy
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                proxy_ip = data.get('origin', 'N/A')
                print(f"✅ HTTP request through Hysteria2 successful!")
                print(f"   Proxy IP: {proxy_ip}")

                if proxy_ip != ip_info.get('ip'):
                    print("⚠️  IP addresses differ - this could be normal for some VPN providers")
                else:
                    print("✅ IP addresses match - connection is working correctly!")
            else:
                print(f"⚠️  HTTP request returned status: {response.status_code}")

        except Exception as e:
            print(f"⚠️  HTTP test failed: {e}")
            print("   This might be normal - the connection could still be working")

    else:
        print("⚠️  Could not retrieve IP information")
        print("   The connection might be working but IP detection failed")

    # Show connection logs
    print("\n📝 Connection Logs:")
    print("-" * 30)
    logs = manager.get_logs()
    if logs:
        print(logs[-500:])  # Show last 500 characters
    else:
        print("No logs available")

    # Cleanup
    print("\n🧹 Cleaning up...")
    manager.disconnect()
    print("✅ Disconnected")

    return True


def test_basic_functionality():
    """Test basic functionality without connecting"""
    print("🔧 Testing Hysteria2 Manager Basic Functionality")
    print("="*50)

    # Create Hysteria2 manager
    config_dir = "~/.config/hysteria2-test"
    manager = Hysteria2Manager(config_dir)

    print(f"Config directory: {os.path.expanduser(config_dir)}")
    print(f"Hysteria2 client: {manager.hysteria_client or 'Not found'}")

    # Test URL parsing
    hysteria2_url = "hysteria2://YwuvGJk36B@81.168.83.89:2083?sni=kotlet.arshiacomplus.dpdns.org&obfs=salamander&obfs-password=khameniiko%40smad%40ret&insecure=1#%40Daily_Configs"

    try:
        config = manager.parse_hysteria2_url(hysteria2_url)
        print("\n✅ URL parsing successful:")
        for key, value in config.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ URL parsing failed: {e}")
        return False

    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--basic":
        test_basic_functionality()
    else:
        test_hysteria2_connection()