# Real Connection Tests

This directory contains tests for real V2Ray VPN connections using actual VLess servers.

## Prerequisites

1. **V2Ray Core** must be installed:
   ```bash
   bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
   ```

2. **Python dependencies** must be installed:
   ```bash
   ./venv/bin/pip install -r requirements.txt
   ```

3. **PySocks** is required for proxy testing:
   ```bash
   ./venv/bin/pip install PySocks
   ```

## Running Tests

### Using the Helper Script (Recommended)

The easiest way to run the tests is using the provided helper script:

```bash
# Run quick tests (default, excludes slow tests)
./test_connection.sh

# Run all tests including slow ones
./test_connection.sh all

# Run specific test types
./test_connection.sh basic      # Basic connection test only
./test_connection.sh ip         # IP verification test only
./test_connection.sh stability  # 30-second stability test
./test_connection.sh long       # 2-minute long-running test
```

### Using pytest Directly

You can also run tests directly with pytest:

```bash
# Run all connection tests
./venv/bin/pytest tests/test_real_connection.py -v -s

# Run specific test
./venv/bin/pytest tests/test_real_connection.py::TestRealVLessConnection::test_connect_to_real_vless_server -v -s

# Run with markers
./venv/bin/pytest tests/test_real_connection.py -m "not slow" -v -s
```

## Test Descriptions

### TestRealVLessConnection

#### test_parse_vless_server_link
- Verifies the VLess server link can be parsed correctly
- Checks all server parameters (host, port, UUID, security, etc.)
- **Duration:** < 1 second

#### test_connect_to_real_vless_server
- Connects to the real VLess server
- Verifies V2Ray process starts and stays running
- Checks logs for errors
- **Duration:** ~10 seconds

#### test_connection_with_ip_check
- Gets public IP before VPN connection
- Connects to VLess server
- Gets public IP through SOCKS proxy
- Verifies IP changed (confirms VPN is working)
- **Duration:** ~20 seconds
- **Requires:** PySocks library

#### test_connection_stability
- Connects to server
- Monitors connection for 30 seconds
- Checks process stays alive throughout
- **Duration:** ~30 seconds

#### test_reconnection
- Tests connecting and disconnecting 3 times
- Verifies each cycle works correctly
- **Duration:** ~20 seconds

### TestVLessConfigGeneration

#### test_generate_vless_config_from_link
- Tests V2Ray configuration generation from VLess link
- Verifies config structure is correct
- **Duration:** < 1 second

#### test_config_file_creation
- Tests that config file is created correctly
- Verifies file content matches expected format
- **Duration:** ~5 seconds

### TestExtendedConnection (marked as slow)

#### test_long_running_connection
- Tests connection stability over 2 minutes
- Monitors process every 10 seconds
- **Duration:** 2 minutes
- **Marker:** `@pytest.mark.slow`

## Test Server

The tests use a real VLess server:

```
vless://5c9b6087-f955-4506-9c1d-67a5aae44bc9@france-free-raiv2mmr.koyeb.app:443
```

**Server Details:**
- Host: france-free-raiv2mmr.koyeb.app
- Port: 443
- Protocol: VLess
- Network: xhttp
- Security: TLS
- Encryption: none

## Understanding Test Output

### Successful Connection
```
🚀 CONNECTING TO V2RAY SERVER
📝 Saving config to: /tmp/v2ray-test/temp_config.json
✅ Config saved successfully
✅ V2Ray binary found at: /usr/local/bin/v2ray
🔄 Starting V2Ray process...
✅ Process started with PID: 12345
✅ Log streaming started
⏳ Waiting for V2Ray to initialize...
✅ V2Ray is running successfully!
```

### Connection Failure
```
❌ ERROR: V2Ray process terminated unexpectedly.
[error logs will be shown here]
```

### IP Verification Success
```
✅ IP before VPN: 203.0.113.42 (US)
✅ IP through VPN: 198.51.100.10 (FR, Paris)
✅ SUCCESS: IP changed from 203.0.113.42 to 198.51.100.10
```

## Troubleshooting

### V2Ray Not Found
```
❌ V2Ray binary not found. Please install V2Ray first.
```
**Solution:** Install V2Ray using the official script:
```bash
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
```

### Process Terminates Immediately
**Possible causes:**
1. Invalid server configuration
2. Server is offline or unreachable
3. Firewall blocking connection
4. V2Ray version incompatibility

**Solution:** Check V2Ray logs in test output for specific error messages.

### Proxy Connection Failed
```
❌ Proxy error: [Errno 111] Connection refused
```
**Possible causes:**
1. V2Ray not accepting connections on port 1080
2. SOCKS inbound not configured correctly
3. Process crashed after starting

**Solution:** 
- Check V2Ray logs for errors
- Verify inbound configuration in test output
- Ensure no other service is using port 1080

### IP Did Not Change
```
⚠️ WARNING: IP did not change (still 203.0.113.42)
```
**Possible causes:**
1. VPN connected but not routing traffic
2. DNS leaking
3. Application not using proxy correctly

**Solution:**
- Check V2Ray logs for routing issues
- Verify streamSettings in configuration
- Test with curl: `curl --socks5 127.0.0.1:1080 https://ipinfo.io`

### PySocks Not Found
```
ModuleNotFoundError: No module named 'socks'
```
**Solution:** Install PySocks:
```bash
./venv/bin/pip install PySocks
```

## Manual Testing

You can also test the connection manually:

```bash
# Start V2Ray with test config
v2ray -config /path/to/temp_config.json

# In another terminal, test with curl
curl --socks5 127.0.0.1:1080 https://ipinfo.io

# Should show French IP if VPN is working
```

## Notes

- Tests create temporary config files in `/tmp/v2ray-test/`
- All tests clean up after themselves (disconnect, remove config files)
- Tests are designed to be run in CI/CD environments
- Some tests may fail if the test server is offline or overloaded
- Network latency may affect test timing

## Adding New Test Servers

To test with a different server, update the `TEST_VLESS_LINK` constant in `test_real_connection.py`:

```python
TEST_VLESS_LINK = "vless://your-uuid@your-server:port?params#name"
```

The parser supports:
- VMess: `vmess://base64-encoded-json`
- VLess: `vless://uuid@host:port?params#name`
- Trojan: `trojan://password@host:port?params#name`
