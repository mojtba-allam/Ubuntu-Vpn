"""
Icon loading utility for the V2Ray Client application.
Provides functions to load icons with fallback support.
"""

import os
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize

# Base directory for icons
ICONS_DIR = Path(__file__).parent / "icons"
APP_ICONS_DIR = ICONS_DIR / "app"
FLAG_ICONS_DIR = ICONS_DIR / "flags"
STATUS_ICONS_DIR = ICONS_DIR / "status"


class IconLoader:
    """Utility class for loading application icons with fallback support."""
    
    _cache = {}  # Cache loaded icons to improve performance
    
    @staticmethod
    def get_app_icon(size: int = 128) -> QIcon:
        """
        Load the main application icon.
        
        Args:
            size: Desired icon size (16, 32, 48, 64, 128, 256, 512)
        
        Returns:
            QIcon object with the application icon
        """
        cache_key = f"app_{size}"
        if cache_key in IconLoader._cache:
            return IconLoader._cache[cache_key]
        
        # Try to load PNG of requested size
        icon_path = APP_ICONS_DIR / f"v2ray-client-{size}.png"
        if not icon_path.exists():
            # Fall back to SVG
            icon_path = APP_ICONS_DIR / "v2ray-client.svg"
        
        if not icon_path.exists():
            # Fall back to default PNG
            icon_path = APP_ICONS_DIR / "v2ray-client.png"
        
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
        IconLoader._cache[cache_key] = icon
        return icon
    
    @staticmethod
    def get_flag_icon(country_code: str, size: int = 48) -> QPixmap:
        """
        Load a country flag icon.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'SG')
            size: Desired icon size in pixels
        
        Returns:
            QPixmap object with the flag icon, or fallback icon if not found
        """
        cache_key = f"flag_{country_code}_{size}"
        if cache_key in IconLoader._cache:
            return IconLoader._cache[cache_key]
        
        # Normalize country code to uppercase
        country_code = country_code.upper()
        
        # Try to load the flag
        flag_path = FLAG_ICONS_DIR / f"{country_code}.png"
        
        if not flag_path.exists():
            # Try fallback flag
            flag_path = FLAG_ICONS_DIR / "UNKNOWN.png"
            if not flag_path.exists():
                flag_path = FLAG_ICONS_DIR / "UNKNOWN.svg"
        
        if flag_path.exists():
            pixmap = QPixmap(str(flag_path))
            if size != 48:  # Scale if different size requested
                pixmap = pixmap.scaled(
                    QSize(size, int(size * 0.75)),  # Maintain 4:3 aspect ratio
                    aspectRatioMode=1  # Qt.KeepAspectRatio
                )
        else:
            # Create empty pixmap as last resort
            pixmap = QPixmap(size, int(size * 0.75))
            pixmap.fill()
        
        IconLoader._cache[cache_key] = pixmap
        return pixmap
    
    @staticmethod
    def get_status_icon(status: str, size: int = 64) -> QIcon:
        """
        Load a connection status icon.
        
        Args:
            status: Status type ('connected', 'disconnected', 'connecting')
            size: Desired icon size in pixels
        
        Returns:
            QIcon object with the status icon
        """
        cache_key = f"status_{status}_{size}"
        if cache_key in IconLoader._cache:
            return IconLoader._cache[cache_key]
        
        # Normalize status name
        status = status.lower()
        
        # Try PNG first, then SVG
        icon_path = STATUS_ICONS_DIR / f"{status}.png"
        if not icon_path.exists():
            icon_path = STATUS_ICONS_DIR / f"{status}.svg"
        
        if not icon_path.exists():
            # Fall back to disconnected icon
            icon_path = STATUS_ICONS_DIR / "disconnected.png"
            if not icon_path.exists():
                icon_path = STATUS_ICONS_DIR / "disconnected.svg"
        
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
        IconLoader._cache[cache_key] = icon
        return icon
    
    @staticmethod
    def get_status_pixmap(status: str, size: int = 64) -> QPixmap:
        """
        Load a connection status icon as a pixmap.
        
        Args:
            status: Status type ('connected', 'disconnected', 'connecting')
            size: Desired icon size in pixels
        
        Returns:
            QPixmap object with the status icon
        """
        icon = IconLoader.get_status_icon(status, size)
        return icon.pixmap(QSize(size, size))
    
    @staticmethod
    def clear_cache():
        """Clear the icon cache to free memory."""
        IconLoader._cache.clear()
    
    @staticmethod
    def preload_common_icons():
        """Preload commonly used icons to improve initial performance."""
        # Preload app icon
        IconLoader.get_app_icon(128)
        
        # Preload status icons
        for status in ['connected', 'disconnected', 'connecting']:
            IconLoader.get_status_icon(status)
        
        # Preload common country flags
        common_countries = ['US', 'GB', 'CA', 'DE', 'FR', 'NL', 'SG', 'JP', 'HK']
        for country in common_countries:
            IconLoader.get_flag_icon(country)


# Convenience functions for backward compatibility
def get_app_icon(size: int = 128) -> QIcon:
    """Get the main application icon."""
    return IconLoader.get_app_icon(size)


def get_flag_icon(country_code: str, size: int = 48) -> QPixmap:
    """Get a country flag icon."""
    return IconLoader.get_flag_icon(country_code, size)


def get_status_icon(status: str, size: int = 64) -> QIcon:
    """Get a connection status icon."""
    return IconLoader.get_status_icon(status, size)


def get_status_pixmap(status: str, size: int = 64) -> QPixmap:
    """Get a connection status icon as pixmap."""
    return IconLoader.get_status_pixmap(status, size)
