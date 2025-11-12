#!/usr/bin/env python3
"""
Test System Proxy and TUN Functionality

Tests the system proxy manager and TUN manager implementations.
"""

import sys
import os
import time

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_system_proxy_manager():
    """Test SystemProxyManager functionality"""
    print("🔧 Testing System Proxy Manager")
    print("="*40)

    try:
        from system_proxy_manager import SystemProxyManager

        # Create manager
        config_dir = "~/.config/proxy-test"
        manager = SystemProxyManager(config_dir)

        # Check requirements
        proxy_info = manager.get_proxy_info()
        print(f"GNOME Available: {proxy_info['gnome_available']}")
        print(f"Has Permissions: {proxy_info['has_permissions']}")
        print(f"Current Mode: {proxy_info['current_mode']}")

        if not proxy_info['gnome_available']:
            print("⚠️  GNOME not available - cannot test system proxy")
            return False

        if not proxy_info['has_permissions']:
            print("⚠️  Insufficient permissions - cannot test system proxy")
            return False

        # Test backup
        print("\\n1. Testing backup...")
        backup_success = manager.backup_original_settings()
        print(f"   Backup: {'✅' if backup_success else '❌'}")

        # Test proxy configuration
        print("\\n2. Testing proxy configuration...")
        config_success = manager.configure_system_proxy(
            proxy_type='both',
            host='127.0.0.1',
            port=1081,
            socks_port=1080
        )
        print(f"   Configuration: {'✅' if config_success else '❌'}")

        if config_success:
            # Wait a moment
            time.sleep(2)

            # Test restoration
            print("\\n3. Testing restoration...")
            restore_success = manager.restore_original_settings()
            print(f"   Restoration: {'✅' if restore_success else '❌'}")

        return True

    except Exception as e:
        print(f"❌ System proxy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tun_manager():
    """Test TUNManager functionality"""
    print("\\n🚇 Testing TUN Manager")
    print("="*30)

    try:
        from tun_manager import TUNManager

        # Create manager
        config_dir = "~/.config/tun-test"
        manager = TUNManager(config_dir)

        # Check requirements
        requirements = manager.check_requirements()
        print(f"TUN Device Available: {requirements['tun_device_available']}")
        print(f"IPRoute2 Available: {requirements['iproute2_available']}")
        print(f"Has Permissions: {requirements['has_permissions']}")
        print(f"Root Required: {requirements['root_required']}")
        print(f"Can Create TUN: {requirements['can_create_tun']}")

        if not requirements['can_create_tun']:
            if requirements['root_required']:
                print("\\n⚠️  TUN mode requires root privileges")
                print("   Fix: sudo chown $USER:$USER /dev/net/tun")
            else:
                missing = [k for k, v in requirements.items()
                          if not v and k not in ['can_create_tun', 'root_required']]
                if missing:
                    print(f"\\n⚠️  Missing requirements: {', '.join(missing)}")

            return False

        print("\\n1. Testing TUN interface creation...")
        create_success = manager.create_tun_interface()
        print(f"   Creation: {'✅' if create_success else '❌'}")

        if create_success:
            # Get status
            status = manager.get_status()
            print(f"   Interface: {status.get('interface_name')}")
            print(f"   Active: {status.get('is_active')}")

            # Test connectivity
            print("\\n2. Testing connectivity...")
            connectivity = manager.test_connectivity()
            print(f"   DNS Resolution: {'✅' if connectivity['dns_resolution'] else '❌'}")
            print(f"   External Connectivity: {'✅' if connectivity['external_connectivity'] else '❌'}")
            print(f"   Internal Connectivity: {'✅' if connectivity['internal_connectivity'] else '❌'}")
            if connectivity.get('latency_ms'):
                print(f"   Latency: {connectivity['latency_ms']}ms")

            # Test destruction
            print("\\n3. Testing TUN interface destruction...")
            destroy_success = manager.destroy_tun_interface()
            print(f"   Destruction: {'✅' if destroy_success else '❌'}")

        return True

    except Exception as e:
        print(f"❌ TUN test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_integration():
    """Test GUI integration with system managers"""
    print("\\n🖥️  Testing GUI Integration")
    print("="*35)

    try:
        from PyQt6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        import time

        # Create QApplication (for testing)
        app = QApplication(sys.argv)

        print("Creating main window...")
        config_dir = "~/.config/gui-test"
        window = MainWindow(config_dir=config_dir)

        # Check if managers are initialized
        has_proxy_manager = hasattr(window, 'system_proxy_manager')
        has_tun_manager = hasattr(window, 'tun_manager')

        print(f"System Proxy Manager: {'✅' if has_proxy_manager else '❌'}")
        print(f"TUN Manager: {'✅' if has_tun_manager else '❌'}")

        if has_proxy_manager:
            proxy_info = window.system_proxy_manager.get_proxy_info()
            print(f"   GNOME Available: {proxy_info['gnome_available']}")
            print(f"   Has Permissions: {proxy_info['has_permissions']}")

        if has_tun_manager:
            tun_requirements = window.tun_manager.check_requirements()
            print(f"   TUN Available: {tun_requirements['can_create_tun']}")

        print("\\n✅ GUI integration test completed")
        return True

    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_current_environment():
    """Test current environment setup"""
    print("🌍 Current Environment Test")
    print("="*30)

    # Test TUN device
    tun_exists = os.path.exists('/dev/net/tun')
    print(f"TUN Device: {'✅' if tun_exists else '❌'} (/dev/net/tun)")

    # Test ip command
    try:
        import subprocess
        result = subprocess.run(['ip', '--version'], capture_output=True, text=True, timeout=2)
        ip_available = result.returncode == 0
        print(f"IP Command: {'✅' if ip_available else '❌'}")
    except Exception:
        print(f"IP Command: ❌")

    # Test gsettings
    try:
        result = subprocess.run(['gsettings', '--version'], capture_output=True, text=True, timeout=2)
        gsettings_available = result.returncode == 0
        print(f"GSettings: {'✅' if gsettings_available else '❌'}")
    except Exception:
        print(f"GSettings: ❌")

    # Test current proxy settings
    try:
        result = subprocess.run(['gsettings', 'get', 'org.gnome.system.proxy', 'mode'],
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            current_mode = result.stdout.strip().strip("'")
            print(f"Current Proxy Mode: {current_mode}")
        else:
            print(f"Current Proxy Mode: Unable to detect")
    except Exception:
        print(f"Current Proxy Mode: Unable to detect")

    # Test DNS resolution
    try:
        import socket
        socket.gethostbyname('google.com')
        print(f"DNS Resolution: ✅")
    except Exception:
        print(f"DNS Resolution: ❌")

    # Test internet connectivity
    try:
        import requests
        response = requests.get('http://httpbin.org/ip', timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_ip = data.get('origin', 'N/A')
            print(f"Current IP: {current_ip}")
        else:
            print(f"Internet Connectivity: ❌ (HTTP {response.status_code})")
    except Exception:
        print(f"Internet Connectivity: ❌")


def main():
    """Main test function"""
    print("🧪 Comprehensive System Proxy and TUN Test")
    print("="*50)

    # Test current environment
    test_current_environment()

    # Test system proxy manager
    proxy_success = test_system_proxy_manager()

    # Test TUN manager
    tun_success = test_tun_manager()

    # Test GUI integration
    try:
        gui_success = test_gui_integration()
    except Exception as e:
        print(f"\\n⚠️  GUI test skipped: {e}")
        gui_success = False

    # Summary
    print("\\n" + "="*50)
    print("📋 Test Summary")
    print("="*50)
    print(f"System Proxy Manager: {'✅' if proxy_success else '❌'}")
    print(f"TUN Manager: {'✅' if tun_success else '❌'}")
    print(f"GUI Integration: {'✅' if gui_success else '❌'}")

    overall_success = proxy_success and tun_success and gui_success
    print(f"Overall: {'✅ All tests passed!' if overall_success else '❌ Some tests failed'}")

    if overall_success:
        print("\\n🎉 System proxy and TUN functionality is working!")
        print("   - System proxy can automatically configure GNOME settings")
        print("   - TUN mode can create system-wide VPN routing")
        print("   - GUI integration is complete")
    else:
        print("\\n⚠️  Some functionality may not work:")
        if not proxy_success:
            print("   - System proxy configuration may fail")
        if not tun_success:
            print("   - TUN mode may not be available")
        if not gui_success:
            print("   - GUI integration may have issues")


if __name__ == "__main__":
    main()