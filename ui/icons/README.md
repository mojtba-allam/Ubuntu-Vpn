# Icons Directory

This directory contains all icon assets for the V2Ray Client application.

## Directory Structure

```
ui/icons/
├── app/          # Application icons
├── flags/        # Country flag icons
├── status/       # Connection status icons
└── README.md     # This file
```

## Application Icons (`app/`)

Main application icons in various sizes:

- `v2ray-client.svg` - Vector source (128x128)
- `v2ray-client-16.png` - 16x16 pixels
- `v2ray-client-32.png` - 32x32 pixels
- `v2ray-client-48.png` - 48x48 pixels
- `v2ray-client-64.png` - 64x64 pixels
- `v2ray-client-128.png` - 128x128 pixels
- `v2ray-client-256.png` - 256x256 pixels
- `v2ray-client-512.png` - 512x512 pixels
- `v2ray-client.png` - Symlink to 128px version

### Usage

```python
from ui.icon_loader import get_app_icon

# Get app icon at specific size
icon = get_app_icon(128)
window.setWindowIcon(icon)
```

## Country Flags (`flags/`)

Country flag icons in PNG format (48x36 pixels, 4:3 aspect ratio).

### Available Countries

45 country flags are included for common VPN server locations:
- US, GB, CA, DE, FR, NL, SG, JP, KR, HK, TW, AU, IN, BR, RU, IT, ES, SE, CH, NO, FI, DK, PL, TR, AE, IL, ZA, MX, AR, CL, TH, VN, ID, MY, PH, NZ, AT, BE, CZ, IE, PT, RO, UA, GR, BG

### Fallback

- `UNKNOWN.svg` - Fallback icon for unknown/missing country codes

### Usage

```python
from ui.icon_loader import get_flag_icon

# Get flag for a country code
flag_pixmap = get_flag_icon('US')  # Returns QPixmap
label.setPixmap(flag_pixmap)

# With custom size
flag_pixmap = get_flag_icon('SG', size=64)
```

## Status Icons (`status/`)

Connection status indicators in both SVG and PNG formats (64x64 pixels).

### Available Icons

- `connected.svg/png` - Green checkmark (successful connection)
- `disconnected.svg/png` - Red X (no connection)
- `connecting.svg/png` - Blue spinner (connection in progress)

### Usage

```python
from ui.icon_loader import get_status_icon, get_status_pixmap

# Get as QIcon
icon = get_status_icon('connected')
button.setIcon(icon)

# Get as QPixmap
pixmap = get_status_pixmap('disconnected')
label.setPixmap(pixmap)
```

## Icon Loader API

The `ui/icon_loader.py` module provides a unified interface for loading all icons with automatic fallback support.

### Key Features

- **Caching**: Icons are cached after first load for better performance
- **Fallback**: Automatically falls back to alternative formats or default icons
- **Preloading**: Can preload common icons at startup
- **Type Safety**: Returns appropriate Qt types (QIcon, QPixmap)

### IconLoader Class

```python
from ui.icon_loader import IconLoader

# Load icons
app_icon = IconLoader.get_app_icon(size=128)
flag = IconLoader.get_flag_icon('US', size=48)
status = IconLoader.get_status_icon('connected', size=64)

# Cache management
IconLoader.clear_cache()  # Clear all cached icons
IconLoader.preload_common_icons()  # Preload frequently used icons
```

### Convenience Functions

```python
from ui.icon_loader import get_app_icon, get_flag_icon, get_status_icon

# Simpler imports for common use cases
icon = get_app_icon()
flag = get_flag_icon('JP')
status = get_status_icon('connecting')
```

## Regenerating Icons

### Application Icons

To regenerate PNG versions from SVG:

```bash
python create_app_icons.py
```

Requires: `cairosvg` or `inkscape` or `imagemagick` or `librsvg`

### Status Icons

To regenerate status icon PNGs:

```bash
python create_status_icons.py
```

Requires: `cairosvg`

### Country Flags

To re-download country flags:

```bash
python download_flags.py
```

Downloads from: https://flagcdn.com (free CDN)

## Adding New Icons

### Adding a New Country Flag

1. Download the flag PNG (48x36) to `ui/icons/flags/`
2. Name it with the ISO 3166-1 alpha-2 code (e.g., `XX.png`)
3. The icon loader will automatically find and use it

### Adding a New Status Icon

1. Create SVG in `ui/icons/status/` (64x64 viewBox)
2. Generate PNG: `cairosvg status_name.svg -o status_name.png -W 64 -H 64`
3. Use via `get_status_icon('status_name')`

### Adding a New App Icon Size

1. Edit `create_app_icons.py` to include the new size
2. Run the script to generate the PNG
3. The icon loader will automatically find it

## Icon Sources

- **Application Icon**: Custom design (gradient V with network nodes)
- **Status Icons**: Custom SVG designs
- **Country Flags**: https://flagcdn.com (public domain)

## License

- Application and status icons: Same as project license
- Country flags: Public domain (via flagcdn.com)
