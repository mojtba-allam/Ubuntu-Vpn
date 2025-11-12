#!/usr/bin/env python3
"""
Test IP Change with VPN Connection

Tests current IP and then connects to VPN to show IP change.
"""

import requests
import time
import subprocess
import socket
import sys
import os


def get_current_ip():
    """Get current public IP address"""
    try:
        print("🌍 Getting current IP address...")
        response = requests.get('https://ipinfo.io/json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'ip': data.get('ip', 'N/A'),
                'country': data.get('country', 'N/A'),
                'city': data.get('city', 'N/A'),
                'org': data.get('org', 'N/A'),
                'location': data.get('loc', 'N/A')
            }
    except Exception as e:
        print(f"❌ Failed to get IP: {e}")

    return None


def test_connectivity():
    """Test basic internet connectivity"""
    try:
        print("🔗 Testing internet connectivity...")
        # Test DNS resolution
        socket.gethostbyname('google.com')
        print("✅ DNS resolution working")

        # Test HTTP connection
        response = requests.get('http://httpbin.org/ip', timeout=5)
        if response.status_code == 200:
            print("✅ HTTP connectivity working")
            return True
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")

    return False


def test_proxy_connectivity(proxy_port=1081):
    """Test connectivity through proxy"""
    try:
        print(f"🔗 Testing connectivity through HTTP proxy (127.0.0.1:{proxy_port})...")

        proxies = {
            'http': f'http://127.0.0.1:{proxy_port}',
            'https': f'http://127.0.0.1:{proxy_port}'
        }

        response = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            proxy_ip = data.get('origin', 'N/A')
            print(f"✅ Proxy working! Proxy IP: {proxy_ip}")
            return proxy_ip
        else:
            print(f"❌ Proxy returned status: {response.status_code}")

    except Exception as e:
        print(f"❌ Proxy test failed: {e}")

    return None


def start_mock_vpn():
    """Start mock VPN server for testing"""
    print("🚀 Starting mock VPN server...")

    # Create mock script that pretends to be a VPN
    mock_script = '''#!/bin/bash
echo "Mock VPN Server Started"
echo "SOCKS5 proxy on 127.0.0.1:1080"
echo "HTTP proxy on 127.0.0.1:1081"

# Create simple HTTP proxy using netcat if available
if command -v nc >/dev/null 2>&1; then
    echo "Starting simple HTTP proxy on port 1081..."
    # This is a very basic proxy - just for testing
    while true; do
        echo -e "HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nMock VPN Response" | nc -l -p 1081
    done
else
    echo "Netcat not available, just keeping process alive..."
    while true; do sleep 1; done
fi
'''

    with open('/tmp/mock_vpn.sh', 'w') as f:
        f.write(mock_script)

    os.chmod('/tmp/mock_vpn.sh', 0o755)

    # Start mock VPN in background
    process = subprocess.Popen(['/tmp/mock_vpn.sh'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)

    print(f"✅ Mock VPN started with PID: {process.pid}")
    return process


def test_ip_change():
    """Test IP change before and after VPN connection"""
    print("🧪 Testing IP Change Detection")
    print("="*50)

    # Test initial connectivity
    if not test_connectivity():
        print("❌ Cannot proceed - no internet connectivity")
        return False

    # Get current IP
    current_ip = get_current_ip()
    if current_ip:
        print(f"📍 Current IP Information:")
        print(f"   IP: {current_ip['ip']}")
        print(f"   Country: {current_ip['country']}")
        print(f"   City: {current_ip['city']}")
        print(f"   Organization: {current_ip['org']}")
    else:
        print("❌ Could not get current IP")
        return False

    print()

    # Test Hysteria2 connection
    print("🔐 Testing Hysteria2 VPN Connection...")

    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        from hysteria2_manager import Hysteria2Manager

        # Hysteria2 configuration
        hysteria2_url = "hysteria2://YwuvGJk36B@81.168.83.89:2083?sni=kotlet.arshiacomplus.dpdns.org&obfs=salamander&obfs-password=khameniiko%40smad%40ret&insecure=1#%40Daily_Configs"

        # Create manager
        manager = Hysteria2Manager("~/.config/hysteria2-test")

        if not manager.hysteria_client:
            print("❌ Hysteria2 client not found")
            return False

        print(f"✅ Hysteria2 client: {manager.hysteria_client}")

        # Parse server config
        server_config = manager.parse_hysteria2_url(hysteria_url)
        print(f"✅ Server: {server_config['server']}:{server_config['port']}")

        # Connect to VPN
        print("🚀 Connecting to VPN...")
        success, error = manager.connect(server_config)

        if not success:
            print(f"❌ VPN connection failed: {error}")
            return False

        print("✅ VPN Connected!")

        # Wait for connection to establish
        print("⏳ Waiting 5 seconds for connection to stabilize...")
        time.sleep(5)

        # Test proxy connectivity
        proxy_ip = test_proxy_connectivity()

        if proxy_ip:
            print(f"\n🎉 IP Change Detection Results:")
            print(f"   Original IP: {current_ip['ip']}")
            print(f"   VPN Proxy IP: {proxy_ip}")

            if proxy_ip != current_ip['ip']:
                print("✅ SUCCESS: IP address changed through VPN!")
            else:
                print("⚠️  IP didn't change - might be mock VPN or proxy issues")
        else:
            print("⚠️  Could not test proxy connectivity")

        # Test IP through VPN manager
        vpn_ip_info = manager.get_public_ip()
        if vpn_ip_info:
            print(f"\n🌍 VPN IP Information:")
            print(f"   IP: {vpn_ip_info.get('ip', 'N/A')}")
            print(f"   Country: {vpn_ip_info.get('country', 'N/A')}")
            print(f"   City: {vpn_ip_info.get('city', 'N/A')}")

            if vpn_ip_info.get('ip') != current_ip['ip']:
                print("✅ SUCCESS: VPN detected different IP!")
            else:
                print("⚠️  Same IP detected - might be mock VPN")

        # Cleanup
        print("\n🧹 Disconnecting VPN...")
        manager.disconnect()
        print("✅ VPN disconnected")

        return True

    except Exception as e:
        print(f"❌ VPN test failed: {e}")
        return False


if __name__ == "__main__":
    test_ip_change()