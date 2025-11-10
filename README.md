# V2Ray Client for Ubuntu

A modern, user-friendly V2Ray VPN client for Ubuntu with a beautiful PyQt6 interface. Manage multiple subscription sources, connect to servers with one click, and monitor your connection in real-time.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Ubuntu%2020.04+-orange.svg)

## ✨ Features

- **🎨 Modern UI**: Beautiful interface with Dark, Light, and Neon themes
- **🔗 One-Click Connect**: Connect to any V2Ray server instantly
- **📡 Multi-Protocol Support**: VMess, VLess, and Trojan protocols
- **🔄 Auto-Update**: Automatic server list refresh from subscriptions
- **🌍 Country Flags**: Visual server identification with country flags
- **⚡ Ping Display**: Real-time latency measurement for all servers
- **📊 Live Logs**: Monitor V2Ray connection logs in real-time
- **⚙️ Easy Configuration**: Simple settings management
- **🔐 Secure**: All configurations stored locally with proper permissions

## 📸 Screenshots

### Servers Tab
Browse and connect to servers with visual ping indicators and country flags.

### Settings Tab
Manage subscription URLs, refresh intervals, and theme preferences.

### Logs Tab
Monitor V2Ray connection logs in real-time for troubleshooting.

## 🚀 Quick Start

### Prerequisites

- Ubuntu 20.04 or later
- Python 3.8 or higher
- V2Ray Core (installed automatically by the script)

### Installation

#### Option 1: Using the Install Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/v2ray-client.git
cd v2ray-client

# Run the installation script
chmod +x install.sh
./install.sh
```

The script will:
- Install Python dependencies
- Install V2Ray Core
- Set up configuration directories
- Create a desktop entry

#### Option 2: Manual Installation

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install V2Ray Core
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# Create config directory
mkdir -p ~/.config/v2ray-client
```

#### Option 3: Package Installation

**Debian Package (.deb)**
```bash
sudo dpkg -i v2ray-client_1.0.0_amd64.deb
sudo apt-get install -f  # Install dependencies
```

**AppImage**
```bash
chmod +x V2RayClient-1.0.0-x86_64.AppImage
./V2RayClient-1.0.0-x86_64.AppImage
```

## 📖 Usage

### Starting the Application

```bash
# If installed via script or package
v2ray-client

# If running from source
python3 main.py
```

### Adding Subscription URLs

1. Open the **Settings** tab
2. Click **Add Subscription**
3. Enter your subscription URL
4. Click **OK**
5. The server list will update automatically

### Connecting to a Server

1. Go to the **Servers** tab
2. Browse available servers (sorted by ping)
3. Click **Connect** on your preferred server
4. Wait for the connection to establish
5. Your public IP will be displayed when connected

### Disconnecting

1. Click the **Disconnect** button on the connected server card
2. Or use the disconnect button in the status bar

### Changing Themes

1. Open the **Settings** tab
2. Select your preferred theme:
   - **Dark**: Classic dark mode
   - **Light**: Clean light mode
   - **Neon**: Vibrant gradients with glow effects
3. Theme applies immediately

### Viewing Logs

1. Open the **Logs** tab
2. View real-time V2Ray output
3. Use **Clear Logs** to reset the display
4. Use **Export Logs** to save to a file

## ⚙️ Configuration

### Configuration Files

All configuration files are stored in `~/.config/v2ray-client/`:

- `settings.json` - Application settings
- `subscriptions.json` - Subscription URLs
- `temp_config.json` - Temporary V2Ray configuration (created during connection)

### Settings Options

- **Refresh Interval**: How often to update server lists (minimum 5 seconds)
- **Theme**: Visual appearance (Dark, Light, Neon)
- **Auto-start**: Launch on system startup
- **Sort By**: Order servers by ping or name

## 🔧 Troubleshooting

### Application won't start

**Problem**: Error about missing PyQt6 or other dependencies

**Solution**:
```bash
# Reinstall dependencies
./venv/bin/pip install -r requirements.txt
```

### V2Ray Core not found

**Problem**: "v2ray command not found" error

**Solution**:
```bash
# Install V2Ray Core manually
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# Verify installation
which v2ray
v2ray --version
```

### Connection fails

**Problem**: Server connects but no internet access

**Solution**:
1. Check the **Logs** tab for error messages
2. Verify the server configuration is correct
3. Try a different server
4. Check your firewall settings:
```bash
sudo ufw status
```

### Subscription fetch fails

**Problem**: "Failed to fetch subscription" error

**Solution**:
1. Verify the URL is accessible in a browser
2. Check your internet connection
3. Some subscriptions require specific headers - check with your provider
4. Try refreshing manually with the refresh button

### Icons not displaying

**Problem**: Missing country flags or status icons

**Solution**:
```bash
# Download flag icons
python3 download_flags.py

# Verify icons directory
ls -la ui/icons/flags/
```

### Permission denied errors

**Problem**: Cannot write to config directory

**Solution**:
```bash
# Fix permissions
chmod 700 ~/.config/v2ray-client
chmod 600 ~/.config/v2ray-client/*.json
```

### High CPU usage

**Problem**: Application using too much CPU

**Solution**:
1. Increase refresh interval in Settings (e.g., 30 seconds)
2. Reduce number of subscriptions
3. Check for excessive logging in Logs tab

## 🧪 Development

### Running Tests

```bash
# Run all tests
./venv/bin/pytest tests/ -v

# Run specific test file
./venv/bin/pytest tests/test_v2ray_manager.py -v

# Run with coverage
./venv/bin/pytest tests/ --cov=. --cov-report=html
```

### Project Structure

```
v2ray-client/
├── main.py                 # Application entry point
├── v2ray_manager.py        # V2Ray process management
├── subscription_manager.py # Subscription fetching and parsing
├── server_updater.py       # Periodic server updates
├── ui/                     # GUI components
│   ├── main_window.py      # Main application window
│   ├── servers_tab.py      # Server list display
│   ├── settings_tab.py     # Settings interface
│   ├── logs_tab.py         # Log viewer
│   ├── server_card.py      # Individual server widget
│   ├── animated_button.py  # Custom button with animations
│   ├── icon_loader.py      # Icon loading utilities
│   ├── theme_loader.py     # Theme management
│   ├── themes/             # QSS stylesheets
│   └── icons/              # Application icons
├── tests/                  # Test suite
├── debian/                 # Debian package files
├── AppDir/                 # AppImage structure
└── requirements.txt        # Python dependencies
```

### Building Packages

**Debian Package**:
```bash
chmod +x build-deb.sh
./build-deb.sh
```

**AppImage**:
```bash
chmod +x build-appimage.sh
./build-appimage.sh
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   ./venv/bin/pytest tests/ -v
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to all classes and methods
- Write tests for new features
- Keep commits atomic and well-described

### Testing Requirements

- All new features must include tests
- Maintain or improve code coverage
- Tests must pass before PR is merged

### Reporting Bugs

Please include:
- Ubuntu version
- Python version
- V2Ray Core version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [V2Ray Project](https://www.v2ray.com/) - The core VPN technology
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Country Flags](https://flagpedia.net/) - Flag icons
- All contributors and users

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/v2ray-client/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/v2ray-client/discussions)
- **Documentation**: See [USER_GUIDE.md](USER_GUIDE.md) for detailed usage instructions

## 🗺️ Roadmap

- [ ] System tray integration
- [ ] Shadowsocks protocol support
- [ ] Custom routing rules
- [ ] Bandwidth usage statistics
- [ ] Connection profiles
- [ ] Multi-language support
- [ ] Auto-connect to fastest server
- [ ] Configuration backup/restore

---

**Note**: This application is for educational and research purposes. Please comply with local laws and regulations when using VPN services.
