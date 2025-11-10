#!/usr/bin/env python3
"""
Script to create PNG versions of the application icon in various sizes.
"""

import os
import subprocess

def create_png_from_svg(svg_path, png_path, size):
    """Convert SVG to PNG using available tools."""
    # Try using cairosvg (Python library)
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
        print(f"Created {png_path} ({size}x{size}) using cairosvg")
        return True
    except ImportError:
        pass
    
    # Try using inkscape
    try:
        result = subprocess.run(
            ['inkscape', svg_path, '--export-filename', png_path, 
             f'--export-width={size}', f'--export-height={size}'],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"Created {png_path} ({size}x{size}) using inkscape")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try using ImageMagick (convert)
    try:
        result = subprocess.run(
            ['convert', '-background', 'none', '-resize', f'{size}x{size}', 
             svg_path, png_path],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"Created {png_path} ({size}x{size}) using ImageMagick")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try using rsvg-convert
    try:
        result = subprocess.run(
            ['rsvg-convert', '-w', str(size), '-h', str(size), 
             svg_path, '-o', png_path],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"Created {png_path} ({size}x{size}) using rsvg-convert")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print(f"Could not create {png_path} - no SVG converter available")
    print("Install one of: cairosvg (pip), inkscape, imagemagick, or librsvg")
    return False

def create_simple_png_fallback(png_path, size):
    """Create a simple PNG icon using PIL as fallback."""
    try:
        from PIL import Image, ImageDraw
        
        # Create image with gradient-like effect
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw circle background with gradient approximation
        center = size // 2
        radius = int(size * 0.9 / 2)
        
        # Draw filled circle
        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            fill=(106, 17, 203, 255)  # Purple color from gradient
        )
        
        # Draw V shape
        v_width = int(size * 0.15)
        v_top = int(size * 0.3)
        v_bottom = int(size * 0.7)
        v_left = int(size * 0.35)
        v_right = int(size * 0.65)
        
        # Simple V using lines (approximation)
        draw.line([v_left, v_top, center, v_bottom], fill='white', width=v_width)
        draw.line([center, v_bottom, v_right, v_top], fill='white', width=v_width)
        
        img.save(png_path)
        print(f"Created {png_path} ({size}x{size}) using PIL fallback")
        return True
    except ImportError:
        print(f"Could not create {png_path} - PIL not available")
        return False

def main():
    """Main function to create PNG icons."""
    svg_path = 'ui/icons/app/v2ray-client.svg'
    app_icons_dir = 'ui/icons/app'
    
    # Icon sizes needed
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    print("Creating PNG icons from SVG...")
    print("=" * 60)
    
    success_count = 0
    
    for size in sizes:
        png_path = os.path.join(app_icons_dir, f'v2ray-client-{size}.png')
        
        # Try SVG conversion first
        if create_png_from_svg(svg_path, png_path, size):
            success_count += 1
        # Fall back to PIL if available
        elif create_simple_png_fallback(png_path, size):
            success_count += 1
    
    print("=" * 60)
    print(f"Created {success_count}/{len(sizes)} PNG icons")
    
    # Create a default symlink/copy for the main icon
    main_icon_path = os.path.join(app_icons_dir, 'v2ray-client.png')
    source_icon = os.path.join(app_icons_dir, 'v2ray-client-128.png')
    
    if os.path.exists(source_icon):
        try:
            if os.path.exists(main_icon_path):
                os.remove(main_icon_path)
            os.symlink('v2ray-client-128.png', main_icon_path)
            print(f"\nCreated symlink: v2ray-client.png -> v2ray-client-128.png")
        except OSError:
            # Symlink failed, try copy
            import shutil
            shutil.copy(source_icon, main_icon_path)
            print(f"\nCopied v2ray-client-128.png to v2ray-client.png")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
