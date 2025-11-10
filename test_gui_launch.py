#!/usr/bin/env python3
"""
Test GUI Launch

Quick test to verify the GUI launches and shows servers.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow

def test_gui():
    """Test GUI launch"""
    print("\n" + "="*60)
    print("🧪 Testing GUI Launch")
    print("="*60)
    
    # Create application
    print("\n1. Creating QApplication...")
    app = QApplication(sys.argv)
    print("✅ QApplication created")
    
    # Create main window
    print("\n2. Creating MainWindow...")
    window = MainWindow()
    print("✅ MainWindow created")
    
    # Show window
    print("\n3. Showing window...")
    window.show()
    print("✅ Window shown")
    
    # Check servers tab
    print("\n4. Checking servers tab...")
    servers_tab = window.servers_tab
    print(f"   All servers count: {len(servers_tab.all_servers)}")
    print(f"   Server cards count: {len(servers_tab.server_cards)}")
    
    if servers_tab.all_servers:
        print("\n✅ Servers loaded:")
        for server in servers_tab.all_servers:
            print(f"   - {server.get('name', 'Unknown')}")
            print(f"     {server.get('ip', 'Unknown')}:{server.get('port', 'Unknown')}")
            print(f"     Network: {server.get('network', 'Unknown')}")
    else:
        print("\n⚠️  No servers loaded yet")
        print("   Servers will load after refresh...")
    
    # Trigger refresh to load servers
    print("\n5. Triggering server refresh...")
    window.server_updater.refresh_now()
    
    # Wait a bit for servers to load
    def check_after_refresh():
        print(f"\n6. After refresh:")
        print(f"   All servers count: {len(servers_tab.all_servers)}")
        print(f"   Server cards count: {len(servers_tab.server_cards)}")
        
        if servers_tab.all_servers:
            print("\n✅ SUCCESS: Servers are displayed!")
            for server in servers_tab.all_servers:
                print(f"   - {server.get('name', 'Unknown')}")
        else:
            print("\n⚠️  Still no servers")
            print("   Check if manual_servers.json exists")
        
        print("\n" + "="*60)
        print("GUI is running. Close the window to exit.")
        print("="*60 + "\n")
    
    # Check after 2 seconds
    QTimer.singleShot(2000, check_after_refresh)
    
    # Run application
    sys.exit(app.exec())

if __name__ == '__main__':
    test_gui()
