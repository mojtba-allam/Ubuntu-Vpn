#!/usr/bin/env python3
"""
V2Ray Client - Main Entry Point

Modern V2Ray VPN client for Ubuntu with PyQt6 GUI.
"""

import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow


# Application version
__version__ = "1.0.0"


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Modern V2Ray VPN Client for Ubuntu",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'V2Ray Client v{__version__}'
    )
    
    parser.add_argument(
        '--theme',
        type=str,
        choices=['dark', 'light', 'neon'],
        default=None,
        help='Initial theme to load (dark, light, or neon)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='~/.config/v2ray-client',
        help='Custom configuration directory path (default: ~/.config/v2ray-client)'
    )
    
    return parser.parse_args()


def main():
    """Main application entry point"""
    # Print startup banner
    print("\n" + "="*60)
    print("🚀 V2RAY CLIENT FOR UBUNTU")
    print(f"   Version: {__version__}")
    print("="*60 + "\n")
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Expand config directory path
    config_dir = os.path.expanduser(args.config)
    print(f"📁 Config directory: {config_dir}")
    
    # Create QApplication instance
    print("🎨 Initializing Qt application...")
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("V2Ray Client")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("V2Ray Client")
    
    # Create and configure main window
    window = MainWindow(config_dir=config_dir)
    
    # Apply theme from command-line if specified
    if args.theme:
        window.load_theme(args.theme)
    
    # Show main window
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
