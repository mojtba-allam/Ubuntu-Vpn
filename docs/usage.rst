Usage Guide
===========

This guide covers the basic usage of V2Ray Client.

Starting the Application
-------------------------

.. code-block:: bash

   # If installed via script or package
   v2ray-client

   # If running from source
   python3 main.py

   # With custom theme
   python3 main.py --theme neon

   # With custom config directory
   python3 main.py --config ~/my-v2ray-config

Main Interface
--------------

The application has three main tabs:

1. **Servers Tab**: Browse and connect to available servers
2. **Settings Tab**: Configure subscriptions and application preferences
3. **Logs Tab**: View real-time V2Ray connection logs

Managing Subscriptions
----------------------

Adding a Subscription
~~~~~~~~~~~~~~~~~~~~~

1. Click on the **Settings** tab
2. Click **Add Subscription** button
3. Enter your subscription URL
4. Optionally give it a name
5. Click **OK**

The server list will update automatically.

Editing a Subscription
~~~~~~~~~~~~~~~~~~~~~~

1. Go to the **Settings** tab
2. Select a subscription from the list
3. Click **Edit** button
4. Modify the name
5. Click **OK**

Removing a Subscription
~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the **Settings** tab
2. Select a subscription from the list
3. Click **Remove** button
4. Confirm the removal

Connecting to Servers
---------------------

Viewing Server List
~~~~~~~~~~~~~~~~~~~

The **Servers** tab displays all available servers with:

* Country flag
* Server name
* IP address and port
* Ping latency
* Connect button

Connecting
~~~~~~~~~~

1. Browse the server list in the **Servers** tab
2. Look for servers with low ping (green bars)
3. Click **Connect** on your preferred server
4. Wait for connection to establish
5. Your public IP will be displayed when connected

Disconnecting
~~~~~~~~~~~~~

Click the **Disconnect** button on the connected server card.

Searching Servers
~~~~~~~~~~~~~~~~~

Use the search bar at the top of the Servers tab:

.. code-block:: text

   Search examples:
   - "USA" - Find all US servers
   - "Singapore" - Find Singapore servers
   - "45.67" - Find servers by IP

Configuring Settings
--------------------

Refresh Interval
~~~~~~~~~~~~~~~~

Controls how often subscription URLs are fetched:

* Default: 10 seconds
* Minimum: 5 seconds
* Recommended: 10-30 seconds

Theme Selection
~~~~~~~~~~~~~~~

Choose your preferred visual appearance:

* **Dark**: Classic dark mode
* **Light**: Clean light mode
* **Neon**: Vibrant gradients with glow effects

Auto-Start
~~~~~~~~~~

Enable the application to launch automatically when you log in.

Monitoring Logs
---------------

The **Logs** tab displays real-time output from V2Ray Core.

Reading Logs
~~~~~~~~~~~~

Successful connection:

.. code-block:: text

   [Info] V2Ray started
   [Info] Outbound connection established
   [Info] TCP connection to server:port

Connection issues:

.. code-block:: text

   [Error] Failed to connect to server
   [Warning] Connection timeout
   [Error] Invalid configuration

Clearing Logs
~~~~~~~~~~~~~

Click **Clear Logs** button to empty the display.

Exporting Logs
~~~~~~~~~~~~~~

1. Click **Export Logs** button
2. Choose save location
3. Logs are saved as plain text file

Keyboard Shortcuts
------------------

* **Ctrl+Tab**: Switch between tabs
* **Ctrl+F**: Focus search bar (in Servers tab)
* **Ctrl+R**: Refresh server list
* **Ctrl+Q**: Quit application

Command-Line Options
--------------------

.. code-block:: bash

   # Show version
   python3 main.py --version

   # Start with specific theme
   python3 main.py --theme dark
   python3 main.py --theme light
   python3 main.py --theme neon

   # Use custom config directory
   python3 main.py --config /path/to/config

Tips and Best Practices
------------------------

For Best Performance
~~~~~~~~~~~~~~~~~~~~

* Choose servers with ping < 100ms
* Prefer servers geographically closer to you
* Avoid servers with very high ping

For Reliability
~~~~~~~~~~~~~~~

* Add multiple subscriptions for redundancy
* Monitor logs for issues
* Keep V2Ray Core updated

For Privacy
~~~~~~~~~~~

* Use TLS-enabled servers
* Verify server provider reputation
* Don't share subscription URLs
* Disconnect when not needed

Troubleshooting
---------------

Connection Fails
~~~~~~~~~~~~~~~~

1. Check the **Logs** tab for error messages
2. Try a different server
3. Verify V2Ray Core is installed: ``v2ray --version``
4. Check firewall settings: ``sudo ufw status``

No Internet After Connect
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Disconnect and reconnect
2. Try a different server
3. Check system proxy settings
4. Verify V2Ray is running: ``ps aux | grep v2ray``

Slow Connection
~~~~~~~~~~~~~~~

* Choose servers with lower ping
* Try servers in different locations
* Check your internet connection speed

Application Won't Start
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check Python version
   python3 --version  # Should be 3.8+

   # Reinstall dependencies
   ./venv/bin/pip install -r requirements.txt

   # Run from terminal to see errors
   python3 main.py
