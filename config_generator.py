"""
V2Ray Configuration Generator

Converts server information to V2Ray configuration JSON.
"""

from typing import Dict
from system_proxy_detector import get_system_proxy, add_system_proxy_to_config


def generate_v2ray_config(server: Dict, use_system_proxy: bool = True) -> Dict:
    """
    Generate V2Ray configuration from server information.
    
    Args:
        server: Server configuration dictionary
        
    Returns:
        V2Ray configuration dictionary
    """
    server_type = server.get("type", "vmess")
    
    print(f"\n⚙️  Generating V2Ray config for {server_type.upper()} server")
    print(f"   Server: {server.get('name', 'Unknown')}")
    print(f"   Address: {server.get('ip', 'Unknown')}:{server.get('port', 'Unknown')}")
    print(f"   Network: {server.get('network', 'tcp')}")
    print(f"   TLS: {server.get('tls', False)}")
    
    if server_type == "vmess":
        config = generate_vmess_config(server)
    elif server_type == "vless":
        config = generate_vless_config(server)
    elif server_type == "trojan":
        config = generate_trojan_config(server)
    else:
        error_msg = f"Unsupported server type: {server_type}"
        print(f"❌ ERROR: {error_msg}")
        raise ValueError(error_msg)
    
    print("✅ Config generated successfully")
    
    # Add system proxy if requested and available
    if use_system_proxy:
        system_proxy = get_system_proxy()
        if system_proxy:
            config = add_system_proxy_to_config(config, system_proxy)
        else:
            print("ℹ️  No system proxy found - connecting directly")
    
    return config


def generate_vmess_config(server: Dict) -> Dict:
    """Generate VMess configuration"""
    # Get network type and convert xhttp to ws for compatibility
    network = server.get("network", "tcp")
    
    # xhttp and httpupgrade are newer transports not supported in all V2Ray versions
    # Convert to WebSocket (ws) for compatibility
    if network in ["xhttp", "httpupgrade"]:
        print(f"   ⚠️  Converting {network} to ws (WebSocket) for compatibility")
        network = "ws"
    
    config = {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": 1080,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True
                }
            },
            {
                "port": 1081,
                "protocol": "http"
            }
        ],
        "outbounds": [
            {
                "protocol": "vmess",
                "settings": {
                    "vnext": [
                        {
                            "address": server.get("ip", ""),
                            "port": server.get("port", 443),
                            "users": [
                                {
                                    "id": server.get("uuid", ""),
                                    "alterId": server.get("alterId", 0),
                                    "security": server.get("security", "auto")
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": network
                }
            }
        ]
    }
    
    # Add TLS if enabled
    if server.get("tls", False):
        config["outbounds"][0]["streamSettings"]["security"] = "tls"
        config["outbounds"][0]["streamSettings"]["tlsSettings"] = {
            "allowInsecure": False
        }
        
        # Use server IP as SNI if sni not specified
        sni = server.get("sni") or server.get("ip")
        if sni:
            config["outbounds"][0]["streamSettings"]["tlsSettings"]["serverName"] = sni
    
    # Add network-specific settings
    if network == "ws":
        ws_settings = {
            "path": server.get("path", "/")
        }
        # Add host header if available
        if server.get("ip"):
            ws_settings["headers"] = {
                "Host": server.get("ip")
            }
        config["outbounds"][0]["streamSettings"]["wsSettings"] = ws_settings
    elif network == "h2":
        config["outbounds"][0]["streamSettings"]["httpSettings"] = {
            "path": server.get("path", "/"),
            "host": [server.get("ip", "")]
        }
    elif network == "grpc":
        config["outbounds"][0]["streamSettings"]["grpcSettings"] = {
            "serviceName": server.get("path", "")
        }
    
    return config


def generate_vless_config(server: Dict) -> Dict:
    """Generate VLess configuration"""
    # Get network type and convert xhttp to ws for compatibility
    network = server.get("network", "tcp")
    
    # xhttp and httpupgrade are newer transports not supported in all V2Ray versions
    # Convert to WebSocket (ws) for compatibility
    if network in ["xhttp", "httpupgrade"]:
        print(f"   ⚠️  Converting {network} to ws (WebSocket) for compatibility")
        network = "ws"
    
    config = {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": 1080,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True
                }
            },
            {
                "port": 1081,
                "protocol": "http"
            }
        ],
        "outbounds": [
            {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": server.get("ip", ""),
                            "port": server.get("port", 443),
                            "users": [
                                {
                                    "id": server.get("uuid", ""),
                                    "encryption": "none"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": network
                }
            }
        ]
    }
    
    # Add TLS if enabled
    if server.get("tls", False):
        config["outbounds"][0]["streamSettings"]["security"] = "tls"
        config["outbounds"][0]["streamSettings"]["tlsSettings"] = {
            "allowInsecure": False
        }
        
        # Use server IP as SNI if sni not specified
        sni = server.get("sni") or server.get("ip")
        if sni:
            config["outbounds"][0]["streamSettings"]["tlsSettings"]["serverName"] = sni
    
    # Add network-specific settings
    if network == "ws":
        ws_settings = {
            "path": server.get("path", "/")
        }
        # Add host header if available
        if server.get("ip"):
            ws_settings["headers"] = {
                "Host": server.get("ip")
            }
        config["outbounds"][0]["streamSettings"]["wsSettings"] = ws_settings
    elif network == "h2":
        config["outbounds"][0]["streamSettings"]["httpSettings"] = {
            "path": server.get("path", "/"),
            "host": [server.get("ip", "")]
        }
    elif network == "grpc":
        config["outbounds"][0]["streamSettings"]["grpcSettings"] = {
            "serviceName": server.get("path", "")
        }
    
    return config


def generate_trojan_config(server: Dict) -> Dict:
    """Generate Trojan configuration"""
    # Get network type and convert xhttp to ws for compatibility
    network = server.get("network", "tcp")
    
    # xhttp and httpupgrade are newer transports not supported in all V2Ray versions
    # Convert to WebSocket (ws) for compatibility
    if network in ["xhttp", "httpupgrade"]:
        print(f"   ⚠️  Converting {network} to ws (WebSocket) for compatibility")
        network = "ws"
    
    config = {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": 1080,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True
                }
            },
            {
                "port": 1081,
                "protocol": "http"
            }
        ],
        "outbounds": [
            {
                "protocol": "trojan",
                "settings": {
                    "servers": [
                        {
                            "address": server.get("ip", ""),
                            "port": server.get("port", 443),
                            "password": server.get("uuid", "")
                        }
                    ]
                },
                "streamSettings": {
                    "network": network,
                    "security": "tls",
                    "tlsSettings": {
                        "allowInsecure": False
                    }
                }
            }
        ]
    }
    
    # Add SNI - use server IP if sni not specified
    sni = server.get("sni") or server.get("ip")
    if sni:
        config["outbounds"][0]["streamSettings"]["tlsSettings"]["serverName"] = sni
    
    # Add network-specific settings
    if network == "ws":
        ws_settings = {
            "path": server.get("path", "/")
        }
        # Add host header if available
        if server.get("ip"):
            ws_settings["headers"] = {
                "Host": server.get("ip")
            }
        config["outbounds"][0]["streamSettings"]["wsSettings"] = ws_settings
    elif network == "h2":
        config["outbounds"][0]["streamSettings"]["httpSettings"] = {
            "path": server.get("path", "/"),
            "host": [server.get("ip", "")]
        }
    elif network == "grpc":
        config["outbounds"][0]["streamSettings"]["grpcSettings"] = {
            "serviceName": server.get("path", "")
        }
    
    return config
