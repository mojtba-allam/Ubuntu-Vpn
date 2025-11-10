# ✅ Port Configuration Updated!

## What Changed

The V2Ray client now uses **different ports** to avoid conflicts with v2rayN:

### Old Ports (Conflicted with v2rayN)
- ❌ SOCKS5: 10808 (same as v2rayN)
- ❌ HTTP: 10809 (same as v2rayN)

### New Ports (No Conflict!)
- ✅ SOCKS5: **1080**
- ✅ HTTP: **1081**

## Why This Matters

### Before (Port Conflict)
```
v2rayN:        127.0.0.1:10808 (SOCKS5)
V2Ray Client:  127.0.0.1:10808 (SOCKS5) ← CONFLICT!
```
Result: V2Ray process crashed immediately

### After (No Conflict)
```
v2rayN:        127.0.0.1:10808 (SOCKS5) ← Your existing VPN
V2Ray Client:  127.0.0.1:1080  (SOCKS5) ← New client
```
Result: Both can run together!

## Proxy Chain Configuration

### With v2rayN Running (Recommended for Iran)

```
Browser → V2Ray Client (1080) → v2rayN (10808) → V2Ray Server → Internet
```

**Your setup:**
- v2rayN provides initial VPN connection
- V2Ray client routes through v2rayN
- Double encryption layer

### Without v2rayN (Direct Connection)

```
Browser → V2Ray Client (1080) → V2Ray Server → Internet
```

**Direct connection:**
- No system proxy needed
- Single VPN connection
- May not work in Iran without initial VPN

## How to Use

### Option 1: With v2rayN (For Iran)

1. **Keep v2rayN running** (your current VPN)
2. **Run V2Ray client:**
   ```bash
   ./run.sh
   ```
3. **Configure browser** to use:
   - SOCKS5: `127.0.0.1:1080`
   - HTTP: `127.0.0.1:1081`

### Option 2: Without v2rayN (Direct)

1. **Stop v2rayN**
2. **Run V2Ray client:**
   ```bash
   ./run.sh
   ```
3. **Configure browser** to use:
   - SOCKS5: `127.0.0.1:1080`
   - HTTP: `127.0.0.1:1081`

## Browser Configuration

### Update Your Browser Settings

Since the ports changed, update your browser:

#### Chrome with SwitchyOmega
1. Open SwitchyOmega options
2. Edit V2Ray profile
3. Change port from **10808** to **1080**
4. Save

#### Firefox Manual Proxy
1. Settings → Network Settings
2. SOCKS Host: `127.0.0.1`
3. Port: **1080** (changed from 10808)
4. Save

#### Launch Chrome Script
```bash
# Updated script uses new port
./chrome_with_v2ray.sh
```

The script will automatically use port 1080.

## Testing

### Test V2Ray Client Proxy

```bash
# Test with new port
curl --socks5 127.0.0.1:1080 https://ipinfo.io/ip
```

Should show French IP if connected!

### Test v2rayN Proxy (Your Current VPN)

```bash
# Test v2rayN
curl --socks5 127.0.0.1:10808 https://ipinfo.io/ip
```

Should show your v2rayN server IP.

## Port Summary

| Service | SOCKS5 Port | HTTP Port | Purpose |
|---------|-------------|-----------|---------|
| **v2rayN** | 10808 | 10809 | Your existing VPN |
| **V2Ray Client** | **1080** | **1081** | New VPN client |

## Automatic Detection

The V2Ray client automatically:
1. ✅ Detects v2rayN on port 10808
2. ✅ Uses it as system proxy
3. ✅ Avoids port conflicts
4. ✅ Creates proxy chain

You'll see:
```
🔍 Detecting system proxy settings...
✅ Found GNOME SOCKS proxy: 127.0.0.1:10808
🔗 Configuring V2Ray to use system proxy
✅ System proxy configured in V2Ray chain
```

## Troubleshooting

### "Port already in use"

If you see this error:
```bash
# Check what's using port 1080
ss -tuln | grep 1080

# If something else is using it, stop that service
```

### "Connection refused" on port 1080

**Problem:** V2Ray client not running

**Solution:**
```bash
# Start the client
./run.sh
```

### Browser still using old port (10808)

**Problem:** Browser configured with old port

**Solution:**
1. Update browser proxy settings to port **1080**
2. Or use the launch script: `./chrome_with_v2ray.sh`

### v2rayN and V2Ray Client conflict

**Problem:** Both trying to use same port

**Solution:**
- This is now fixed! They use different ports
- v2rayN: 10808
- V2Ray Client: 1080

## Quick Reference

### For Iran Users (With v2rayN)

```bash
# 1. Keep v2rayN running (port 10808)
# 2. Run V2Ray client
./run.sh

# 3. Configure browser
# SOCKS5: 127.0.0.1:1080

# 4. Test
curl --socks5 127.0.0.1:1080 https://ipinfo.io
```

### For Direct Connection (Without v2rayN)

```bash
# 1. Stop v2rayN
# 2. Run V2Ray client
./run.sh

# 3. Configure browser
# SOCKS5: 127.0.0.1:1080

# 4. Test
curl --socks5 127.0.0.1:1080 https://ipinfo.io
```

## Summary

✅ **Port conflict fixed**  
✅ **V2Ray Client uses ports 1080/1081**  
✅ **v2rayN uses ports 10808/10809**  
✅ **Both can run together**  
✅ **Automatic proxy chain**  
✅ **No circular routing**  

**Now run the client and it should work!** 🎉

---

**Next step:** Run `./run.sh` and configure your browser to use port **1080**!
