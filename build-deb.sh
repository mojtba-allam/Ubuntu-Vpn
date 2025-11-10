#!/bin/bash

# V2Ray Client .deb Package Build Script

set -e

echo "=========================================="
echo "V2Ray Client .deb Package Builder"
echo "=========================================="
echo ""

# Check if running on Ubuntu/Debian
if [ ! -f /etc/os-release ]; then
    echo "Error: Cannot detect OS."
    exit 1
fi

source /etc/os-release

if [ "$ID" != "ubuntu" ] && [ "$ID" != "debian" ]; then
    echo "Warning: This script is designed for Ubuntu/Debian. Detected: $ID"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for required build tools
echo "Checking build dependencies..."
MISSING_DEPS=()

if ! command -v dpkg-deb &> /dev/null; then
    MISSING_DEPS+=("dpkg-dev")
fi

if ! command -v debuild &> /dev/null; then
    MISSING_DEPS+=("devscripts")
fi

if ! command -v dh &> /dev/null; then
    MISSING_DEPS+=("debhelper")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "Missing build dependencies: ${MISSING_DEPS[*]}"
    echo "Installing build dependencies..."
    sudo apt-get update
    sudo apt-get install -y build-essential debhelper devscripts dh-python python3-all
    echo "✓ Build dependencies installed"
else
    echo "✓ All build dependencies present"
fi

echo ""

# Get version from changelog
if [ -f debian/changelog ]; then
    VERSION=$(head -n 1 debian/changelog | sed 's/.*(\(.*\)).*/\1/')
    echo "Building version: $VERSION"
else
    echo "Error: debian/changelog not found"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf debian/v2ray-client
rm -f ../v2ray-client_*.deb
rm -f ../v2ray-client_*.changes
rm -f ../v2ray-client_*.buildinfo
rm -f ../v2ray-client_*.tar.xz
rm -f ../v2ray-client_*.dsc

echo "✓ Cleaned"
echo ""

# Make debian scripts executable
echo "Setting permissions on debian scripts..."
chmod +x debian/postinst
chmod +x debian/prerm
chmod +x debian/postrm
chmod +x debian/rules
echo "✓ Permissions set"
echo ""

# Build the package
echo "Building .deb package..."
echo "This may take a few minutes..."
echo ""

# Build without signing (for local builds)
dpkg-buildpackage -us -uc -b

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Build completed successfully!"
    echo "=========================================="
    echo ""
    
    # Find and display the generated .deb file
    DEB_FILE=$(ls -t ../v2ray-client_*.deb 2>/dev/null | head -n 1)
    
    if [ -n "$DEB_FILE" ]; then
        DEB_SIZE=$(du -h "$DEB_FILE" | cut -f1)
        echo "Package created: $DEB_FILE"
        echo "Package size: $DEB_SIZE"
        echo ""
        echo "To install the package:"
        echo "  sudo dpkg -i $DEB_FILE"
        echo "  sudo apt-get install -f  # Install dependencies if needed"
        echo ""
        echo "To test the package:"
        echo "  dpkg-deb -I $DEB_FILE  # Show package info"
        echo "  dpkg-deb -c $DEB_FILE  # List package contents"
        echo ""
    else
        echo "Warning: Could not find generated .deb file"
    fi
else
    echo ""
    echo "=========================================="
    echo "Build failed!"
    echo "=========================================="
    echo ""
    echo "Please check the error messages above."
    exit 1
fi
