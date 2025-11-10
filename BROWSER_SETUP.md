## ✅ V2Ray is Working! Now Configure Your Browser

Good news! Your V2Ray client is **successfully connected** to the server. The issue is that your browser doesn't know to use the proxy.

### 🎯 Quick Solution

**Run this command in a NEW terminal** (keep V2Ray running in the first terminal):

```bash
./chrome_with_v2ray.sh
```

This will launch Chrome configured to use your V2Ray proxy automatically!

---

## Understanding the Setup

### V2Ray Proxy Ports

Your V2Ray client creates two local proxies:

- **SOCKS5**: `127.0.0.1:10808` ← Use this one!
- **HTTP**: `127.0.0.1:10809`

These proxies forward your traffic through the V2Ray server in France.

### Why Browser Doesn't Work by Default

Browsers don't automatically use V2Ray. You need to configure them to use the proxy on `127.0.0.1:10808`.

---

## 🚀 Solution Methods

### Method 1: Auto-Launch Chrome (Easiest!)

```bash
# In a NEW terminal (keep V2Ray running):
./chrome_with_v2ray.sh
```

This script:
- ✅ Checks V2Ray is running
- ✅ Launches Chrome with proxy configured
- ✅ Routes all traffic through V2Ray
- ✅ Works immediately!

**Test it:**
1. Open https://ipinfo.io
2. You should see a French IP address!

### Method 2: Firefox Manual Proxy (Recommended for Iran)

Firefox is better for Iran because it has built-in proxy settings:

1. Open Firefox
2. Go to **Settings** (☰ menu → Settings)
3. Scroll to **Network Settings**
4. Click **Settings** button
5. Select **Manual proxy configuration**
6. Fill in:
   - **SOCKS Host**: `127.0.0.1`
   - **Port**: `10808`
   - Select **SOCKS v5**
   - ✅ Check **"Proxy DNS when using SOCKS v5"** (IMPORTANT!)
7. Click **OK**

**Test it:**
- Open https://ipinfo.io
- Should show French IP!

### Method 3: SwitchyOmega Extension (Best Long-term)

**For Chrome/Chromium:**

1. **Install Extension** (use your current VPN):
   - Go to Chrome Web Store
   - Search "Proxy SwitchyOmega"
   - Install it

2. **Configure**:
   - Click SwitchyOmega icon → Options
   - Click **New Profile** → Name it "V2Ray"
   - Select **Proxy Profile**
   - Configure:
     - Protocol: **SOCKS5**
     - Server: **127.0.0.1**
     - Port: **10808**
   - Click **Apply changes**

3. **Use**:
   - Click SwitchyOmega icon
   - Select "V2Ray" profile
   - Done!

**Advantages:**
- Easy to switch on/off
- Can set rules (auto-switch for certain sites)
- Works with regular Chrome

### Method 4: System-Wide Proxy (Ubuntu/GNOME)

```bash
# Enable system proxy
gsettings set org.gnome.system.proxy mode 'manual'
gsettings set org.gnome.system.proxy.socks host '127.0.0.1'
gsettings set org.gnome.system.proxy.socks port 10808

# To disable later:
gsettings set org.gnome.system.proxy mode 'none'
```

**Note:** This affects ALL applications, not just browser.

---

## 🧪 Test Your Connection

### Test 1: Command Line

```bash
./test_proxy.sh
```

Should show:
```
✅ V2Ray process is running
✅ SOCKS proxy listening on port 10808
✅ SOCKS5 proxy is working!
🎉 SUCCESS! You're connected through V2Ray!
   IP: [French IP]
   Country: FR
```

### Test 2: Manual curl Test

```bash
# Test with curl
curl --socks5 127.0.0.1:10808 https://ipinfo.io

# Should show French IP and location
```

### Test 3: Browser Test

1. Configure browser (use any method above)
2. Go to: https://ipinfo.io
3. Should show:
   - IP from France
   - Country: FR
   - City: Paris (or other French city)

---

## 📋 Complete Workflow

### Terminal 1: Run V2Ray Client

```bash
cd ~/GitHub_Projects/LV
./run.sh
```

Keep this running! You should see:
```
✅ Successfully connected to JOIN BEDE RAIV2MMR🔥
```

### Terminal 2: Launch Browser with Proxy

```bash
cd ~/GitHub_Projects/LV
./chrome_with_v2ray.sh
```

Or configure Firefox manually (see Method 2 above).

### Test Connection

Open https://ipinfo.io in the browser - should show French IP!

---

## 🔧 Troubleshooting

### "Connection refused" in browser

**Problem:** V2Ray not running or not listening on port 10808

**Solution:**
```bash
# Check if V2Ray is running
pgrep -x v2ray

# Check if port is listening
ss -tuln | grep 10808

# If not running, start V2Ray client:
./run.sh
```

### Browser still shows Iranian IP

**Problem:** Browser not using proxy

**Solutions:**
1. Make sure you configured proxy correctly
2. For Firefox: Check "Proxy DNS when using SOCKS v5"
3. Try the auto-launch script: `./chrome_with_v2ray.sh`
4. Clear browser cache and restart

### "Proxy server is refusing connections"

**Problem:** V2Ray disconnected or crashed

**Solution:**
```bash
# Check V2Ray status in GUI
# Or restart V2Ray:
# 1. Close V2Ray GUI
# 2. Run ./run.sh again
# 3. Click Connect in GUI
```

### Can't access any websites

**Problem:** V2Ray server might be blocked or slow

**Solutions:**
1. Check V2Ray logs in GUI (Logs tab)
2. Try disconnecting and reconnecting
3. Wait a few seconds for connection to stabilize
4. Test with: `curl --socks5 127.0.0.1:10808 https://google.com`

---

## 💡 Tips for Iran Users

### 1. Keep V2Ray Running

Don't close the V2Ray GUI window - minimize it instead.

### 2. Use Firefox

Firefox has better built-in proxy support than Chrome. Recommended for daily use.

### 3. Proxy DNS

Always enable "Proxy DNS" in Firefox to avoid DNS leaks.

### 4. Test Regularly

Periodically check https://ipinfo.io to make sure proxy is working.

### 5. Have Backup

Keep your current VPN as backup in case V2Ray server goes down.

### 6. Multiple Servers

Add more subscription URLs in Settings tab to have backup servers.

---

## 📱 Mobile/Other Devices

To use V2Ray on other devices on your network:

1. Find your computer's local IP:
   ```bash
   hostname -I | awk '{print $1}'
   ```

2. Configure device to use:
   - SOCKS5 proxy: `[your-computer-ip]:10808`
   - Example: `192.168.1.100:10808`

**Note:** Make sure firewall allows connections to port 10808.

---

## 🎉 Success Checklist

- [ ] V2Ray GUI running and connected
- [ ] Browser configured with proxy (127.0.0.1:10808)
- [ ] https://ipinfo.io shows French IP
- [ ] Can access blocked websites
- [ ] Can talk to Claude AI! 🤖

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│         V2Ray Proxy Settings            │
├─────────────────────────────────────────┤
│ Protocol:  SOCKS5                       │
│ Host:      127.0.0.1                    │
│ Port:      10808                        │
│                                         │
│ Alternative (HTTP):                     │
│ Host:      127.0.0.1                    │
│ Port:      10809                        │
└─────────────────────────────────────────┘

Commands:
  Start V2Ray:    ./run.sh
  Launch Chrome:  ./chrome_with_v2ray.sh
  Test Proxy:     ./test_proxy.sh
  Test with curl: curl --socks5 127.0.0.1:10808 https://ipinfo.io
```

---

**You're all set! Enjoy unrestricted internet access! 🚀🌍**
