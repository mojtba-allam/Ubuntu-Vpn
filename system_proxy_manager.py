"""
System Proxy Manager

Automatically configures system proxy settings for Ubuntu/GNOME.
"""

import os
import subprocess
import json
import tempfile
from typing import Dict, Optional, Tuple
from pathlib import Path


class SystemProxyManager:
    """Manages system proxy configuration automatically"""

    def __init__(self, config_dir: str):
        """
        Initialize system proxy manager.

        Args:
            config_dir: Directory for storing proxy settings
        """
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.config_dir / "system_proxy_settings.json"
        self.original_settings = None
        self.is_configured = False

    def backup_original_settings(self) -> bool:
        """
        Backup original system proxy settings.

        Returns:
            True if backup successful
        """
        try:
            print("💾 Backing up original system proxy settings...")

            # Get current GNOME proxy settings
            settings = {
                'mode': self._get_gsetting('org.gnome.system.proxy', 'mode'),
                'http_host': self._get_gsetting('org.gnome.system.proxy.http', 'host'),
                'http_port': self._get_gsetting('org.gnome.system.proxy.http', 'port'),
                'https_host': self._get_gsetting('org.gnome.system.proxy.https', 'host'),
                'https_port': self._get_gsetting('org.gnome.system.proxy.https', 'port'),
                'socks_host': self._get_gsetting('org.gnome.system.proxy.socks', 'host'),
                'socks_port': self._get_gsetting('org.gnome.system.proxy.socks', 'port'),
                'autoconfig_url': self._get_gsetting('org.gnome.system.proxy', 'autoconfig-url'),
                'ignore_hosts': self._get_gsetting('org.gnome.system.proxy', 'ignore-hosts')
            }

            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)

            self.original_settings = settings
            print("✅ Original settings backed up")
            return True

        except Exception as e:
            print(f"❌ Failed to backup settings: {e}")
            return False

    def _get_gsetting(self, schema: str, key: str) -> str:
        """Get gsetting value"""
        try:
            result = subprocess.run(
                ['gsettings', 'get', schema, key],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().strip("'")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return ""

    def _set_gsetting(self, schema: str, key: str, value: str) -> bool:
        """Set gsetting value"""
        try:
            result = subprocess.run(
                ['gsettings', 'set', schema, key, value],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def configure_system_proxy(self, proxy_type: str, host: str = "127.0.0.1",
                             port: int = 1080, socks_port: int = 1080) -> bool:
        """
        Configure system proxy settings.

        Args:
            proxy_type: Type of proxy ('socks', 'http', 'both')
            host: Proxy host address
            port: HTTP proxy port
            socks_port: SOCKS proxy port

        Returns:
            True if configuration successful
        """
        try:
            print(f"🔧 Configuring system proxy ({proxy_type}) on {host}")

            # Backup original settings if not already done
            if not self.original_settings:
                if not self.backup_original_settings():
                    return False

            # Set proxy mode to manual
            if not self._set_gsetting('org.gnome.system.proxy', 'mode', 'manual'):
                print("❌ Failed to set proxy mode")
                return False

            success = True

            if proxy_type in ['socks', 'both']:
                # Configure SOCKS proxy
                success &= self._set_gsetting('org.gnome.system.proxy.socks', 'host', host)
                success &= self._set_gsetting('org.gnome.system.proxy.socks', 'port', str(socks_port))
                print(f"✅ SOCKS proxy configured: {host}:{socks_port}")

            if proxy_type in ['http', 'both']:
                # Configure HTTP proxy
                success &= self._set_gsetting('org.gnome.system.proxy.http', 'host', host)
                success &= self._set_gsetting('org.gnome.system.proxy.http', 'port', str(port))
                success &= self._set_gsetting('org.gnome.system.proxy.https', 'host', host)
                success &= self._set_gsetting('org.gnome.system.proxy.https', 'port', str(port))
                print(f"✅ HTTP/HTTPS proxy configured: {host}:{port}")

            if success:
                self.is_configured = True
                print("✅ System proxy configured successfully")

                # Configure proxy bypass for local addresses
                self._configure_bypass_settings()

                # Notify user
                self._show_proxy_notification(proxy_type, host, port, socks_port)

            return success

        except Exception as e:
            print(f"❌ Failed to configure system proxy: {e}")
            return False

    def _configure_bypass_settings(self):
        """Configure proxy bypass for local addresses"""
        try:
            # Set ignore hosts for local addresses
            ignore_hosts = [
                'localhost', '127.*', '::1', '10.*', '192.168.*', '172.16.*', '172.17.*', '172.18.*',
                '172.19.*', '172.20.*', '172.21.*', '172.22.*', '172.23.*', '172.24.*', '172.25.*',
                '172.26.*', '172.27.*', '172.28.*', '172.29.*', '172.30.*', '172.31.*'
            ]

            # Convert to array format for gsettings
            ignore_hosts_str = "['" + "', '".join(ignore_hosts) + "']"
            self._set_gsetting('org.gnome.system.proxy', 'ignore-hosts', ignore_hosts_str)
            print("✅ Proxy bypass configured for local networks")

        except Exception as e:
            print(f"⚠️  Failed to configure bypass settings: {e}")

    def _show_proxy_notification(self, proxy_type: str, host: str, port: int, socks_port: int):
        """Show system notification about proxy configuration"""
        try:
            if proxy_type == 'socks':
                message = f"System proxy configured\\nSOCKS5: {host}:{socks_port}"
            elif proxy_type == 'http':
                message = f"System proxy configured\\nHTTP: {host}:{port}"
            else:  # both
                message = f"System proxy configured\\nHTTP: {host}:{port}\\nSOCKS5: {host}:{socks_port}"

            # Try to show notification
            subprocess.run([
                'notify-send',
                'VPN Proxy Active',
                message,
                '-i', 'network-vpn',
                '-t', '3000'
            ], capture_output=True)

        except Exception:
            # Fallback to console message
            print(f"📢 System proxy configured! {message.replace(chr(10), ' ')}")

    def restore_original_settings(self) -> bool:
        """
        Restore original system proxy settings.

        Returns:
            True if restoration successful
        """
        try:
            if not self.original_settings:
                # Load from file
                if self.settings_file.exists():
                    with open(self.settings_file, 'r') as f:
                        self.original_settings = json.load(f)
                else:
                    print("ℹ️  No original settings to restore")
                    return True

            print("🔄 Restoring original system proxy settings...")

            settings = self.original_settings
            success = True

            # Restore all settings
            success &= self._set_gsetting('org.gnome.system.proxy', 'mode', settings['mode'])
            success &= self._set_gsetting('org.gnome.system.proxy.http', 'host', settings['http_host'])
            success &= self._set_gsetting('org.gnome.system.proxy.http', 'port', settings['http_port'])
            success &= self._set_gsetting('org.gnome.system.proxy.https', 'host', settings['https_host'])
            success &= self._set_gsetting('org.gnome.system.proxy.https', 'port', settings['https_port'])
            success &= self._set_gsetting('org.gnome.system.proxy.socks', 'host', settings['socks_host'])
            success &= self._set_gsetting('org.gnome.system.proxy.socks', 'port', settings['socks_port'])
            success &= self._set_gsetting('org.gnome.system.proxy', 'autoconfig-url', settings['autoconfig_url'])
            success &= self._set_gsetting('org.gnome.system.proxy', 'ignore-hosts', settings['ignore_hosts'])

            if success:
                self.is_configured = False
                print("✅ Original settings restored")

                # Remove backup file
                if self.settings_file.exists():
                    self.settings_file.unlink()

                # Show notification
                try:
                    subprocess.run([
                        'notify-send',
                        'VPN Proxy Disabled',
                        'System proxy settings restored',
                        '-i', 'network-vpn',
                        '-t', '3000'
                    ], capture_output=True)
                except Exception:
                    pass

            return success

        except Exception as e:
            print(f"❌ Failed to restore settings: {e}")
            return False

    def disable_system_proxy(self) -> bool:
        """
        Disable system proxy (set to none).

        Returns:
            True if successful
        """
        try:
            print("🚫 Disabling system proxy...")

            # Backup current settings if not already done
            if not self.original_settings:
                self.backup_original_settings()

            # Set proxy mode to none
            if self._set_gsetting('org.gnome.system.proxy', 'mode', 'none'):
                self.is_configured = False
                print("✅ System proxy disabled")

                # Show notification
                try:
                    subprocess.run([
                        'notify-send',
                        'VPN Proxy Disabled',
                        'System proxy has been disabled',
                        '-i', 'network-idle',
                        '-t', '3000'
                    ], capture_output=True)
                except Exception:
                    pass

                return True
            else:
                print("❌ Failed to disable proxy")
                return False

        except Exception as e:
            print(f"❌ Failed to disable proxy: {e}")
            return False

    def get_current_proxy_settings(self) -> Dict:
        """
        Get current system proxy settings.

        Returns:
            Dictionary with current proxy settings
        """
        return {
            'mode': self._get_gsetting('org.gnome.system.proxy', 'mode'),
            'http_host': self._get_gsetting('org.gnome.system.proxy.http', 'host'),
            'http_port': self._get_gsetting('org.gnome.system.proxy.http', 'port'),
            'socks_host': self._get_gsetting('org.gnome.system.proxy.socks', 'host'),
            'socks_port': self._get_gsetting('org.gnome.system.proxy.socks', 'port'),
        }

    def is_gnome_available(self) -> bool:
        """
        Check if GNOME/gsettings is available.

        Returns:
            True if GNOME is available
        """
        try:
            result = subprocess.run(
                ['gsettings', '--version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def check_permissions(self) -> bool:
        """
        Check if we have permission to change system settings.

        Returns:
            True if permissions are sufficient
        """
        try:
            # Try to read a setting
            self._get_gsetting('org.gnome.system.proxy', 'mode')
            return True
        except Exception:
            return False

    def get_proxy_info(self) -> Dict:
        """
        Get information about current proxy configuration.

        Returns:
            Dictionary with proxy information
        """
        current_settings = self.get_current_proxy_settings()

        return {
            'gnome_available': self.is_gnome_available(),
            'has_permissions': self.check_permissions(),
            'current_mode': current_settings['mode'],
            'is_configured': self.is_configured,
            'has_backup': self.original_settings is not None,
            'backup_file': str(self.settings_file) if self.settings_file.exists() else None,
            'current_proxy': {
                'http': f"{current_settings['http_host']}:{current_settings['http_port']}" if current_settings['http_host'] and current_settings['http_port'] else None,
                'socks': f"{current_settings['socks_host']}:{current_settings['socks_port']}" if current_settings['socks_host'] and current_settings['socks_port'] else None
            }
        }