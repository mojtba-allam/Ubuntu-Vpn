# V2Ray Client Packaging Guide

This document describes how to build and distribute the V2Ray Client application using different packaging formats.

## Overview

The V2Ray Client supports three distribution methods:

1. **Direct Installation** - Using `install.sh` script
2. **.deb Package** - For Debian/Ubuntu systems
3. **AppImage** - Universal Linux package

## Prerequisites

### System Requirements

- Ubuntu 20.04 or later (or compatible Debian-based distribution)
- Python 3.8 or later
- V2Ray Core (installed separately)

### Build Dependencies

For .deb packages:
```bash
sudo apt-get install build-essential debhelper devscripts dh-python python3-all
```

For AppImage:
```bash
sudo apt-get install python3 python3-pip wget
```

## Method 1: Direct Installation

The `install.sh` script provides a simple installation method for development and testing.

### Features

- Checks Ubuntu version (20.04+)
- Installs system dependencies
- Installs Python packages
- Installs and verifies V2Ray Core
- Creates configuration directory with proper permissions
- Creates desktop entry
- Sets up initial configuration files

### Usage

```bash
chmod +x install.sh
./install.sh
```

### What It Does

1. Verifies Ubuntu version compatibility
2. Installs Python 3, pip, curl, and wget
3. Installs Python packages from requirements.txt
4. Downloads and installs V2Ray Core
5. Creates `~/.config/v2ray-client/` directory
6. Creates initial settings and subscriptions files
7. Creates desktop entry in `~/.local/share/applications/`
8. Sets proper file permissions

### Configuration Files Created

- `~/.config/v2ray-client/settings.json` - Application settings
- `~/.config/v2ray-client/subscriptions.json` - Subscription URLs
- `~/.config/v2ray-client/logs/` - Log directory
- `~/.config/v2ray-client/cache/` - Cache directory

## Method 2: .deb Package

The .deb package provides a standard Debian/Ubuntu installation method.

### Building the Package

```bash
chmod +x build-deb.sh
./build-deb.sh
```

### Build Process

1. Checks for build dependencies
2. Installs missing dependencies if needed
3. Cleans previous builds
4. Sets permissions on debian scripts
5. Builds the package using `dpkg-buildpackage`
6. Creates the .deb file in the parent directory

### Package Structure

```
debian/
├── control          # Package metadata and dependencies
├── changelog        # Version history
├── compat           # Debhelper compatibility level
├── copyright        # License information
├── rules            # Build rules
├── postinst         # Post-installation script
├── prerm            # Pre-removal script
└── postrm           # Post-removal script
```

### Installing the Package

```bash
# Install the package
sudo dpkg -i ../v2ray-client_1.0.0_all.deb

# Install dependencies if needed
sudo apt-get install -f

# Install V2Ray Core (required)
sudo bash -c "$(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)"
```

### Package Contents

- `/usr/bin/v2ray-client` - Executable wrapper
- `/usr/share/v2ray-client/` - Application files
- `/usr/share/applications/v2ray-client.desktop` - Desktop entry
- `/usr/share/v2ray-client/config-template/` - Configuration templates

### Uninstalling

```bash
# Remove package but keep configuration
sudo apt-get remove v2ray-client

# Remove package and configuration
sudo apt-get purge v2ray-client
```

## Method 3: AppImage

The AppImage provides a portable, self-contained application bundle.

### Building the AppImage

```bash
chmod +x build-appimage.sh
./build-appimage.sh
```

### Build Process

1. Downloads appimagetool if not present
2. Creates AppDir structure
3. Copies Python interpreter and libraries
4. Installs Python dependencies (PyQt6, requests)
5. Copies application files
6. Creates wrapper scripts
7. Builds the AppImage

### AppImage Structure

```
AppDir/
├── AppRun                    # Main entry point
├── v2ray-client.desktop      # Desktop integration
├── v2ray-client.png          # Application icon
└── usr/
    ├── bin/
    │   ├── python3           # Bundled Python
    │   └── v2ray-client      # Wrapper script
    ├── lib/
    │   └── python3/
    │       └── dist-packages/ # Python dependencies
    └── share/
        └── v2ray-client/      # Application files
```

### Running the AppImage

```bash
# Make executable
chmod +x V2RayClient-1.0.0-x86_64.AppImage

# Run directly
./V2RayClient-1.0.0-x86_64.AppImage

# Or install system-wide
sudo mv V2RayClient-1.0.0-x86_64.AppImage /usr/local/bin/v2ray-client
sudo chmod +x /usr/local/bin/v2ray-client
```

### AppImage Features

- Self-contained (includes Python and dependencies)
- No installation required
- Portable across Linux distributions
- Automatic configuration directory creation
- V2Ray Core detection with user-friendly error messages

### AppImage Limitations

- V2Ray Core must be installed separately
- Larger file size due to bundled dependencies
- First run may be slower due to extraction

## Comparison

| Feature | install.sh | .deb Package | AppImage |
|---------|-----------|--------------|----------|
| Installation | Manual | System package manager | None required |
| Dependencies | Installed globally | Managed by apt | Bundled |
| Updates | Manual | apt upgrade | Manual download |
| Uninstall | Manual cleanup | apt remove | Delete file |
| Size | Smallest | Small | Largest |
| Portability | Ubuntu only | Debian/Ubuntu | All Linux |
| System Integration | Good | Excellent | Good |

## Post-Installation

### Installing V2Ray Core

All three methods require V2Ray Core to be installed separately:

```bash
sudo bash -c "$(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)"
```

### Verifying Installation

```bash
# Check V2Ray Core
v2ray --version

# Run the application
v2ray-client

# Or search for "V2Ray Client" in your application menu
```

### Configuration

1. Launch V2Ray Client
2. Go to Settings tab
3. Add your subscription URLs
4. Wait for server list to populate
5. Go to Servers tab
6. Click Connect on a server

## Troubleshooting

### .deb Package Issues

**Problem:** Dependencies not installed
```bash
sudo apt-get install -f
```

**Problem:** Package conflicts
```bash
sudo apt-get remove v2ray-client
sudo apt-get autoremove
sudo dpkg -i ../v2ray-client_1.0.0_all.deb
```

### AppImage Issues

**Problem:** AppImage won't run
```bash
# Make sure it's executable
chmod +x V2RayClient-1.0.0-x86_64.AppImage

# Check for FUSE
sudo apt-get install fuse libfuse2
```

**Problem:** V2Ray Core not found
```bash
# Install V2Ray Core
sudo bash -c "$(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)"

# Verify installation
which v2ray
v2ray --version
```

### General Issues

**Problem:** Python dependencies missing
```bash
pip3 install -r requirements.txt
```

**Problem:** Permission denied
```bash
# For config directory
chmod 700 ~/.config/v2ray-client

# For executable
chmod +x /path/to/v2ray-client
```

## Development

### Testing Packages Locally

**.deb package:**
```bash
# Build
./build-deb.sh

# Inspect
dpkg-deb -I ../v2ray-client_1.0.0_all.deb
dpkg-deb -c ../v2ray-client_1.0.0_all.deb

# Install in test environment
sudo dpkg -i ../v2ray-client_1.0.0_all.deb
```

**AppImage:**
```bash
# Build
./build-appimage.sh

# Test
./V2RayClient-1.0.0-x86_64.AppImage

# Extract for inspection
./V2RayClient-1.0.0-x86_64.AppImage --appimage-extract
```

### Modifying Packages

**Update version:**
1. Edit `debian/changelog` for .deb
2. Edit `APP_VERSION` in `build-appimage.sh` for AppImage

**Add dependencies:**
1. Edit `debian/control` for .deb
2. Edit `requirements.txt` and rebuild for AppImage

**Change installation paths:**
1. Edit `debian/rules` for .deb
2. Edit `build-appimage.sh` for AppImage

## Distribution

### Hosting .deb Packages

```bash
# Create a simple repository
mkdir -p repo/pool/main
cp ../v2ray-client_1.0.0_all.deb repo/pool/main/

# Generate Packages file
cd repo
dpkg-scanpackages pool/main /dev/null | gzip -9c > pool/main/Packages.gz
```

### Hosting AppImages

```bash
# Upload to GitHub Releases
gh release create v1.0.0 V2RayClient-1.0.0-x86_64.AppImage

# Or use any file hosting service
```

## License

This packaging configuration is part of the V2Ray Client project and is licensed under the MIT License.

## Support

For issues related to packaging:
- Check this documentation
- Review build logs
- Open an issue on GitHub

For application issues:
- Check the main README.md
- Review application logs in ~/.config/v2ray-client/logs/
