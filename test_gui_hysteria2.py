#!/usr/bin/env python3
"""
Test GUI with Hysteria2 support

Tests the Ubuntu-Vpn GUI with Hysteria2 server support.
"""

import sys
import os

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow
import time


def test_gui_with_hysteria2():
    """Test GUI with Hysteria2 server support"""

    print("🖥️  Testing GUI with Hysteria2 Support")
    print("="*50)

    # Create QApplication
    app = QApplication(sys.argv)

    # Create main window
    print("🏠 Creating main window...")
    config_dir = "~/.config/v2ray-test"
    window = MainWindow(config_dir=config_dir)

    print(f"✅ Main window created")
    print(f"   Window title: {window.windowTitle()}")
    print(f"   Window size: {window.size().width()}x{window.size().height()}")

    # Test Hysteria2 manager
    print("\n🔧 Testing Hysteria2 Manager...")
    if hasattr(window, 'hysteria2_manager'):
        print("✅ Hysteria2 manager found in main window")
        if window.hysteria2_manager.hysteria_client:
            print(f"✅ Hysteria2 client: {window.hysteria2_manager.hysteria_client}")
        else:
            print("❌ Hysteria2 client not found")
    else:
        print("❌ Hysteria2 manager not found in main window")
        return False

    # Test adding Hysteria2 server
    print("\n📝 Testing Hysteria2 server configuration...")
    hysteria2_url = "hysteria2://YwuvGJk36B@81.168.83.89:2083?sni=kotlet.arshiacomplus.dpdns.org&obfs=salamander&obfs-password=khameniiko%40smad%40ret&insecure=1#%40Daily_Configs"

    try:
        server_config = window.hysteria2_manager.parse_hysteria2_url(hysteria_url)
        print("✅ Hysteria2 server config parsed successfully")
        print(f"   Name: {server_config['name']}")
        print(f"   Server: {server_config['server']}:{server_config['port']}")
        print(f"   Type: {server_config['type']}")

        # Add to server list manually for testing
        test_servers = [server_config]
        print(f"✅ Adding {len(test_servers)} server(s) to GUI...")
        window.servers_tab.update_servers(test_servers)
        print("✅ Servers added to GUI")

    except Exception as e:
        print(f"❌ Failed to test Hysteria2 server: {e}")
        return False

    # Show window briefly
    print("\n👁️  Showing GUI for testing...")
    window.show()

    # Schedule window close after 3 seconds
    QTimer.singleShot(3000, app.quit)

    print("   GUI displayed for 3 seconds...")
    print("   Testing themes...")

    # Test theme switching
    try:
        window.load_theme("dark")
        print("✅ Dark theme applied")

        QTimer.singleShot(1000, lambda: window.load_theme("light"))
        print("   Light theme will be applied after 1 second")

    except Exception as e:
        print(f"⚠️  Theme switching failed: {e}")

    # Run the event loop
    print("   Starting Qt event loop...")
    app.exec()

    print("✅ GUI test completed successfully")
    return True


def test_imports():
    """Test all required imports"""
    print("📦 Testing Imports...")
    print("="*30)

    try:
        from hysteria2_manager import Hysteria2Manager
        print("✅ Hysteria2Manager imported")
    except Exception as e:
        print(f"❌ Failed to import Hysteria2Manager: {e}")
        return False

    try:
        from config_generator import generate_v2ray_config
        print("✅ config_generator imported")
    except Exception as e:
        print(f"❌ Failed to import config_generator: {e}")
        return False

    try:
        from ui.main_window import MainWindow
        print("✅ MainWindow imported")
    except Exception as e:
        print(f"❌ Failed to import MainWindow: {e}")
        return False

    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--imports":
        test_imports()
    else:
        test_gui_with_hysteria2()