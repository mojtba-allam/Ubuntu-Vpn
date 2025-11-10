#!/usr/bin/env python3
"""
Manual test for LogsTab widget.

This script creates a simple GUI to test the LogsTab functionality.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.logs_tab import LogsTab
from v2ray_manager import V2RayManager


def main():
    """Run the manual test."""
    app = QApplication(sys.argv)
    
    # Create V2RayManager instance
    manager = V2RayManager()
    
    # Create LogsTab
    logs_tab = LogsTab(manager)
    logs_tab.setWindowTitle("LogsTab Test")
    logs_tab.resize(800, 600)
    logs_tab.show()
    
    # Simulate some log messages
    logs_tab.append_log("2024-01-01 12:00:00 [Info] V2Ray starting...")
    logs_tab.append_log("2024-01-01 12:00:01 [Info] Loading configuration...")
    logs_tab.append_log("2024-01-01 12:00:02 [Info] Starting proxy server on port 1080")
    logs_tab.append_log("2024-01-01 12:00:03 [Info] Connection established")
    logs_tab.append_log("2024-01-01 12:00:04 [Warning] High latency detected: 250ms")
    logs_tab.append_log("2024-01-01 12:00:05 [Info] Data transfer: 1.2 MB sent, 3.4 MB received")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
