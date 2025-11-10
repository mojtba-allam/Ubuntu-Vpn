#!/usr/bin/env python3
"""
Visual test for icon loading - displays all icons in a window.
Run this to verify icons are loading correctly.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt
from ui.icon_loader import IconLoader

class IconTestWindow(QMainWindow):
    """Window to display all loaded icons for visual verification."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("V2Ray Client - Icon Test")
        self.setGeometry(100, 100, 900, 700)
        
        # Set app icon
        self.setWindowIcon(IconLoader.get_app_icon(64))
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Add sections
        scroll_layout.addWidget(self.create_app_icons_section())
        scroll_layout.addWidget(self.create_status_icons_section())
        scroll_layout.addWidget(self.create_flag_icons_section())
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
    
    def create_app_icons_section(self):
        """Create section showing app icons."""
        group = QGroupBox("Application Icons")
        layout = QHBoxLayout()
        
        sizes = [16, 32, 48, 64, 128]
        for size in sizes:
            icon_label = QLabel()
            icon_label.setPixmap(IconLoader.get_app_icon(size).pixmap(size, size))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            text_label = QLabel(f"{size}x{size}")
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addWidget(icon_label)
            container_layout.addWidget(text_label)
            
            layout.addWidget(container)
        
        group.setLayout(layout)
        return group
    
    def create_status_icons_section(self):
        """Create section showing status icons."""
        group = QGroupBox("Status Icons")
        layout = QHBoxLayout()
        
        statuses = [
            ('connected', 'Connected'),
            ('disconnected', 'Disconnected'),
            ('connecting', 'Connecting')
        ]
        
        for status, label_text in statuses:
            icon_label = QLabel()
            icon_label.setPixmap(IconLoader.get_status_pixmap(status, 64))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            text_label = QLabel(label_text)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addWidget(icon_label)
            container_layout.addWidget(text_label)
            
            layout.addWidget(container)
        
        group.setLayout(layout)
        return group
    
    def create_flag_icons_section(self):
        """Create section showing flag icons."""
        group = QGroupBox("Country Flag Icons (Sample)")
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Show a sample of flags
        countries = [
            ('US', 'USA'),
            ('GB', 'UK'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('JP', 'Japan'),
            ('SG', 'Singapore'),
            ('CA', 'Canada'),
            ('AU', 'Australia'),
            ('NL', 'Netherlands'),
            ('HK', 'Hong Kong')
        ]
        
        for code, name in countries:
            icon_label = QLabel()
            icon_label.setPixmap(IconLoader.get_flag_icon(code, 48))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            text_label = QLabel(name)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setStyleSheet("font-size: 10px;")
            
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addWidget(icon_label)
            container_layout.addWidget(text_label)
            container_layout.setSpacing(2)
            
            layout.addWidget(container)
        
        group.setLayout(layout)
        return group

def main():
    """Run the visual icon test."""
    app = QApplication(sys.argv)
    
    # Preload icons
    print("Preloading common icons...")
    IconLoader.preload_common_icons()
    print(f"Cache size: {len(IconLoader._cache)} icons")
    
    window = IconTestWindow()
    window.show()
    
    print("\nIcon test window opened.")
    print("Close the window to exit.")
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
