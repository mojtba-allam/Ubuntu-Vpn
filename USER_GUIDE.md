# V2Ray Client - User Guide

Complete guide to using the V2Ray Client for Ubuntu.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Subscription Management](#subscription-management)
3. [Connecting to Servers](#connecting-to-servers)
4. [Settings Configuration](#settings-configuration)
5. [Monitoring and Logs](#monitoring-and-logs)
6. [Frequently Asked Questions](#frequently-asked-questions)

---

## Getting Started

### First Launch

When you first launch V2Ray Client, you'll see the main window with three tabs:

- **Servers**: Browse and connect to available servers
- **Settings**: Configure subscriptions and application preferences
- **Logs**: View real-time V2Ray connection logs

### Initial Setup

Before you can connect to any servers, you need to add at least one subscription URL:

1. Click on the **Settings** tab
2. Click the **Add Subscription** button
3. Enter your subscription URL
4. Optionally give it a name for easy identification
5. Click **OK**

The application will immediately fetch the server list from your subscription.

---

## Subscription Management

### What is a Subscription?

A subscription is a URL that provides a list of V2Ray server configurations. Subscription providers regularly update these lists with working servers.

### Adding a Subscription

**Step 1**: Navigate to Settings Tab
- Click on the **Settings** tab at the top of the window

**Step 2**: Click Add Subscription
- Click the **+ Add Subscription** button

**Step 3**: Enter Subscription Details
- **URL**: Paste your subscription URL (required)
- **Name**: Give it a memorable name (optional)

**Step 4**: Save
- Click **OK** to save the subscription
- The server list will update automatically

### Supported Subscription Formats

The application supports multiple subscription formats:

1. **Base64 Encoded (.v2ray)**
   - Most common format
   - Contains vmess://, vless://, or trojan:// links
   - Automatically decoded by the application

2. **Plain Text**
   - Direct list of server links
   - One link per line

3. **JSON Format**
   - Structured server configurations
   - Parsed automatically

4. **GitHub Raw URLs**
   - Direct links to subscription files on GitHub
   - Example: `https://raw.githubusercontent.com/user/repo/main/subscription.txt`

### Editing a Subscription

1. Go to the **Settings** tab
2. Find the subscription in the list
3. Click the **Edit** button next to it
4. Modify the URL or name
5. Click **OK** to save changes

### Removing a Subscription

1. Go to the **Settings** tab
2. Find the subscription you want to remove
3. Click the **X** button next to it
4. Confirm the removal when prompted

### Refreshing Subscriptions

**Automatic Refresh**:
- By default, subscriptions refresh every 10 seconds
- You can change this interval in Settings (minimum 5 seconds)

**Manual Refresh**:
- Go to the **Servers** tab
- Click the **🔁 Refresh** button
- All subscriptions will be fetched immediately

### Multiple Subscriptions

You can add multiple subscription URLs:
- Servers from all subscriptions are merged into one list
- Duplicate servers are automatically removed
- Each subscription can be managed independently

---

## Connecting to Servers

### Understanding Server Cards

Each server is displayed as a card showing:

- **Country Flag**: Visual identification of server location
- **Server Name**: Descriptive name (e.g., "USA-1", "Singapore-Fast")
- **IP Address**: Server IP and port
- **Ping Bar**: Visual latency indicator
  - Green bars: Low latency (good)
  - Yellow bars: Medium latency (acceptable)
  - Red bars: High latency (slow)
- **Ping Time**: Exact latency in milliseconds
- **Connect Button**: Click to establish connection

### Connecting to a Server

**Step 1**: Choose a Server
- Browse the server list in the **Servers** tab
- Look for servers with low ping (green bars)
- Consider server location based on your needs

**Step 2**: Click Connect
- Click the **Connect** button on your chosen server
- The button will show a loading animation

**Step 3**: Wait for Connection
- Connection typically takes 2-5 seconds
- Watch the status indicator change to "Connected"
- Your public IP address will be displayed

**Step 4**: Verify Connection
- Check that your IP address has changed
- The connected server card will be highlighted
- Status indicator shows green "Connected"

### Connection Process Details

When you connect to a server:

1. **Configuration Creation**
   - Server configuration is saved to a temporary file
   - Location: `~/.config/v2ray-client/temp_config.json`

2. **V2Ray Process Start**
   - V2Ray Core is launched with the configuration
   - Process runs in the background

3. **IP Verification**
   - Application fetches your public IP from ipinfo.io
   - Displays IP, country, and city information

4. **Status Update**
   - UI updates to show connected state
   - Logs begin streaming in the Logs tab

### Disconnecting from a Server

**Method 1**: From Server Card
- Click the **Disconnect** button on the connected server card

**Method 2**: From Status Bar
- Click the disconnect button in the application status bar

**What Happens on Disconnect**:
1. V2Ray process is terminated cleanly
2. Temporary configuration file is deleted
3. Status updates to "Disconnected"
4. IP information is cleared

### Server Sorting

Servers can be sorted by:

**By Ping** (Default):
- Fastest servers appear first
- Helps you choose the best performing server
- Updates automatically as pings are measured

**By Name**:
- Alphabetical order
- Useful for finding specific server locations
- Change in Settings tab

### Searching for Servers

Use the search bar at the top of the Servers tab:

1. Type server name, country, or IP
2. Server list filters in real-time
3. Clear search to show all servers

Examples:
- Search "USA" to find all US servers
- Search "Singapore" for Singapore servers
- Search "45.67" to find servers by IP

### Connection Tips

**For Best Performance**:
- Choose servers with ping < 100ms
- Prefer servers geographically closer to you
- Avoid servers with high load (very high ping)

**For Specific Regions**:
- Use search to filter by country
- Check multiple servers in the same region
- Some regions may have better routing

**Troubleshooting Connections**:
- If connection fails, try another server
- Check the Logs tab for error messages
- Verify V2Ray Core is installed: `v2ray --version`
- Ensure no firewall is blocking connections

---

## Settings Configuration

### Refresh Interval

Controls how often subscription URLs are fetched:

**Default**: 10 seconds

**Minimum**: 5 seconds

**Recommended**:
- 10-30 seconds for most users
- 60+ seconds if you have many subscriptions
- Lower values = more up-to-date servers
- Higher values = less network usage

**To Change**:
1. Go to **Settings** tab
2. Find "Refresh Interval" spinner
3. Adjust the value (in seconds)
4. Changes apply immediately

### Theme Selection

Choose your preferred visual appearance:

**Dark Theme**:
- Classic dark mode
- Easy on the eyes
- Good for low-light environments
- Professional appearance

**Light Theme**:
- Clean, bright interface
- Good for well-lit environments
- High contrast for readability

**Neon Theme**:
- Vibrant purple, blue, and cyan gradients
- Animated glow effects on hover
- Modern, eye-catching design
- Best for users who want visual flair

**To Change Theme**:
1. Go to **Settings** tab
2. Select your preferred theme radio button
3. Theme applies instantly
4. Your choice is saved for next launch

### Auto-Start on Login

Enable the application to launch automatically when you log in:

**To Enable**:
1. Go to **Settings** tab
2. Check the "Auto-start on login" checkbox
3. Application will launch on next login

**To Disable**:
1. Uncheck the "Auto-start on login" checkbox

**Note**: This creates a desktop entry in your autostart directory.

### Saving Settings

Settings are automatically saved when you:
- Change the refresh interval
- Select a different theme
- Toggle auto-start
- Add/remove subscriptions

Settings are stored in: `~/.config/v2ray-client/settings.json`

---

## Monitoring and Logs

### Logs Tab

The Logs tab displays real-time output from the V2Ray Core process.

**What You'll See**:
- Connection establishment messages
- Routing information
- Error messages (if any)
- Traffic statistics
- Protocol handshake details

**Log Levels**:
- `[Info]`: Normal operation messages
- `[Warning]`: Non-critical issues
- `[Error]`: Connection problems or failures

### Reading Logs

**Successful Connection**:
```
[Info] V2Ray started
[Info] Outbound connection established
[Info] TCP connection to server:port
```

**Connection Issues**:
```
[Error] Failed to connect to server
[Warning] Connection timeout
[Error] Invalid configuration
```

### Log Controls

**Auto-Scroll**:
- Logs automatically scroll to show newest entries
- Scroll up to read older logs (auto-scroll pauses)
- Scroll to bottom to resume auto-scroll

**Clear Logs**:
- Click **Clear Logs** button to empty the display
- Useful for focusing on new connection attempts
- Does not affect V2Ray operation

**Export Logs**:
1. Click **Export Logs** button
2. Choose save location in file dialog
3. Logs are saved as plain text file
4. Useful for troubleshooting or sharing with support

### Log Buffer Limit

- Maximum 10,000 lines retained in memory
- Oldest lines are removed when limit is reached
- Prevents excessive memory usage
- Export logs before they're removed if needed

### Using Logs for Troubleshooting

**Connection Fails**:
1. Open Logs tab
2. Click Connect on a server
3. Watch for error messages
4. Common errors:
   - "Connection refused": Server may be down
   - "Timeout": Network or firewall issue
   - "Invalid config": Server configuration problem

**Slow Connection**:
1. Check logs for routing messages
2. Look for repeated connection attempts
3. May indicate server overload

**No Internet After Connect**:
1. Check for "Outbound connection established" message
2. Verify routing rules are correct
3. Look for DNS resolution errors

---

## Frequently Asked Questions

### General Questions

**Q: What is V2Ray?**

A: V2Ray is a platform for building proxies to bypass network restrictions. It supports multiple protocols and provides flexible routing capabilities.

**Q: Is this application free?**

A: Yes, the application is open-source and free to use. However, you need subscription URLs from V2Ray service providers (which may be paid or free).

**Q: Which Ubuntu versions are supported?**

A: Ubuntu 20.04 and later versions are officially supported. It may work on older versions but is not tested.

**Q: Do I need root/sudo access?**

A: Only for initial installation. The application runs with normal user privileges.

### Subscription Questions

**Q: Where can I get subscription URLs?**

A: Subscription URLs are provided by V2Ray service providers. Search for "V2Ray subscription" or ask your VPN provider.

**Q: Can I use free subscriptions?**

A: Yes, but free subscriptions may have:
- Limited bandwidth
- Slower speeds
- Less reliable servers
- Fewer server locations

**Q: How many subscriptions can I add?**

A: There's no hard limit, but having too many (>10) may slow down refresh operations.

**Q: My subscription URL doesn't work**

A: Check that:
- URL is accessible in a web browser
- URL format is correct (starts with http:// or https://)
- Subscription provider is still active
- Your internet connection is working

**Q: What if servers from my subscription don't appear?**

A: Possible causes:
- Subscription format not supported
- URL returns empty content
- Network error during fetch
- Check Logs tab for error messages

### Connection Questions

**Q: Why can't I connect to any server?**

A: Common causes:
1. V2Ray Core not installed: Run `v2ray --version`
2. Firewall blocking connections: Check `sudo ufw status`
3. All servers are down: Try different subscription
4. Invalid server configurations: Check Logs tab

**Q: Connection succeeds but no internet access**

A: Try these steps:
1. Disconnect and reconnect
2. Try a different server
3. Check system proxy settings
4. Verify V2Ray is running: `ps aux | grep v2ray`
5. Check Logs tab for routing errors

**Q: How do I know if I'm connected?**

A: When connected:
- Status shows "Connected" with green indicator
- Your public IP is displayed
- Connected server card is highlighted
- Logs show active connection messages

**Q: Can I connect to multiple servers simultaneously?**

A: No, only one server connection at a time. Disconnect from current server before connecting to another.

**Q: Why is my connection slow?**

A: Possible reasons:
- High server ping (>200ms)
- Server is overloaded
- Server location is far from you
- Your internet connection is slow
- Try servers with lower ping

### Settings Questions

**Q: What's the best refresh interval?**

A: 
- 10-30 seconds: Good balance for most users
- 60+ seconds: If you have stable subscriptions
- 5-10 seconds: If servers change frequently

**Q: Will changing theme affect performance?**

A: No, themes are purely visual and don't impact connection performance.

**Q: Where are my settings stored?**

A: In `~/.config/v2ray-client/settings.json`. You can back up this file to preserve your settings.

**Q: Can I edit settings.json manually?**

A: Yes, but close the application first. Invalid JSON will be reset to defaults.

### Technical Questions

**Q: Which protocols are supported?**

A: Currently supported:
- VMess
- VLess  
- Trojan

**Q: Does it support Shadowsocks?**

A: Not yet, but it's on the roadmap for future versions.

**Q: Can I use custom V2Ray configurations?**

A: Currently, only subscription-based configurations are supported. Manual configuration may be added in future versions.

**Q: How do I update V2Ray Core?**

A: Run the V2Ray installation script again:
```bash
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
```

**Q: Where are V2Ray logs stored?**

A: Logs are only displayed in the application. They're not saved to disk unless you export them.

**Q: Can I run this on other Linux distributions?**

A: It should work on most Debian-based distributions. For others, you may need to adjust installation steps.

### Troubleshooting Questions

**Q: Application won't start**

A: Try:
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
./venv/bin/pip install -r requirements.txt

# Run from terminal to see errors
python3 main.py
```

**Q: "PyQt6 not found" error**

A: Install PyQt6:
```bash
./venv/bin/pip install PyQt6
```

**Q: Icons are missing**

A: Download icons:
```bash
python3 download_flags.py
python3 create_status_icons.py
python3 create_app_icons.py
```

**Q: Permission denied errors**

A: Fix permissions:
```bash
chmod 700 ~/.config/v2ray-client
chmod 600 ~/.config/v2ray-client/*.json
```

**Q: High CPU usage**

A: 
- Increase refresh interval to 60+ seconds
- Reduce number of subscriptions
- Close and reopen the application

**Q: Application crashes on startup**

A: Check for:
- Corrupted settings.json (delete and restart)
- Missing dependencies (reinstall requirements.txt)
- Qt platform plugin issues (install qt6-qpa-plugins)

### Privacy and Security Questions

**Q: Is my data encrypted?**

A: Yes, V2Ray encrypts all traffic between your device and the V2Ray server. However, the server provider can see your traffic.

**Q: Are my subscription URLs stored securely?**

A: URLs are stored in plain text in `~/.config/v2ray-client/subscriptions.json` with user-only read permissions (chmod 600).

**Q: Does the application collect any data?**

A: No, the application doesn't collect or transmit any usage data. All operations are local.

**Q: Can my ISP see I'm using V2Ray?**

A: Your ISP can see encrypted traffic to V2Ray servers but cannot see the content. Some protocols (like VMess with TLS) are harder to detect.

---

## Getting Help

If you need additional help:

1. **Check the Logs tab** for error messages
2. **Review this guide** for common solutions
3. **Search GitHub Issues** for similar problems
4. **Open a new issue** with:
   - Ubuntu version
   - Python version
   - V2Ray Core version
   - Steps to reproduce
   - Log output

---

## Tips and Best Practices

### For Best Performance

1. **Choose nearby servers**: Lower ping = faster speeds
2. **Test multiple servers**: Performance varies by server
3. **Use appropriate refresh interval**: Balance freshness vs. network usage
4. **Keep V2Ray Core updated**: Newer versions have improvements

### For Reliability

1. **Add multiple subscriptions**: Redundancy if one fails
2. **Monitor logs**: Catch issues early
3. **Export logs before troubleshooting**: Helpful for support
4. **Backup settings.json**: Easy to restore configuration

### For Privacy

1. **Use TLS-enabled servers**: Better encryption
2. **Verify server provider reputation**: Trust is important
3. **Don't share subscription URLs**: They may be tied to your account
4. **Disconnect when not needed**: Reduces exposure

---

**Last Updated**: 2025-11-10

For more information, visit the [GitHub repository](https://github.com/yourusername/v2ray-client).
