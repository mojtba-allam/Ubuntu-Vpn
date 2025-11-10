#!/bin/bash

# V2Ray Client AppImage Build Script

set -e

echo "=========================================="
echo "V2Ray Client AppImage Builder"
echo "=========================================="
echo ""

# Configuration
APP_NAME="V2RayClient"
APP_VERSION="1.0.0"
ARCH="x86_64"
APPIMAGE_NAME="${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
APPDIR="AppDir"

# Check if running on Linux
if [ "$(uname -s)" != "Linux" ]; then
    echo "Error: This script must be run on Linux"
    exit 1
fi

# Check for required tools
echo "Checking build dependencies..."
MISSING_TOOLS=()

if ! command -v python3 &> /dev/null; then
    MISSING_TOOLS+=("python3")
fi

if ! command -v pip3 &> /dev/null; then
    MISSING_TOOLS+=("python3-pip")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "Missing required tools: ${MISSING_TOOLS[*]}"
    echo "Please install them first."
    exit 1
fi

echo "✓ Required tools present"
echo ""

# Download appimagetool if not present
if [ ! -f "appimagetool-${ARCH}.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    chmod +x "appimagetool-${ARCH}.AppImage"
    echo "✓ appimagetool downloaded"
else
    echo "✓ appimagetool already present"
fi

echo ""

# Clean previous build
echo "Cleaning previous build..."
rm -rf "${APPDIR}/usr"
rm -f "${APPIMAGE_NAME}"
echo "✓ Cleaned"
echo ""

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib"
mkdir -p "${APPDIR}/usr/share/v2ray-client"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

echo "✓ Directory structure created"
echo ""

# Install Python in AppDir
echo "Setting up Python environment..."
echo "This may take several minutes..."

# Create a minimal Python installation
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Using Python ${PYTHON_VERSION}"

# Copy Python binary and libraries
cp -L "$(which python3)" "${APPDIR}/usr/bin/"

# Find Python library directory
PYTHON_LIB_DIR=$(python3 -c "import sys; print([p for p in sys.path if 'lib/python' in p and 'site-packages' in p][0])")
PYTHON_LIB_BASE=$(dirname "${PYTHON_LIB_DIR}")

# Copy Python standard library
mkdir -p "${APPDIR}/usr/lib/python${PYTHON_VERSION}"
cp -r "${PYTHON_LIB_BASE}/python${PYTHON_VERSION}"/* "${APPDIR}/usr/lib/python${PYTHON_VERSION}/" 2>/dev/null || true

# Create site-packages directory
mkdir -p "${APPDIR}/usr/lib/python3/dist-packages"

echo "✓ Python environment set up"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --target="${APPDIR}/usr/lib/python3/dist-packages" \
    PyQt6 \
    requests \
    --no-warn-script-location

echo "✓ Dependencies installed"
echo ""

# Copy application files
echo "Copying application files..."
cp -r *.py "${APPDIR}/usr/share/v2ray-client/" 2>/dev/null || echo "Warning: No .py files found"
cp -r ui "${APPDIR}/usr/share/v2ray-client/" 2>/dev/null || echo "Warning: ui directory not found"
cp -r tests "${APPDIR}/usr/share/v2ray-client/" 2>/dev/null || echo "Warning: tests directory not found"
cp requirements.txt "${APPDIR}/usr/share/v2ray-client/" 2>/dev/null || echo "Warning: requirements.txt not found"

echo "✓ Application files copied"
echo ""

# Create wrapper script
echo "Creating wrapper script..."
cat > "${APPDIR}/usr/bin/v2ray-client" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")/.."
export PYTHONPATH="${HERE}/lib/python3/dist-packages:${PYTHONPATH}"
cd "${HERE}/share/v2ray-client"
exec "${HERE}/bin/python3" main.py "$@"
EOF

chmod +x "${APPDIR}/usr/bin/v2ray-client"
echo "✓ Wrapper script created"
echo ""

# Copy desktop file and icon
echo "Setting up desktop integration..."
cp "${APPDIR}/v2ray-client.desktop" "${APPDIR}/usr/share/applications/"

# Copy icon if available, otherwise create a placeholder
if [ -f "ui/icons/app/v2ray-client.png" ]; then
    cp "ui/icons/app/v2ray-client.png" "${APPDIR}/usr/share/icons/hicolor/256x256/apps/"
    cp "ui/icons/app/v2ray-client.png" "${APPDIR}/"
    ln -sf "v2ray-client.png" "${APPDIR}/.DirIcon"
else
    echo "Warning: Application icon not found, using placeholder"
    # Create a simple placeholder icon (1x1 transparent PNG)
    echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > "${APPDIR}/v2ray-client.png"
    ln -sf "v2ray-client.png" "${APPDIR}/.DirIcon"
fi

echo "✓ Desktop integration set up"
echo ""

# Make AppRun executable
chmod +x "${APPDIR}/AppRun"

# Build the AppImage
echo "Building AppImage..."
echo "This may take a few minutes..."
echo ""

ARCH=${ARCH} ./appimagetool-${ARCH}.AppImage "${APPDIR}" "${APPIMAGE_NAME}"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Build completed successfully!"
    echo "=========================================="
    echo ""
    
    if [ -f "${APPIMAGE_NAME}" ]; then
        APPIMAGE_SIZE=$(du -h "${APPIMAGE_NAME}" | cut -f1)
        echo "AppImage created: ${APPIMAGE_NAME}"
        echo "AppImage size: ${APPIMAGE_SIZE}"
        echo ""
        echo "To run the AppImage:"
        echo "  chmod +x ${APPIMAGE_NAME}"
        echo "  ./${APPIMAGE_NAME}"
        echo ""
        echo "To install system-wide:"
        echo "  sudo mv ${APPIMAGE_NAME} /usr/local/bin/v2ray-client"
        echo "  sudo chmod +x /usr/local/bin/v2ray-client"
        echo ""
        echo "IMPORTANT: V2Ray Core must be installed separately:"
        echo "  sudo bash -c \"\$(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)\""
        echo ""
    else
        echo "Warning: Could not find generated AppImage"
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
