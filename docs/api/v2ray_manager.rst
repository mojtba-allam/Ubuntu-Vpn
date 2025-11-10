v2ray_manager module
====================

.. automodule:: v2ray_manager
   :members:
   :undoc-members:
   :show-inheritance:

The v2ray_manager module handles all V2Ray process lifecycle operations including:

* Starting and stopping V2Ray processes
* Managing configuration files
* Monitoring connection status
* Fetching public IP information
* Streaming process logs

Classes
-------

.. autoclass:: v2ray_manager.V2RayManager
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   The main class for managing V2Ray connections.

   **Key Methods:**

   * :meth:`connect` - Start V2Ray with server configuration
   * :meth:`disconnect` - Stop V2Ray process and cleanup
   * :meth:`is_connected` - Check connection status
   * :meth:`get_public_ip` - Fetch public IP information
   * :meth:`get_logs` - Retrieve recent logs
   * :meth:`stream_logs` - Set up real-time log streaming

Usage Example
-------------

.. code-block:: python

   from v2ray_manager import V2RayManager

   # Initialize manager
   manager = V2RayManager()

   # Connect to a server
   server_config = {
       "name": "Test Server",
       "type": "vmess",
       "ip": "1.2.3.4",
       "port": 443,
       "uuid": "your-uuid-here",
       # ... other config
   }

   if manager.connect(server_config):
       print("Connected successfully!")
       
       # Get public IP
       ip_info = manager.get_public_ip()
       print(f"Public IP: {ip_info['ip']}")
       
       # Set up log streaming
       manager.stream_logs(lambda line: print(line))
   
   # Disconnect when done
   manager.disconnect()
