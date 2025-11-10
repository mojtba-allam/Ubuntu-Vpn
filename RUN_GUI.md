# Running the V2Ray Client GUI

## Quick Start - See the GUI Window

### Method 1: Run the Application (Recommended)

```bash
./run.sh
```

This will:
1. ✅ Check dependencies
2. ✅ Launch the GUI window
3. ✅ Show server cards with Connect buttons
4. ✅ Display the Servers, Settings, and Logs tabs

### Method 2: Test GUI Launch

```bash
./venv/bin/python test_gui_launch.py
```

This will:
- Launch the GUI
- Show diagnostic information
- Display server count
- Keep window open for testing

### Method 3: Direct Python

```bash
./venv/bin/python main.py
```

## What You Should See

### 1. Main Window

The application window will open with:
- **Title**: "V2Ray Client"
- **Size**: 1000x700 pixels
- **Three tabs**: Servers, Settings, Logs

### 2. Servers Tab (Default View)

You should see:

```
┌─────────────────────────────────────────────────────────┐
│  🔍 Search servers...    [⬇️ Sort by Ping]  [🔄 Refresh] │
├─────────────────────────────────────────────────────────┤
│  Status: Disconnected                                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐                               │
│  │ 🔥 JOIN BEDE RAIV2MMR│                               │
│  │ france-free-raiv...  │                               │
│  │ Port: 443            │                               │
│  │ Network: xhttp→ws    │                               │
│  │ [    Connect    ]    │  ← Click this button!        │
│  └──────────────────────┘                               │
└─────────────────────────────────────────────────────────┘
```

### 3. Server Card Details

Each server card shows:
- 🔥 **Server Name**: JOIN BEDE RAIV2MMR🔥
- 🌐 **Address**: france-free-raiv2mmr.koyeb.app
- 🔌 **Port**: 443
- 📡 **Network**: xhttp (converted to ws)
- 🔒 **Security**: TLS
- 🟢 **Connect Button**: Click to connect!

## How to Connect

1. **Click the "Connect" button** on any server card
2. You'll see a toast notification: "Connecting to..."
3. Wait 2-3 seconds for connection
4. Status bar will turn green: "Status: Connected to..."
5. Your IP address will be displayed

## If You Don't See Servers

### Check 1: Manual Servers File

```bash
cat ~/.config/v2ray-client/manual_servers.json
```

Should show the test server. If empty or missing:

```bash
# Create manual servers file
cat > ~/.config/v2ray-client/manual_servers.json << 'EOF'
[
  {
    "name": "JOIN BEDE RAIV2MMR🔥",
    "type": "vless",
    "ip": "france-free-raiv2mmr.koyeb.app",
    "port": 443,
    "uuid": "5c9b6087-f955-4506-9c1d-67a5aae44bc9",
    "alterId": 0,
    "security": "tls",
    "network": "xhttp",
    "tls": true,
    "sni": "",
    "path": "/@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr-@Raiv2mmr",
    "ping": -1,
    "country_code": "FR"
  }
]
EOF
```

### Check 2: Click Refresh

In the GUI:
1. Click the **"🔄 Refresh"** button at the top
2. Wait 1-2 seconds
3. Server cards should appear

### Check 3: Add Subscription

If you want more servers:
1. Go to **Settings** tab
2. Click **"Add Subscription"**
3. Enter a subscription URL
4. Click **"Save"**
5. Go back to **Servers** tab
6. Click **"Refresh"**

## GUI Features

### Servers Tab

- **Search**: Filter servers by name, IP, or country
- **Sort**: Sort by ping or name
- **Refresh**: Reload server list
- **Connect**: Click on any server card
- **Status Bar**: Shows connection status and IP

### Settings Tab

- **Subscriptions**: Add/remove subscription URLs
- **Refresh Interval**: Set how often to update (5-60 seconds)
- **Theme**: Choose Dark, Light, or Neon
- **Auto-start**: Launch on system startup

### Logs Tab

- **Real-time logs**: See V2Ray output
- **Clear**: Remove all logs
- **Export**: Save logs to file
- **Auto-scroll**: Automatically scroll to latest

## Troubleshooting GUI Issues

### Window Doesn't Appear

```bash
# Check if running in graphical environment
echo $DISPLAY
# Should show something like :0 or :1

# If empty, you're not in a graphical session
# Use SSH with X11 forwarding:
ssh -X user@host
```

### Window Appears But No Servers

1. Check manual servers file exists
2. Click Refresh button
3. Check console output for errors
4. Go to Settings and add a subscription

### Connect Button Doesn't Work

1. Check V2Ray is installed: `v2ray version`
2. Look at Logs tab for error messages
3. Try a different server
4. Check the console output

### Theme Looks Wrong

1. Go to Settings tab
2. Try different themes:
   - Dark
   - Light
   - Neon (default)
3. Theme applies immediately

## Console Output

When you run the app, you'll see:

```
============================================================
🚀 V2RAY CLIENT FOR UBUNTU
   Version: 1.0.0
============================================================

📁 Config directory: /home/user/.config/v2ray-client
🎨 Initializing Qt application...

⚙️  Generating V2Ray config for VLESS server
   Server: JOIN BEDE RAIV2MMR🔥
   Address: france-free-raiv2mmr.koyeb.app:443
   Network: xhttp
   TLS: True
   ⚠️  Converting xhttp to ws (WebSocket) for compatibility
✅ Config generated successfully
```

This is normal! The xhttp → ws conversion is automatic.

## Screenshots (What to Expect)

### Disconnected State
- Status bar: Red/Purple gradient
- Text: "Status: Disconnected"
- Server cards: Blue "Connect" buttons

### Connected State
- Status bar: Green gradient with border
- Text: "Status: Connected to [server name]"
- IP displayed: "IP: x.x.x.x (City, Country)"
- Connected server card: Green "Disconnect" button

## Next Steps

Once the GUI is running:

1. ✅ **Connect to server** - Click Connect button
2. ✅ **Check IP** - Verify your IP changed
3. ✅ **View logs** - Go to Logs tab
4. ✅ **Add more servers** - Go to Settings tab
5. ✅ **Customize theme** - Choose your favorite

## Need Help?

If the GUI still doesn't show properly:

1. Run the test script:
   ```bash
   ./venv/bin/python test_gui_launch.py
   ```

2. Check the output for errors

3. Make sure you're in a graphical environment:
   ```bash
   echo $DISPLAY
   ```

4. Try running with verbose output:
   ```bash
   QT_DEBUG_PLUGINS=1 ./venv/bin/python main.py
   ```

---

**The GUI should now be working! Enjoy your V2Ray client! 🚀**
