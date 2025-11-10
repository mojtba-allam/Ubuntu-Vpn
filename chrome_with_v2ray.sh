#!/bin/bash
# Launch Chrome with V2Ray Proxy

echo "=========================================="
echo "🌐 Launching Chrome with V2Ray Proxy"
echo "=========================================="
echo ""

# Check if V2Ray is running
if ! pgrep -x "v2ray" > /dev/null; then
    echo "❌ V2Ray is not running!"
    echo ""
    echo "Please start V2Ray first:"
    echo "  ./run.sh"
    echo ""
    exit 1
fi

echo "✅ V2Ray is running"
echo ""

# Check if Chrome is already running
if pgrep -f "chrome.*proxy-server" > /dev/null; then
    echo "⚠️  Chrome with proxy is already running"
    echo "   Close it first if you want to restart"
    echo ""
    exit 0
fi

# Find Chrome executable
CHROME=""
if command -v google-chrome &> /dev/null; then
    CHROME="google-chrome"
elif command -v google-chrome-stable &> /dev/null; then
    CHROME="google-chrome-stable"
elif command -v chromium &> /dev/null; then
    CHROME="chromium"
elif command -v chromium-browser &> /dev/null; then
    CHROME="chromium-browser"
else
    echo "❌ Chrome/Chromium not found!"
    echo ""
    echo "Please install Chrome or use Firefox with manual proxy:"
    echo "  Settings → Network → Manual Proxy"
    echo "  SOCKS Host: 127.0.0.1, Port: 10808"
    echo ""
    exit 1
fi

echo "✅ Found: $CHROME"
echo ""
echo "🚀 Launching Chrome with V2Ray proxy..."
echo "   Proxy: socks5://127.0.0.1:1080"
echo ""
echo "Note: This Chrome instance will use V2Ray for all connections"
echo "      Close this terminal to stop Chrome"
echo ""

# Launch Chrome with proxy
$CHROME \
    --proxy-server="socks5://127.0.0.1:1080" \
    --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" \
    > /dev/null 2>&1 &

CHROME_PID=$!

echo "✅ Chrome launched (PID: $CHROME_PID)"
echo ""
echo "Test your connection:"
echo "  1. Open: https://ipinfo.io"
echo "  2. Check if your IP is from France"
echo ""
echo "Press Ctrl+C to stop..."
echo ""

# Wait for Chrome to exit
wait $CHROME_PID

echo ""
echo "Chrome closed."
