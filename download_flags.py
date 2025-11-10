#!/usr/bin/env python3
"""
Script to download country flag icons for the V2Ray client.
Uses the flagcdn.com API which provides free flag icons.
"""

import os
import urllib.request
import urllib.error

# Common countries for VPN servers
COUNTRIES = {
    'US': 'United States',
    'GB': 'United Kingdom',
    'CA': 'Canada',
    'DE': 'Germany',
    'FR': 'France',
    'NL': 'Netherlands',
    'SG': 'Singapore',
    'JP': 'Japan',
    'KR': 'South Korea',
    'HK': 'Hong Kong',
    'TW': 'Taiwan',
    'AU': 'Australia',
    'IN': 'India',
    'BR': 'Brazil',
    'RU': 'Russia',
    'IT': 'Italy',
    'ES': 'Spain',
    'SE': 'Sweden',
    'CH': 'Switzerland',
    'NO': 'Norway',
    'FI': 'Finland',
    'DK': 'Denmark',
    'PL': 'Poland',
    'TR': 'Turkey',
    'AE': 'United Arab Emirates',
    'IL': 'Israel',
    'ZA': 'South Africa',
    'MX': 'Mexico',
    'AR': 'Argentina',
    'CL': 'Chile',
    'TH': 'Thailand',
    'VN': 'Vietnam',
    'ID': 'Indonesia',
    'MY': 'Malaysia',
    'PH': 'Philippines',
    'NZ': 'New Zealand',
    'AT': 'Austria',
    'BE': 'Belgium',
    'CZ': 'Czech Republic',
    'IE': 'Ireland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'UA': 'Ukraine',
    'GR': 'Greece',
    'BG': 'Bulgaria',
}

def download_flag(country_code, output_dir):
    """Download flag icon for a country code."""
    country_code_lower = country_code.lower()
    url = f"https://flagcdn.com/48x36/{country_code_lower}.png"
    output_path = os.path.join(output_dir, f"{country_code}.png")
    
    try:
        print(f"Downloading {country_code} ({COUNTRIES.get(country_code, 'Unknown')})...", end=' ')
        urllib.request.urlretrieve(url, output_path)
        print("✓")
        return True
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}")
        return False

def create_fallback_flag(output_dir):
    """Create a fallback flag icon for unknown countries."""
    fallback_path = os.path.join(output_dir, "UNKNOWN.png")
    
    # Create a simple gray flag as fallback
    try:
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (48, 36), color='#cccccc')
        draw = ImageDraw.Draw(img)
        draw.text((12, 12), "?", fill='#666666')
        img.save(fallback_path)
        print("Created fallback flag icon")
        return True
    except ImportError:
        print("PIL not available, creating SVG fallback instead")
        # Create SVG fallback
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 36" width="48" height="36">
  <rect width="48" height="36" fill="#cccccc"/>
  <text x="24" y="24" font-size="20" text-anchor="middle" fill="#666666">?</text>
</svg>'''
        with open(fallback_path.replace('.png', '.svg'), 'w') as f:
            f.write(svg_content)
        return True

def main():
    """Main function to download all flags."""
    flags_dir = os.path.join('ui', 'icons', 'flags')
    
    # Ensure directory exists
    os.makedirs(flags_dir, exist_ok=True)
    
    print(f"Downloading flags to {flags_dir}...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for country_code in sorted(COUNTRIES.keys()):
        if download_flag(country_code, flags_dir):
            success_count += 1
        else:
            fail_count += 1
    
    print("=" * 60)
    print(f"Downloaded {success_count} flags successfully")
    if fail_count > 0:
        print(f"Failed to download {fail_count} flags")
    
    # Create fallback flag
    create_fallback_flag(flags_dir)
    
    print("\nDone!")

if __name__ == '__main__':
    main()
