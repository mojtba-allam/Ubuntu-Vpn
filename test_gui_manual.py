#!/usr/bin/env python3
"""
Manual GUI test script for Servers Tab

Run this to visually test the servers tab implementation.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Launch the application for manual testing."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Add some test servers for demonstration
    test_servers = [
        {
            "name": "USA Server 1",
            "type": "vmess",
            "ip": "45.67.89.10",
            "port": 443,
            "uuid": "test-uuid-1",
            "ping": 92,
            "country_code": "us"
        },
        {
            "name": "Singapore Server",
            "type": "vless",
            "ip": "103.145.67.89",
            "port": 8443,
            "uuid": "test-uuid-2",
            "ping": 45,
            "country_code": "sg"
        },
        {
            "name": "Germany Server",
            "type": "trojan",
            "ip": "88.99.10.20",
            "port": 443,
            "uuid": "test-uuid-3",
            "ping": 120,
            "country_code": "de"
        },
        {
            "name": "Japan Server",
            "type": "vmess",
            "ip": "150.95.10.20",
            "port": 443,
            "uuid": "test-uuid-4",
            "ping": 78,
            "country_code": "jp"
        },
        {
            "name": "UK Server",
            "type": "vless",
            "ip": "185.220.101.50",
            "port": 443,
            "uuid": "test-uuid-5",
            "ping": 105,
            "country_code": "gb"
        },
        {
            "name": "Canada Server",
            "type": "trojan",
            "ip": "142.44.215.177",
            "port": 443,
            "uuid": "test-uuid-6",
            "ping": 88,
            "country_code": "ca"
        }
    ]
    
    # Update servers tab with test data
    window.servers_tab.update_servers(test_servers)
    
    # Show welcome toast
    window.show_toast("Welcome to V2Ray Client!", "info")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
