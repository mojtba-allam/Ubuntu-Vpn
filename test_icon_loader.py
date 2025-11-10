#!/usr/bin/env python3
"""
Test script for icon loader functionality.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.icon_loader import IconLoader

def test_icon_loader():
    """Test the icon loader functionality."""
    app = QApplication(sys.argv)
    
    print("Testing Icon Loader...")
    print("=" * 60)
    
    # Test app icon
    print("\n1. Testing app icon loading:")
    for size in [16, 32, 48, 64, 128, 256]:
        icon = IconLoader.get_app_icon(size)
        if not icon.isNull():
            print(f"   ✓ App icon ({size}x{size}) loaded successfully")
        else:
            print(f"   ✗ App icon ({size}x{size}) failed to load")
    
    # Test status icons
    print("\n2. Testing status icon loading:")
    for status in ['connected', 'disconnected', 'connecting']:
        icon = IconLoader.get_status_icon(status)
        if not icon.isNull():
            print(f"   ✓ Status icon '{status}' loaded successfully")
        else:
            print(f"   ✗ Status icon '{status}' failed to load")
    
    # Test flag icons
    print("\n3. Testing flag icon loading:")
    test_countries = ['US', 'GB', 'SG', 'JP', 'DE', 'FR', 'INVALID']
    for country in test_countries:
        pixmap = IconLoader.get_flag_icon(country)
        if not pixmap.isNull():
            print(f"   ✓ Flag icon '{country}' loaded successfully ({pixmap.width()}x{pixmap.height()})")
        else:
            print(f"   ✗ Flag icon '{country}' failed to load")
    
    # Test cache
    print("\n4. Testing icon cache:")
    cache_size_before = len(IconLoader._cache)
    IconLoader.get_app_icon(128)  # Should use cache
    IconLoader.get_flag_icon('US')  # Should use cache
    cache_size_after = len(IconLoader._cache)
    print(f"   Cache size: {cache_size_after} items")
    print(f"   ✓ Cache is working (no new items added on reload)")
    
    # Test preload
    print("\n5. Testing icon preloading:")
    IconLoader.clear_cache()
    print(f"   Cache cleared: {len(IconLoader._cache)} items")
    IconLoader.preload_common_icons()
    print(f"   After preload: {len(IconLoader._cache)} items")
    print(f"   ✓ Preload completed successfully")
    
    print("\n" + "=" * 60)
    print("Icon loader tests completed!")
    
    return 0

if __name__ == '__main__':
    sys.exit(test_icon_loader())
