#!/bin/bash
# V2Ray Client Launcher Script

echo "=========================================="
echo "🚀 V2Ray Client for Ubuntu"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo ""
    echo "Please create a virtual environment first:"
    echo "  python3 -m venv venv"
    echo "  ./venv/bin/pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Check if dependencies are installed
if ! ./venv/bin/python -c "import PyQt6" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo ""
    echo "Installing dependencies..."
    ./venv/bin/pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if V2Ray is installed
if ! command -v v2ray &> /dev/null; then
    echo "⚠️  V2Ray Core not found!"
    echo ""
    echo "V2Ray is required for VPN connections."
    echo "Install it with:"
    echo "  bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)"
    echo ""
    read -p "Continue without V2Ray? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    V2RAY_VERSION=$(v2ray version 2>&1 | head -n 1)
    echo "✅ V2Ray found: $V2RAY_VERSION"
fi

echo ""
echo "🎨 Launching V2Ray Client..."
echo ""

# Parse command line arguments
THEME=""
CONFIG_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --theme)
            THEME="--theme $2"
            shift 2
            ;;
        --config)
            CONFIG_DIR="--config $2"
            shift 2
            ;;
        --help|-h)
            ./venv/bin/python main.py --help
            exit 0
            ;;
        --version|-v)
            ./venv/bin/python main.py --version
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the application
./venv/bin/python main.py $THEME $CONFIG_DIR

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "=========================================="
    echo "❌ Application exited with error code: $EXIT_CODE"
    echo "=========================================="
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if you're in a graphical environment"
    echo "  2. Verify all dependencies are installed"
    echo "  3. Check the logs in ~/.config/v2ray-client/"
    echo ""
fi

exit $EXIT_CODE
