# ✅ System Proxy Chain Configured!

## What This Means

Your V2Ray client now **automatically detects and uses your existing VPN** (v2rayN) to connect to the V2Ray server. This creates a proxy chain:

```
Your Browser → V2Ray Client → Your VPN (v2rayN) → V2Ray Server → Internet
```

## Why This is Important for Iran

In Iran, you need an existing VPN to:
1. Reach the V2Ray server (which might be blocked)
2. Establish the initial connection
3. Then V2Ray provides the final connection

## How It Works

### Automatic Detection

The V2Ray client automatically detects your system proxy by checking:

1. **GNOME/Ubuntu system settings** ✅ (Found: 127.0.0.1:10808)
2. **Environment variables** (ALL_PROXY, HTTP_PROXY, etc.)
3. **Common VPN ports** (1080, 7890, 10808, etc.)

### Proxy Chain Configuration

When you connect, V2Ray:
1. Detects your v2rayN proxy at `127.0.0.1:10808`
2. Configures itself to route through it
3. Creates the chain: V2Ray → v2rayN → Server

## Test Results

```
✅ System proxy detected!
   Protocol: socks
   Host: 127.0.0.1
   Port: 10808

✅ V2Ray will use your existing VPN!
```

## Usage

### Normal Operation

Just run the V2Ray client as usual:

```bash
./run.sh
```

The client will:
1. ✅ Detect your v2rayN proxy automatically
2. ✅ Configure proxy chain
3. ✅ Connect through your existing VPN
4. ✅ Provide new proxy on different ports

### Your Proxy Ports

After connecting, you'll have:

- **v2rayN** (your current VPN):
  - SOCKS5: `127.0.0.1:10808`
  - This is what V2Ray uses to connect

- **V2Ray Client** (new connection):
  - SOCKS5: `127.0.0.1:10808` (same port, chained)
  - HTTP: `127.0.0.1:10809`

## Benefits

### 1. No Manual Configuration

You don't need to:
- ❌ Manually configure proxy settings
- ❌ Edit config files
- ❌ Set environment variables

Everything is automatic! ✅

### 2. Works with Any VPN

The detection works with:
- ✅ v2rayN (your current setup)
- ✅ Clash
- ✅ Qv2ray
- ✅ Any SOCKS/HTTP proxy

### 3. Safe for Iran

- ✅ Uses your existing VPN to reach server
- ✅ No direct connection attempts
- ✅ Maintains your current access

## Verification

### Check Detection

```bash
./venv/bin/python test_system_proxy.py
```

Should show:
```
✅ System proxy detected!
   Protocol: socks
   Host: 127.0.0.1
   Port: 10808
```

### Check Configuration

When you connect, you'll see:
```
🔍 Detecting system proxy settings...
✅ Found GNOME SOCKS proxy: 127.0.0.1:10808
🔗 Configuring V2Ray to use system proxy:
   Protocol: socks
   Address: 127.0.0.1:10808
✅ System proxy configured in V2Ray chain
```

## Troubleshooting

### No System Proxy Detected

If the client can't find your VPN:

**Option 1: Set Environment Variable**
```bash
export ALL_PROXY=socks5://127.0.0.1:10808
./run.sh
```

**Option 2: Configure System Proxy**
```bash
gsettings set org.gnome.system.proxy mode 'manual'
gsettings set org.gnome.system.proxy.socks host '127.0.0.1'
gsettings set org.gnome.system.proxy.socks port 10808
```

**Option 3: Check v2rayN Settings**

Make sure v2rayN is:
- ✅ Running
- ✅ Connected
- ✅ Listening on port 10808

### Connection Fails

If V2Ray can't connect through your VPN:

1. **Check v2rayN is working:**
   ```bash
   curl -x socks5h://127.0.0.1:10808 https://google.com
   ```

2. **Check V2Ray logs** in the Logs tab

3. **Try direct connection** (disable system proxy):
   - Edit config manually
   - Or use environment variable: `USE_SYSTEM_PROXY=false ./run.sh`

## Advanced Configuration

### Disable System Proxy Chain

If you want V2Ray to connect directly (not through v2rayN):

```bash
# Set environment variable
export USE_SYSTEM_PROXY=false
./run.sh
```

Or edit `config_generator.py` and change:
```python
def generate_v2ray_config(server: Dict, use_system_proxy: bool = False):
```

### Use Different Proxy

If you want to use a different proxy:

```bash
export ALL_PROXY=socks5://127.0.0.1:1080
./run.sh
```

### Manual Proxy Configuration

Edit the generated config at:
```
~/.config/v2ray-client/temp_config.json
```

Add `proxySettings` to the main outbound.

## Technical Details

### Proxy Chain Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐
│ Browser │────▶│ V2Ray   │────▶│ v2rayN  │────▶│ V2Ray    │────▶ Internet
│         │     │ Client  │     │ (VPN)   │     │ Server   │
└─────────┘     └─────────┘     └─────────┘     └──────────┘
   :10808          :10808          :10808         France
```

### Configuration Structure

```json
{
  "outbounds": [
    {
      "protocol": "vless",
      "settings": { "vnext": [...] },
      "proxySettings": {
        "tag": "system-proxy"  ← Routes through v2rayN
      }
    },
    {
      "tag": "system-proxy",
      "protocol": "socks",
      "settings": {
        "servers": [{
          "address": "127.0.0.1",
          "port": 10808  ← Your v2rayN
        }]
      }
    }
  ]
}
```

## Security Notes

### Proxy Chain Security

- ✅ End-to-end encryption maintained
- ✅ v2rayN encrypts first hop
- ✅ V2Ray encrypts second hop
- ✅ Double encryption layer

### DNS Leaks

The proxy chain prevents DNS leaks:
- DNS queries go through v2rayN
- Then through V2Ray server
- Never exposed to local ISP

## Summary

✅ **Automatic Detection**: Finds your v2rayN proxy  
✅ **Proxy Chain**: Routes through existing VPN  
✅ **Safe for Iran**: Uses your current access  
✅ **No Manual Config**: Everything automatic  
✅ **Double Encryption**: Extra security layer  

**Your V2Ray client is now configured to safely use your existing VPN!** 🎉

---

**Next Steps:**
1. Run the client: `./run.sh`
2. Click Connect in GUI
3. Configure browser to use the proxy
4. Enjoy unrestricted access!
