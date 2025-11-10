# V2Ray Client - Quick Start Guide

## 🚀 Run the Application

### Easiest Way (Recommended)

```bash
./run.sh
```

### Alternative Ways

```bash
# Direct Python execution
./venv/bin/python main.py

# With theme selection
./venv/bin/python main.py --theme neon

# Show help
./venv/bin/python main.py --help
```

## 📋 Prerequisites Checklist

- [x] Python 3.8+ installed
- [x] Virtual environment created (`venv/`)
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [ ] V2Ray Core installed (required for VPN connections)

### Install V2Ray Core

```bash
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
```

## 🎯 First Time Setup

1. **Launch the application:**
   ```bash
   ./run.sh
   ```

2. **Add a subscription:**
   - Go to **Settings** tab
   - Click **"Add Subscription"**
   - Enter your subscription URL
   - Click **"Save"**

3. **Load servers:**
   - Go to **Servers** tab
   - Click **"Refresh"** button
   - Wait for servers to load

4. **Connect to a server:**
   - Click **"Connect"** on any server card
   - Wait for connection to establish
   - Your new IP will be displayed

5. **Disconnect:**
   - Click **"Disconnect"** button

## 📱 Application Tabs

### Servers Tab
- View all available servers
- Connect/disconnect with one click
- See server ping and location
- Search and filter servers

### Settings Tab
- Manage subscription URLs
- Configure refresh interval
- Change theme (Dark/Light/Neon)
- Enable auto-start

### Logs Tab
- View real-time V2Ray logs
- Monitor connection status
- Export logs for troubleshooting
- Clear log history

## 🧪 Test the Application

### Test Connection

```bash
# Run basic connection test
./test_connection.sh basic

# Test with IP verification
./test_connection.sh ip

# Test stability (30 seconds)
./test_connection.sh stability
```

### Run All Tests

```bash
# Run unit tests
./venv/bin/pytest tests/ -v

# Run with coverage
./venv/bin/pytest tests/ --cov=. --cov-report=html
```

## 🎨 Themes

Choose from three beautiful themes:

- **Dark** - Easy on the eyes
- **Light** - Clean and bright
- **Neon** - Colorful gradients (default)

Change theme in Settings tab or via command line:
```bash
./run.sh --theme dark
./run.sh --theme light
./run.sh --theme neon
```

## 🔧 Troubleshooting

### Application won't start

```bash
# Install dependencies
./venv/bin/pip install -r requirements.txt

# Check Python version (need 3.8+)
python3 --version
```

### No servers showing

1. Add a subscription URL in Settings
2. Click Refresh in Servers tab
3. Check internet connection
4. Verify subscription URL is valid

### Connection fails

1. Check V2Ray is installed: `v2ray version`
2. View logs in Logs tab
3. Try a different server
4. Check firewall settings

### V2Ray not found

```bash
# Install V2Ray Core
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# Verify installation
v2ray version
```

## 📚 Documentation

- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Complete usage guide
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Test suite documentation
- **[tests/README_CONNECTION_TESTS.md](tests/README_CONNECTION_TESTS.md)** - Connection testing guide
- **[docs/README.md](docs/README.md)** - Full project documentation

## 🎯 Common Commands

```bash
# Run application
./run.sh

# Run with specific theme
./run.sh --theme neon

# Show version
./run.sh --version

# Show help
./run.sh --help

# Run tests
./test_connection.sh basic

# Run all tests
./venv/bin/pytest tests/ -v
```

## 🔐 Security Notes

- Config files stored in `~/.config/v2ray-client/`
- Never share subscription URLs publicly
- Use TLS when available
- Monitor logs for suspicious activity

## 💡 Tips

1. **Sort by ping** - Find fastest servers
2. **Use refresh** - Keep server list updated
3. **Check logs** - Troubleshoot connection issues
4. **Export logs** - Save for later analysis
5. **Try different servers** - If one doesn't work

## 🆘 Need Help?

1. Check the **Logs tab** for error messages
2. Read **[HOW_TO_RUN.md](HOW_TO_RUN.md)** for detailed guide
3. Run tests to verify installation: `./test_connection.sh basic`
4. Check V2Ray is installed: `v2ray version`

## 🎉 You're Ready!

The application is now ready to use. Enjoy secure VPN connections! 🚀

---

**Quick Links:**
- [Full Documentation](HOW_TO_RUN.md)
- [Test Guide](tests/README_CONNECTION_TESTS.md)
- [Project Specs](.kiro/specs/ubuntu-v2ray-client/)
