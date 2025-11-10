#!/bin/bash
# Helper script to run real connection tests

echo "=========================================="
echo "V2Ray Real Connection Test Runner"
echo "=========================================="
echo ""

# Check if V2Ray is installed
echo "🔍 Checking for V2Ray installation..."
if command -v v2ray &> /dev/null; then
    V2RAY_PATH=$(which v2ray)
    V2RAY_VERSION=$(v2ray --version 2>&1 | head -n 1)
    echo "✅ V2Ray found at: $V2RAY_PATH"
    echo "   Version: $V2RAY_VERSION"
else
    echo "❌ V2Ray not found!"
    echo ""
    echo "Please install V2Ray first:"
    echo "  bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)"
    echo ""
    exit 1
fi

echo ""

# Check if pytest is available
echo "🔍 Checking for pytest..."
if ./venv/bin/pytest --version &> /dev/null; then
    echo "✅ pytest found"
else
    echo "❌ pytest not found in virtual environment!"
    echo ""
    echo "Please install dependencies:"
    echo "  ./venv/bin/pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo ""

# Check for PySocks (required for SOCKS proxy testing)
echo "🔍 Checking for PySocks (required for proxy tests)..."
if ./venv/bin/python -c "import socks" 2>/dev/null; then
    echo "✅ PySocks found"
else
    echo "⚠️  PySocks not found - installing..."
    ./venv/bin/pip install PySocks
    if [ $? -eq 0 ]; then
        echo "✅ PySocks installed"
    else
        echo "❌ Failed to install PySocks"
        echo "   Some tests may fail without it"
    fi
fi

echo ""
echo "=========================================="
echo "Running Tests"
echo "=========================================="
echo ""

# Parse command line arguments
TEST_FILTER=""
VERBOSE="-v -s"

if [ "$1" == "quick" ]; then
    echo "🚀 Running quick tests (excluding slow tests)..."
    TEST_FILTER='-m "not slow"'
elif [ "$1" == "all" ]; then
    echo "🚀 Running all tests (including slow tests)..."
    TEST_FILTER=""
elif [ "$1" == "stability" ]; then
    echo "🚀 Running stability test only..."
    TEST_FILTER="-k test_connection_stability"
elif [ "$1" == "ip" ]; then
    echo "🚀 Running IP verification test only..."
    TEST_FILTER="-k test_connection_with_ip_check"
elif [ "$1" == "basic" ]; then
    echo "🚀 Running basic connection test only..."
    TEST_FILTER="-k test_connect_to_real_vless_server"
elif [ "$1" == "long" ]; then
    echo "🚀 Running long-running test (2 minutes)..."
    TEST_FILTER="-k test_long_running_connection"
else
    echo "🚀 Running all tests except slow ones..."
    echo ""
    echo "Usage: $0 [quick|all|basic|ip|stability|long]"
    echo "  quick     - Run all tests except slow ones (default)"
    echo "  all       - Run all tests including slow ones"
    echo "  basic     - Run basic connection test only"
    echo "  ip        - Run IP verification test only"
    echo "  stability - Run 30-second stability test only"
    echo "  long      - Run 2-minute long-running test"
    echo ""
    TEST_FILTER='-m "not slow"'
fi

echo ""

# Run the tests
./venv/bin/pytest tests/test_real_connection.py $VERBOSE $TEST_FILTER

TEST_RESULT=$?

echo ""
echo "=========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed (exit code: $TEST_RESULT)"
fi
echo "=========================================="
echo ""

exit $TEST_RESULT
