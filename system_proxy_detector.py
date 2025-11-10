"""
System Proxy Detector

Detects system proxy settings to allow V2Ray to connect through existing VPN.
"""

import os
import subprocess
import re


def get_system_proxy():
    """
    Detect system proxy settings.
    
    Returns:
        dict: Proxy settings with 'protocol', 'host', 'port' or None if no proxy
    """
    print("\n🔍 Detecting system proxy settings...")
    
    # Method 1: Check GNOME/Ubuntu system settings
    try:
        mode = subprocess.check_output(
            ['gsettings', 'get', 'org.gnome.system.proxy', 'mode'],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip().strip("'")
        
        if mode == 'manual':
            # Check SOCKS proxy
            socks_host = subprocess.check_output(
                ['gsettings', 'get', 'org.gnome.system.proxy.socks', 'host'],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip().strip("'")
            
            socks_port = subprocess.check_output(
                ['gsettings', 'get', 'org.gnome.system.proxy.socks', 'port'],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            
            if socks_host and socks_port and socks_host != "''":
                print(f"✅ Found GNOME SOCKS proxy: {socks_host}:{socks_port}")
                return {
                    'protocol': 'socks',
                    'host': socks_host,
                    'port': int(socks_port)
                }
            
            # Check HTTP proxy
            http_host = subprocess.check_output(
                ['gsettings', 'get', 'org.gnome.system.proxy.http', 'host'],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip().strip("'")
            
            http_port = subprocess.check_output(
                ['gsettings', 'get', 'org.gnome.system.proxy.http', 'port'],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            
            if http_host and http_port and http_host != "''":
                print(f"✅ Found GNOME HTTP proxy: {http_host}:{http_port}")
                return {
                    'protocol': 'http',
                    'host': http_host,
                    'port': int(http_port)
                }
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Method 2: Check environment variables
    for var in ['ALL_PROXY', 'all_proxy']:
        proxy = os.environ.get(var)
        if proxy:
            parsed = parse_proxy_url(proxy)
            if parsed:
                print(f"✅ Found proxy in {var}: {parsed['protocol']}://{parsed['host']}:{parsed['port']}")
                return parsed
    
    for var in ['HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy']:
        proxy = os.environ.get(var)
        if proxy:
            parsed = parse_proxy_url(proxy)
            if parsed:
                print(f"✅ Found proxy in {var}: {parsed['protocol']}://{parsed['host']}:{parsed['port']}")
                return parsed
    
    # Method 3: Check for common VPN proxy ports
    common_ports = [
        ('127.0.0.1', 1080, 'socks'),   # Common SOCKS port
        ('127.0.0.1', 1081, 'socks'),
        ('127.0.0.1', 7890, 'socks'),   # Clash
        ('127.0.0.1', 7891, 'http'),    # Clash HTTP
        ('127.0.0.1', 10808, 'socks'),  # v2rayN
        ('127.0.0.1', 10809, 'http'),   # v2rayN HTTP
    ]
    
    for host, port, protocol in common_ports:
        if is_port_listening(host, port):
            print(f"✅ Found active proxy on {host}:{port} ({protocol})")
            return {
                'protocol': protocol,
                'host': host,
                'port': port
            }
    
    print("ℹ️  No system proxy detected")
    return None


def parse_proxy_url(url):
    """
    Parse proxy URL like socks5://127.0.0.1:1080 or http://proxy:8080
    
    Args:
        url: Proxy URL string
        
    Returns:
        dict: Parsed proxy settings or None
    """
    # Match protocol://host:port
    match = re.match(r'(socks[45]?|http|https)://([^:]+):(\d+)', url)
    if match:
        protocol = match.group(1)
        if protocol.startswith('socks'):
            protocol = 'socks'
        elif protocol in ['http', 'https']:
            protocol = 'http'
        
        return {
            'protocol': protocol,
            'host': match.group(2),
            'port': int(match.group(3))
        }
    
    return None


def is_port_listening(host, port):
    """
    Check if a port is listening.
    
    Args:
        host: Host address
        port: Port number
        
    Returns:
        bool: True if port is listening
    """
    try:
        # Use ss or netstat to check
        result = subprocess.run(
            ['ss', '-tuln'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            # Look for the port in output
            return f":{port}" in result.stdout
        
        # Fallback to netstat
        result = subprocess.run(
            ['netstat', '-tuln'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            return f":{port}" in result.stdout
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return False


def add_system_proxy_to_config(config, system_proxy):
    """
    Add system proxy as outbound proxy to V2Ray config.
    
    This creates a proxy chain: V2Ray -> System Proxy -> Internet
    
    Args:
        config: V2Ray configuration dict
        system_proxy: System proxy settings dict
        
    Returns:
        dict: Updated configuration
    """
    if not system_proxy:
        return config
    
    # Check if system proxy port conflicts with our inbound ports
    inbound_ports = []
    if 'inbounds' in config:
        inbound_ports = [ib.get('port') for ib in config['inbounds'] if 'port' in ib]
    
    if system_proxy['port'] in inbound_ports:
        print(f"\n⚠️  System proxy port {system_proxy['port']} conflicts with inbound port")
        print(f"   Skipping system proxy to avoid circular routing")
        return config
    
    print(f"\n🔗 Configuring V2Ray to use system proxy:")
    print(f"   Protocol: {system_proxy['protocol']}")
    print(f"   Address: {system_proxy['host']}:{system_proxy['port']}")
    
    # Create proxy outbound
    proxy_outbound = {
        "tag": "system-proxy",
        "protocol": system_proxy['protocol'],
        "settings": {}
    }
    
    if system_proxy['protocol'] == 'socks':
        proxy_outbound['settings'] = {
            "servers": [{
                "address": system_proxy['host'],
                "port": system_proxy['port']
            }]
        }
    elif system_proxy['protocol'] == 'http':
        proxy_outbound['settings'] = {
            "servers": [{
                "address": system_proxy['host'],
                "port": system_proxy['port']
            }]
        }
    
    # Add proxy outbound to config
    if 'outbounds' not in config:
        config['outbounds'] = []
    
    # Insert system proxy as second outbound (after main server)
    if len(config['outbounds']) > 0:
        config['outbounds'].insert(1, proxy_outbound)
    else:
        config['outbounds'].append(proxy_outbound)
    
    # Add routing to use system proxy for the main server connection
    if 'routing' not in config:
        config['routing'] = {
            "domainStrategy": "AsIs",
            "rules": []
        }
    
    # Route the V2Ray server connection through system proxy
    config['routing']['rules'].insert(0, {
        "type": "field",
        "outboundTag": "system-proxy",
        "domain": ["geosite:category-ads-all"],  # Block ads
        "inboundTag": []
    })
    
    # Make the main outbound use system proxy
    if len(config['outbounds']) > 0:
        main_outbound = config['outbounds'][0]
        main_outbound['proxySettings'] = {
            "tag": "system-proxy"
        }
    
    print("✅ System proxy configured in V2Ray chain")
    
    return config
