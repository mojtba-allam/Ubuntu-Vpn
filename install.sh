#!/bin/bash

# Ubuntu V2Ray Client Installation Script
# Supports Ubuntu 20.04 and later

set -e

echo "=========================================="
echo "Ubuntu V2Ray Client Installation Script"
echo "=========================================="
echo ""

# Check if running on Ubuntu
if [ ! -f /etc/os-release ]; then
    echo "Error: Cannot detect OS. This script is designed for Ubuntu."
    exit 1
fi

source /etc/os-release

if [ "$ID" != "ubuntu" ]; then
    echo "Error: This script is designed for Ubuntu. Detected: $ID"
    exit 1
fi

# Check Ubuntu version (20.04 or later)
VERSION_ID_NUM=$(echo $VERSION_ID | cut -d. -f1)
VERSION_ID_MINOR=$(echo $VERSION_ID | cut -d. -f2)

if [ "$VERSION_ID_NUM" -lt 20 ]; then
    echo "Error: Ubuntu 20.04 or later is required. Detected: $VERSION_ID"
    exit 1
elif [ "$VERSION_ID_NUM" -eq 20 ] && [ "$VERSION_ID_MINOR" -lt 4 ]; then
    echo "Error: Ubuntu 20.04 or later is required. Detected: $VERSION_ID"
    exit 1
fi

echo "✓ Detected Ubuntu $VERSION_ID (supported)"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Warning: Running as root. It's recommended to run this script as a regular user with sudo privileges."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip curl wget

echo "✓ System dependencies installed"
echo ""

# Install Python packages
echo "Installing Python packages..."
pip3 install --user -r requirements.txt

echo "✓ Python packages installed"
echo ""

# Install V2Ray Core
echo "Installing V2Ray Core..."
if command -v v2ray &> /dev/null; then
    echo "V2Ray Core is already installed."
    V2RAY_VERSION=$(v2ray --version 2>&1 | head -n 1)
    echo "$V2RAY_VERSION"
    
    # Verify V2Ray can run
    if v2ray test -config /dev/null 2>&1 | grep -q "failed to load config"; then
        echo "✓ V2Ray Core verification successful"
    else
        echo "Warning: V2Ray Core may not be functioning correctly"
    fi
else
    echo "Downloading and installing V2Ray Core..."
    bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
    
    if command -v v2ray &> /dev/null; then
        V2RAY_VERSION=$(v2ray --version 2>&1 | head -n 1)
        echo "✓ V2Ray Core installed successfully"
        echo "$V2RAY_VERSION"
        
        # Verify installation
        if v2ray test -config /dev/null 2>&1 | grep -q "failed to load config"; then
            echo "✓ V2Ray Core verification successful"
        else
            echo "Error: V2Ray Core installation verification failed"
            exit 1
        fi
    else
        echo "Error: V2Ray Core installation failed"
        echo "Please install V2Ray Core manually from: https://github.com/v2fly/v2ray-core"
        exit 1
    fi
fi

echo ""

# Create configuration directory
echo "Creating configuration directory..."
CONFIG_DIR="$HOME/.config/v2ray-client"
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

# Create subdirectories
mkdir -p "$CONFIG_DIR/logs"
mkdir -p "$CONFIG_DIR/cache"
chmod 700 "$CONFIG_DIR/logs"
chmod 700 "$CONFIG_DIR/cache"

# Create initial settings file if it doesn't exist
if [ ! -f "$CONFIG_DIR/settings.json" ]; then
    cat > "$CONFIG_DIR/settings.json" << 'EOF'
{
    "theme": "dark",
    "refresh_interval": 10,
    "auto_start": false,
    "sort_by": "ping",
    "subscriptions": [],
    "last_connected_server": null
}
EOF
    chmod 600 "$CONFIG_DIR/settings.json"
    echo "✓ Initial settings file created"
fi

# Create subscriptions file if it doesn't exist
if [ ! -f "$CONFIG_DIR/subscriptions.json" ]; then
    echo "[]" > "$CONFIG_DIR/subscriptions.json"
    chmod 600 "$CONFIG_DIR/subscriptions.json"
    echo "✓ Subscriptions file created"
fi

echo "✓ Configuration directory created at $CONFIG_DIR"
echo ""

# Create desktop entry
echo "Creating desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/v2ray-client.desktop"
mkdir -p "$HOME/.local/share/applications"

# Get absolute path to the application
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if icon exists, use fallback if not
if [ -f "$APP_DIR/ui/icons/app/v2ray-client.png" ]; then
    ICON_PATH="$APP_DIR/ui/icons/app/v2ray-client.png"
else
    # Use a generic network icon as fallback
    ICON_PATH="network-vpn"
fi

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=V2Ray Client
Comment=Modern V2Ray VPN Client for Ubuntu
Exec=python3 $APP_DIR/main.py
Icon=$ICON_PATH
Terminal=false
Categories=Network;VPN;
StartupNotify=true
Keywords=vpn;v2ray;proxy;network;
EOF

chmod 644 "$DESKTOP_FILE"

# Update desktop database if available
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo "✓ Desktop entry created at $DESKTOP_FILE"
echo ""

# Set permissions for main script
if [ -f "$APP_DIR/main.py" ]; then
    chmod +x "$APP_DIR/main.py"
    echo "✓ Main script permissions set"
else
    echo "Warning: main.py not found in $APP_DIR"
    echo "The application may not run until main.py is present."
fi

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "Installation Summary:"
echo "  - Ubuntu Version: $VERSION_ID"
echo "  - V2Ray Core: Installed and verified"
echo "  - Python Packages: Installed"
echo "  - Configuration Directory: $CONFIG_DIR"
echo "  - Desktop Entry: $DESKTOP_FILE"
echo ""
echo "Configuration files created:"
echo "  - $CONFIG_DIR/settings.json"
echo "  - $CONFIG_DIR/subscriptions.json"
echo "  - $CONFIG_DIR/logs/ (directory)"
echo "  - $CONFIG_DIR/cache/ (directory)"
echo ""
echo "To run the application:"
echo "  python3 $APP_DIR/main.py"
echo ""
echo "Or search for 'V2Ray Client' in your application menu."
echo ""
echo "Note: Make sure to add your subscription URLs in the Settings tab"
echo "      before attempting to connect to a server."
echo ""
