#!/usr/bin/env python3
"""
Test System Proxy Detection

Verifies that the system proxy detector can find your existing VPN.
"""

from system_proxy_detector import get_system_proxy, add_system_proxy_to_config
import json

print("="*60)
print("🧪 Testing System Proxy Detection")
print("="*60)

# Detect system proxy
proxy = get_system_proxy()

if proxy:
    print("\n✅ System proxy detected!")
    print(f"   Protocol: {proxy['protocol']}")
    print(f"   Host: {proxy['host']}")
    print(f"   Port: {proxy['port']}")
    
    # Create a sample V2Ray config
    sample_config = {
        "outbounds": [{
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": "example.com",
                    "port": 443
                }]
            }
        }]
    }
    
    # Add system proxy to config
    updated_config = add_system_proxy_to_config(sample_config, proxy)
    
    print("\n📄 Updated V2Ray Config:")
    print(json.dumps(updated_config, indent=2))
    
    print("\n" + "="*60)
    print("✅ SUCCESS: V2Ray will use your existing VPN!")
    print("="*60)
else:
    print("\n⚠️  No system proxy detected")
    print("\nThis means:")
    print("  1. No system-wide proxy is configured")
    print("  2. Your VPN might not be setting system proxy")
    print("  3. V2Ray will connect directly (might not work in Iran)")
    print("\nTo fix:")
    print("  1. Configure your VPN to use system proxy")
    print("  2. Or set environment variable:")
    print("     export ALL_PROXY=socks5://127.0.0.1:1080")
    print("="*60)
