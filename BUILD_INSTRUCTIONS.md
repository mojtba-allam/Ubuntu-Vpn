# Quick Build Instructions

This document provides quick commands for building V2Ray Client packages.

## Prerequisites

```bash
# For .deb package
sudo apt-get install build-essential debhelper devscripts dh-python python3-all

# For AppImage
sudo apt-get install python3 python3-pip wget
```

## Build Commands

### 1. Direct Installation (Development)

```bash
chmod +x install.sh
./install.sh
```

### 2. Build .deb Package

```bash
chmod +x build-deb.sh
./build-deb.sh
```

Output: `../v2ray-client_1.0.0_all.deb`

### 3. Build AppImage

```bash
chmod +x build-appimage.sh
./build-appimage.sh
```

Output: `V2RayClient-1.0.0-x86_64.AppImage`

## Testing Builds

### Test .deb Package

```bash
# Inspect package
dpkg-deb -I ../v2ray-client_1.0.0_all.deb
dpkg-deb -c ../v2ray-client_1.0.0_all.deb

# Install
sudo dpkg -i ../v2ray-client_1.0.0_all.deb
sudo apt-get install -f

# Test run
v2ray-client

# Uninstall
sudo apt-get remove v2ray-client
```

### Test AppImage

```bash
# Make executable
chmod +x V2RayClient-1.0.0-x86_64.AppImage

# Run
./V2RayClient-1.0.0-x86_64.AppImage

# Extract for inspection
./V2RayClient-1.0.0-x86_64.AppImage --appimage-extract
```

## Install V2Ray Core

All packages require V2Ray Core to be installed separately:

```bash
sudo bash -c "$(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)"
```

## Verify Installation

```bash
# Check V2Ray Core
v2ray --version

# Run application
v2ray-client
```

## For More Details

See `PACKAGING.md` for comprehensive documentation.
