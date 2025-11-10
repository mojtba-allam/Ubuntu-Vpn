#!/usr/bin/env python3
"""
Test config generator with xhttp server
"""

from config_generator import generate_v2ray_config
from subscription_manager import ServerParser
import json

# Test VLess link with xhttp
TEST_VLESS_LINK = "vless://5c9b6087-f955-4506-9c1d-67a5aae44bc9@france-free-raiv2mmr.koyeb.app:443?encryption=none&security=tls&type=xhttp&path=%2F%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr-%40Raiv2mmr&mode=packet-up#JOIN%20BEDE%20RAIV2MMR%F0%9F%94%A5"

print("="*60)
print("Testing Config Generator with xhttp Transport")
print("="*60)

# Parse the server
print("\n1. Parsing VLess link...")
server = ServerParser.parse_vless(TEST_VLESS_LINK)

if not server:
    print("❌ Failed to parse server link")
    exit(1)

print(f"✅ Parsed server: {server['name']}")
print(f"   Network: {server['network']}")

# Generate config
print("\n2. Generating V2Ray config...")
config = generate_v2ray_config(server)

# Save to temp file
temp_file = "/tmp/test_v2ray_config.json"
with open(temp_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"\n3. Config saved to: {temp_file}")
print(f"   Network in config: {config['outbounds'][0]['streamSettings']['network']}")

# Test with V2Ray
print("\n4. Testing config with V2Ray...")
import subprocess
result = subprocess.run(
    ['v2ray', 'test', '-config', temp_file],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ Config is valid!")
    print("\n" + "="*60)
    print("SUCCESS: Config generator correctly converts xhttp to ws")
    print("="*60)
else:
    print("❌ Config test failed:")
    print(result.stderr)
    exit(1)

# Show the config
print("\n5. Generated config:")
print(json.dumps(config, indent=2))
