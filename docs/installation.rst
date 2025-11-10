Installation Guide
==================

This guide covers different methods to install the V2Ray Client on Ubuntu.

Prerequisites
-------------

* Ubuntu 20.04 or later
* Python 3.8 or higher
* V2Ray Core (installed automatically by the script)

Method 1: Installation Script (Recommended)
--------------------------------------------

The easiest way to install V2Ray Client is using the provided installation script:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/v2ray-client.git
   cd v2ray-client

   # Make the script executable
   chmod +x install.sh

   # Run the installation script
   ./install.sh

The script will:

1. Install Python dependencies
2. Install V2Ray Core
3. Set up configuration directories
4. Create a desktop entry

Method 2: Manual Installation
------------------------------

If you prefer to install manually:

Step 1: Install System Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv curl

Step 2: Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

Step 3: Install Python Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

Step 4: Install V2Ray Core
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

Step 5: Create Configuration Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   mkdir -p ~/.config/v2ray-client

Method 3: Package Installation
-------------------------------

Debian Package (.deb)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Download the .deb package
   wget https://github.com/yourusername/v2ray-client/releases/download/v1.0.0/v2ray-client_1.0.0_amd64.deb

   # Install the package
   sudo dpkg -i v2ray-client_1.0.0_amd64.deb

   # Install dependencies if needed
   sudo apt-get install -f

AppImage
~~~~~~~~

.. code-block:: bash

   # Download the AppImage
   wget https://github.com/yourusername/v2ray-client/releases/download/v1.0.0/V2RayClient-1.0.0-x86_64.AppImage

   # Make it executable
   chmod +x V2RayClient-1.0.0-x86_64.AppImage

   # Run the application
   ./V2RayClient-1.0.0-x86_64.AppImage

Verification
------------

After installation, verify that everything is working:

.. code-block:: bash

   # Check Python version
   python3 --version  # Should be 3.8 or higher

   # Check V2Ray Core installation
   v2ray --version

   # Run the application
   python3 main.py

Troubleshooting
---------------

PyQt6 Not Found
~~~~~~~~~~~~~~~

If you get a "PyQt6 not found" error:

.. code-block:: bash

   ./venv/bin/pip install PyQt6

V2Ray Core Not Found
~~~~~~~~~~~~~~~~~~~~~

If V2Ray Core is not found:

.. code-block:: bash

   # Reinstall V2Ray Core
   bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

   # Verify installation
   which v2ray
   v2ray --version

Permission Errors
~~~~~~~~~~~~~~~~~

If you encounter permission errors:

.. code-block:: bash

   # Fix configuration directory permissions
   chmod 700 ~/.config/v2ray-client
   chmod 600 ~/.config/v2ray-client/*.json

Uninstallation
--------------

To uninstall V2Ray Client:

.. code-block:: bash

   # If installed via .deb package
   sudo apt remove v2ray-client

   # If installed manually, remove the directory
   rm -rf ~/v2ray-client

   # Remove configuration files (optional)
   rm -rf ~/.config/v2ray-client

   # Uninstall V2Ray Core (optional)
   sudo bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh) --remove
