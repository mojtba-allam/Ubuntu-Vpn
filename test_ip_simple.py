#!/usr/bin/env python3
"""
Simple IP Change Test
"""

import requests
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🌍 Simple IP Test")
    print("="*30)

    # Get current IP
    try:
        response = requests.get('https://ipinfo.io/json', timeout=10)
        current_data = response.json()
        current_ip = current_data.get('ip', 'N/A')
        print(f"Current IP: {current_ip}")
        print(f"Location: {current_data.get('city', 'N/A')}, {current_data.get('country', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to get current IP: {e}")
        return

    # Test Hysteria2
    print("\n🔐 Testing Hysteria2...")
    try:
        from hysteria2_manager import Hysteria2Manager

        hysteria2_url = "hysteria2://YwuvGJk36B@81.168.83.89:2083?sni=kotlet.arshiacomplus.dpdns.org&obfs=salamander&obfs-password=khameniiko%40smad%40ret&insecure=1#%40Daily_Configs"

        print(f"URL: {hysteria2_url[:50]}...")

        manager = Hysteria2Manager("~/.config/test")
        server_config = manager.parse_hysteria2_url(hysteria2_url)

        print(f"✅ Server: {server_config['server']}:{server_config['port']}")
        print(f"✅ Type: {server_config['type']}")
        print(f"✅ Hysteria2 configuration parsed successfully")

    except Exception as e:
        print(f"❌ Hysteria2 test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()