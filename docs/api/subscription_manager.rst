subscription_manager module
===========================

.. automodule:: subscription_manager
   :members:
   :undoc-members:
   :show-inheritance:

The subscription_manager module handles fetching, parsing, and managing V2Ray server subscriptions.

Classes
-------

.. autoclass:: subscription_manager.SubscriptionManager
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   Manages subscription URLs and server lists.

   **Key Methods:**

   * :meth:`add_subscription` - Add new subscription URL
   * :meth:`remove_subscription` - Remove subscription URL
   * :meth:`fetch_subscription` - Fetch servers from URL
   * :meth:`fetch_all_subscriptions` - Fetch and merge all subscriptions
   * :meth:`get_subscriptions` - Get list of configured subscriptions

.. autoclass:: subscription_manager.ServerParser
   :members:
   :undoc-members:
   :show-inheritance:

   Parses different V2Ray server protocol formats.

   **Supported Protocols:**

   * VMess (vmess://)
   * VLess (vless://)
   * Trojan (trojan://)

   **Key Methods:**

   * :meth:`parse_vmess` - Parse vmess:// links
   * :meth:`parse_vless` - Parse vless:// links
   * :meth:`parse_trojan` - Parse trojan:// links
   * :meth:`deduplicate_servers` - Remove duplicate servers

Usage Example
-------------

.. code-block:: python

   from subscription_manager import SubscriptionManager

   # Initialize manager
   manager = SubscriptionManager()

   # Add a subscription
   manager.add_subscription(
       "https://example.com/subscription",
       "My Subscription"
   )

   # Fetch all servers
   servers = manager.fetch_all_subscriptions()
   
   for server in servers:
       print(f"{server['name']}: {server['ip']}:{server['port']}")

   # Remove a subscription
   manager.remove_subscription("https://example.com/subscription")

Server Configuration Format
---------------------------

Server configurations are dictionaries with the following structure:

.. code-block:: python

   {
       "name": str,           # Display name
       "type": str,           # Protocol: "vmess", "vless", "trojan"
       "ip": str,             # Server IP address
       "port": int,           # Server port
       "uuid": str,           # User ID
       "alterId": int,        # Alter ID (vmess only)
       "security": str,       # Encryption method
       "network": str,        # Network type: "tcp", "ws", "grpc"
       "tls": bool,           # TLS enabled
       "sni": str,            # Server name indication
       "path": str,           # WebSocket path
       "ping": int,           # Latency in ms (-1 if unknown)
       "country_code": str    # ISO country code
   }
