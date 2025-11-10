ui package
==========

.. automodule:: ui
   :members:
   :undoc-members:
   :show-inheritance:

The ui package contains all graphical user interface components.

Submodules
----------

.. toctree::
   :maxdepth: 4

   ui.main_window
   ui.servers_tab
   ui.settings_tab
   ui.logs_tab
   ui.server_card
   ui.animated_button
   ui.icon_loader
   ui.theme_loader

Main Window
-----------

.. automodule:: ui.main_window
   :members:
   :undoc-members:
   :show-inheritance:

Tabs
----

Servers Tab
~~~~~~~~~~~

.. automodule:: ui.servers_tab
   :members:
   :undoc-members:
   :show-inheritance:

Settings Tab
~~~~~~~~~~~~

.. automodule:: ui.settings_tab
   :members:
   :undoc-members:
   :show-inheritance:

Logs Tab
~~~~~~~~

.. automodule:: ui.logs_tab
   :members:
   :undoc-members:
   :show-inheritance:

Widgets
-------

Server Card
~~~~~~~~~~~

.. automodule:: ui.server_card
   :members:
   :undoc-members:
   :show-inheritance:

Animated Button
~~~~~~~~~~~~~~~

.. automodule:: ui.animated_button
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
---------

Icon Loader
~~~~~~~~~~~

.. automodule:: ui.icon_loader
   :members:
   :undoc-members:
   :show-inheritance:

Theme Loader
~~~~~~~~~~~~

.. automodule:: ui.theme_loader
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Creating a Main Window
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from PyQt6.QtWidgets import QApplication
   from ui.main_window import MainWindow

   app = QApplication([])
   window = MainWindow()
   window.show()
   app.exec()

Loading Icons
~~~~~~~~~~~~~

.. code-block:: python

   from ui.icon_loader import IconLoader

   # Get app icon
   icon = IconLoader.get_app_icon(128)

   # Get country flag
   flag = IconLoader.get_flag_icon("US", 48)

   # Get status icon
   status = IconLoader.get_status_icon("connected", 64)

Applying Themes
~~~~~~~~~~~~~~~

.. code-block:: python

   from ui.theme_loader import ThemeLoader

   loader = ThemeLoader()
   
   # Load a theme
   stylesheet = loader.load_theme("neon")
   app.setStyleSheet(stylesheet)
   
   # Save preference
   loader.save_theme_preference("neon")

Creating Custom Widgets
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from PyQt6.QtWidgets import QWidget
   from ui.server_card import ServerCard

   # Create a server card
   server = {
       "name": "Test Server",
       "ip": "1.2.3.4",
       "port": 443,
       "type": "vmess",
       "ping": 50
   }

   card = ServerCard(server)
   card.connect_clicked.connect(lambda s: print(f"Connect to {s['name']}"))
   card.update_ping(50)
