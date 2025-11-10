# How to Run the V2Ray Client Application

## Quick Start

```bash
# Run the application
./venv/bin/python main.py
```

That's it! The GUI application will launch.

## Prerequisites

### 1. V2Ray Core Installation

The application requires V2Ray Core to be installed:

```bash
# Install V2Ray Core
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# Verify installation
v2ray version
```

### 2. Python Dependencies

Make sure all dependencies are installed:

```bash
# Install dependencies
./venv/bin/pip install -r requirements.txt
```

## Running the Application

### Basic Usage

```bash
# Run with default settings
./venv/bin/python main.py
```

### With Command-Line Options

```bash
# Run with specific theme
./venv/bin/python main.py --theme neon

# Run with custom config directory
./venv/bin/python main.py --config ~/my-v2ray-config

# Show version
./venv/bin/python main.py --version

# Show help
./venv/bin/python main.py --help
```

### Available Themes

- `dark` - Dark theme
- `light` - Light theme  
- `neon` - Neon theme with gradients (default)

## Application Features

### 1. Servers Tab

**Add Subscription:**
1. Go to Settings tab
2. Click "Add Subscription"
3. Enter subscription URL
4. Click "Save"
5. Return to Servers tab
6. Click "Refresh" to load servers

**Connect to Server:**
1. Browse available servers in the Servers tab
2. Click "Connect" on any server card
3. Wait for connection to establish
4. Your IP will be displayed when connected

**Disconnect:**
1. Click "Disconnect" button
2. Connection will be terminated

### 2. Settings Tab

**Manage Subscriptions:**
- Add new subscription URLs
- Edit existing subscriptions
- Remove subscriptions

**Configure Refresh Interval:**
- Set how often server lists update (minimum 5 seconds)

**Change Theme:**
- Select Dark, Light, or Neon theme
- Theme applies immediately

**Auto-start:**
- Enable to launch on system startup

### 3. Logs Tab

**View V2Ray Logs:**
- Real-time log streaming from V2Ray process
- Auto-scrolls to latest entries
- Shows connection status and errors

**Export Logs:**
- Click "Export" to save logs to file
- Useful for troubleshooting

**Clear Logs:**
- Click "Clear" to remove all log entries

## Configuration

### Config Directory

Default: `~/.config/v2ray-client/`

Contains:
- `subscriptions.json` - Your subscription URLs
- `settings.json` - Application settings
- `temp_config.json` - Temporary V2Ray config (when connected)
- `manual_servers.json` - Manually added servers

### Settings File Format

`~/.config/v2ray-client/settings.json`:

```json
{
  "theme": "neon",
  "refresh_interval": 10,
  "auto_start": false,
  "sort_by": "ping"
}
```

### Subscription File Format

`~/.config/v2ray-client/subscriptions.json`:

```json
[
  {
    "url": "https://example.com/subscription",
    "name": "My Subscription",
    "last_update": "2024-01-01T12:00:00",
    "server_count": 10,
    "enabled": true
  }
]
```

## Troubleshooting

### Application Won't Start

**Error: ModuleNotFoundError**
```bash
# Install missing dependencies
./venv/bin/pip install -r requirements.txt
```

**Error: Display not found**
```bash
# Make sure you're running in a graphical environment
# If using SSH, enable X11 forwarding:
ssh -X user@host
```

### V2Ray Connection Issues

**Error: V2Ray binary not found**
```bash
# Install V2Ray Core
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# Add to PATH if needed
export PATH=$PATH:/usr/local/bin
```

**Connection fails immediately**
1. Check V2Ray logs in Logs tab
2. Verify server configuration is correct
3. Test server with manual V2Ray config
4. Check firewall settings

**No servers showing**
1. Go to Settings tab
2. Add a subscription URL
3. Click "Refresh" in Servers tab
4. Wait for servers to load

### GUI Issues

**Theme not loading**
- Check that theme files exist in `ui/themes/`
- Try switching to a different theme
- Restart the application

**Icons missing**
- Icons should be in `ui/icons/`
- Application will use text fallbacks if icons are missing

**Window too small/large**
- Resize window manually
- Settings are saved automatically

## Advanced Usage

### Running in Background

```bash
# Run in background
nohup ./venv/bin/python main.py > /dev/null 2>&1 &

# Check if running
ps aux | grep "python main.py"

# Kill process
pkill -f "python main.py"
```

### Creating Desktop Shortcut

Create `~/.local/share/applications/v2ray-client.desktop`:

```ini
[Desktop Entry]
Name=V2Ray Client
Comment=Modern V2Ray VPN Client
Exec=/path/to/your/project/venv/bin/python /path/to/your/project/main.py
Icon=/path/to/your/project/ui/icons/app_icon.png
Terminal=false
Type=Application
Categories=Network;VPN;
```

Make it executable:
```bash
chmod +x ~/.local/share/applications/v2ray-client.desktop
```

### Auto-start on Login

**Method 1: Using Desktop Entry**
```bash
# Copy desktop file to autostart
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/v2ray-client.desktop ~/.config/autostart/
```

**Method 2: Using systemd**

Create `~/.config/systemd/user/v2ray-client.service`:

```ini
[Unit]
Description=V2Ray Client
After=graphical-session.target

[Service]
Type=simple
ExecStart=/path/to/your/project/venv/bin/python /path/to/your/project/main.py
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable v2ray-client.service
systemctl --user start v2ray-client.service
```

## Testing the Application

### Run Tests

```bash
# Run all tests
./venv/bin/pytest tests/ -v

# Run specific test file
./venv/bin/pytest tests/test_v2ray_manager.py -v

# Run with coverage
./venv/bin/pytest tests/ --cov=. --cov-report=html
```

### Test Real Connection

```bash
# Run connection tests
./test_connection.sh basic

# Test with IP verification
./test_connection.sh ip

# Test stability
./test_connection.sh stability
```

## Development

### Running in Development Mode

```bash
# Run with debug output
./venv/bin/python main.py --theme neon

# Watch logs in real-time
tail -f ~/.config/v2ray-client/app.log
```

### Code Structure

```
.
├── main.py                 # Application entry point
├── v2ray_manager.py        # V2Ray process management
├── subscription_manager.py # Subscription handling
├── server_updater.py       # Server list updates
├── ui/                     # GUI components
│   ├── main_window.py      # Main window
│   ├── servers_tab.py      # Servers tab
│   ├── settings_tab.py     # Settings tab
│   ├── logs_tab.py         # Logs tab
│   ├── server_card.py      # Server card widget
│   ├── theme_loader.py     # Theme management
│   └── themes/             # QSS theme files
└── tests/                  # Test suite
```

## Performance Tips

### Optimize Server List

- Reduce refresh interval if you have many subscriptions
- Disable unused subscriptions in Settings
- Sort servers by ping to find fastest ones

### Reduce Memory Usage

- Clear logs regularly
- Limit number of active subscriptions
- Close application when not in use

### Improve Connection Speed

- Choose servers with lowest ping
- Use servers geographically closer to you
- Test different protocols (VMess, VLess, Trojan)

## Security Notes

### Configuration Security

- Config files are stored in `~/.config/v2ray-client/`
- Permissions should be `0600` (user read/write only)
- Never share your subscription URLs publicly
- UUIDs and passwords are sensitive data

### Network Security

- Always use TLS when available
- Verify server certificates
- Use trusted subscription sources
- Monitor logs for suspicious activity

## Getting Help

### Check Logs

1. Open Logs tab in application
2. Look for error messages
3. Check V2Ray output

### Common Error Messages

**"V2Ray binary not found"**
- Install V2Ray Core

**"Connection refused"**
- Server may be offline
- Check firewall settings
- Verify server configuration

**"Invalid configuration"**
- Check subscription URL
- Verify server format
- Test with manual config

### Report Issues

When reporting issues, include:
- Application version (`./venv/bin/python main.py --version`)
- V2Ray version (`v2ray version`)
- Operating system
- Error messages from Logs tab
- Steps to reproduce

## Uninstallation

### Remove Application

```bash
# Remove config directory
rm -rf ~/.config/v2ray-client/

# Remove desktop entry
rm ~/.local/share/applications/v2ray-client.desktop
rm ~/.config/autostart/v2ray-client.desktop

# Remove systemd service (if used)
systemctl --user stop v2ray-client.service
systemctl --user disable v2ray-client.service
rm ~/.config/systemd/user/v2ray-client.service
```

### Keep V2Ray Core

If you want to keep V2Ray for other uses:
```bash
# V2Ray remains installed at /usr/local/bin/v2ray
```

### Remove V2Ray Core

```bash
# Remove V2Ray
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh) --remove
```

## Additional Resources

- [V2Ray Documentation](https://www.v2ray.com/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Project README](README.md)
- [Test Documentation](tests/README_CONNECTION_TESTS.md)

---

**Enjoy using V2Ray Client! 🚀**
