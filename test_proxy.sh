#!/bin/bash
# Test V2Ray Proxy Connection

echo "=========================================="
echo "🧪 Testing V2Ray Proxy"
echo "=========================================="
echo ""

# Check if V2Ray is running
if pgrep -x "v2ray" > /dev/null; then
    echo "✅ V2Ray process is running"
    echo "   PID: $(pgrep -x v2ray)"
else
    echo "❌ V2Ray is not running!"
    echo "   Please start the V2Ray client first"
    exit 1
fi

echo ""

# Check if SOCKS port is listening
if netstat -tuln 2>/dev/null | grep -q ":10808"; then
    echo "✅ SOCKS proxy listening on port 10808"
elif ss -tuln 2>/dev/null | grep -q ":10808"; then
    echo "✅ SOCKS proxy listening on port 10808"
else
    echo "⚠️  Port 10808 not listening"
    echo "   V2Ray might still be starting..."
fi

echo ""

# Check if HTTP port is listening
if netstat -tuln 2>/dev/null | grep -q ":10809"; then
    echo "✅ HTTP proxy listening on port 10809"
elif ss -tuln 2>/dev/null | grep -q ":10809"; then
    echo "✅ HTTP proxy listening on port 10809"
else
    echo "⚠️  Port 10809 not listening"
fi

echo ""
echo "=========================================="
echo "🌐 Testing Connection Through Proxy"
echo "=========================================="
echo ""

# Test with curl (SOCKS5)
echo "1. Testing SOCKS5 proxy (port 10808)..."
if command -v curl &> /dev/null; then
    RESULT=$(curl -s --socks5 127.0.0.1:10808 --connect-timeout 10 https://ipinfo.io 2>&1)
    
    if [ $? -eq 0 ]; then
        echo "✅ SOCKS5 proxy is working!"
        echo ""
        echo "Your IP information:"
        echo "$RESULT" | grep -E '"ip"|"country"|"city"' | sed 's/^/   /'
        echo ""
        
        # Extract IP
        IP=$(echo "$RESULT" | grep '"ip"' | cut -d'"' -f4)
        COUNTRY=$(echo "$RESULT" | grep '"country"' | cut -d'"' -f4)
        
        if [ ! -z "$IP" ]; then
            echo "🎉 SUCCESS! You're connected through V2Ray!"
            echo "   IP: $IP"
            echo "   Country: $COUNTRY"
        fi
    else
        echo "❌ SOCKS5 proxy test failed"
        echo "   Error: $RESULT"
    fi
else
    echo "⚠️  curl not found, skipping test"
fi

echo ""
echo "=========================================="
echo "🔧 How to Use the Proxy"
echo "=========================================="
echo ""
echo "Your V2Ray proxy is running on:"
echo "  • SOCKS5: 127.0.0.1:10808"
echo "  • HTTP:   127.0.0.1:10809"
echo ""
echo "Configure your browser:"
echo ""
echo "Option 1: Chrome with SwitchyOmega"
echo "  1. Install SwitchyOmega extension"
echo "  2. Protocol: SOCKS5"
echo "  3. Server: 127.0.0.1"
echo "  4. Port: 10808"
echo ""
echo "Option 2: Launch Chrome with proxy"
echo "  google-chrome --proxy-server=\"socks5://127.0.0.1:10808\""
echo ""
echo "Option 3: Firefox Manual Proxy"
echo "  Settings → Network → Manual Proxy"
echo "  SOCKS Host: 127.0.0.1, Port: 10808"
echo ""
echo "Option 4: System-wide (GNOME/Ubuntu)"
echo "  gsettings set org.gnome.system.proxy mode 'manual'"
echo "  gsettings set org.gnome.system.proxy.socks host '127.0.0.1'"
echo "  gsettings set org.gnome.system.proxy.socks port 10808"
echo ""
echo "=========================================="
