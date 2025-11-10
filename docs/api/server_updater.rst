server_updater module
=====================

.. automodule:: server_updater
   :members:
   :undoc-members:
   :show-inheritance:

The server_updater module handles periodic server list updates and ping measurements.

Classes
-------

.. autoclass:: server_updater.ServerUpdater
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   Manages periodic server list updates and ping measurements.

   **Signals:**

   * ``servers_updated(list)`` - Emitted when server list is updated

   **Key Methods:**

   * :meth:`start` - Start periodic updates
   * :meth:`stop` - Stop periodic updates
   * :meth:`set_interval` - Change refresh frequency
   * :meth:`refresh_now` - Trigger immediate refresh
   * :meth:`ping_server` - Measure server latency
   * :meth:`sort_servers` - Sort servers by ping or name

Usage Example
-------------

.. code-block:: python

   from PyQt6.QtWidgets import QApplication
   from subscription_manager import SubscriptionManager
   from server_updater import ServerUpdater

   app = QApplication([])

   # Initialize managers
   sub_manager = SubscriptionManager()
   updater = ServerUpdater(sub_manager, interval=10)

   # Connect to signal
   def on_servers_updated(servers):
       print(f"Received {len(servers)} servers")
       for server in servers:
           print(f"  {server['name']}: {server['ping']}ms")

   updater.servers_updated.connect(on_servers_updated)

   # Start periodic updates
   updater.start()

   # Change interval
   updater.set_interval(30)  # 30 seconds

   # Manual refresh
   updater.refresh_now()

   # Stop updates
   updater.stop()

Ping Measurement
----------------

The :meth:`ping_server` method measures latency by:

1. Creating a TCP socket connection
2. Timing the connection attempt
3. Returning latency in milliseconds
4. Returning -1 if server is unreachable

.. code-block:: python

   updater = ServerUpdater(sub_manager)
   
   # Ping a specific server
   latency = updater.ping_server("1.2.3.4", 443)
   
   if latency > 0:
       print(f"Latency: {latency}ms")
   else:
       print("Server unreachable")

Server Sorting
--------------

Servers can be sorted by ping or name:

.. code-block:: python

   # Sort by ping (fastest first)
   sorted_servers = updater.sort_servers(servers, by="ping")

   # Sort by name (alphabetically)
   sorted_servers = updater.sort_servers(servers, by="name")
