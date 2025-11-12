"""
TUN (Tunnel) Manager

Handles TUN interface creation and system-wide VPN routing.
"""

import os
import subprocess
import time
import json
import signal
from typing import Dict, Optional, List
from pathlib import Path


class TUNManager:
    """Manages TUN interface and system-wide routing"""

    def __init__(self, config_dir: str):
        """
        Initialize TUN manager.

        Args:
            config_dir: Directory for storing TUN configuration
        """
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.tun_interface = "tun0"
        self.tun_process = None
        self.routing_config = self.config_dir / "tun_routing.json"
        self.is_active = False

        # Check prerequisites
        self.has_tun_device = self._check_tun_device()
        self.has_iproute2 = self._check_iproute2()
        self.has_permissions = self._check_permissions()

    def _check_tun_device(self) -> bool:
        """Check if TUN device is available"""
        return os.path.exists('/dev/net/tun')

    def _check_iproute2(self) -> bool:
        """Check if ip command is available"""
        try:
            subprocess.run(['ip', '--version'],
                         capture_output=True, timeout=2)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_permissions(self) -> bool:
        """Check if we have permission to create TUN interfaces"""
        try:
            # Test if we can access TUN device
            with open('/dev/net/tun', 'r') as f:
                pass
            return True
        except (PermissionError, OSError):
            return False

    def check_requirements(self) -> Dict:
        """
        Check TUN mode requirements.

        Returns:
            Dictionary with requirement status
        """
        return {
            'tun_device_available': self.has_tun_device,
            'iproute2_available': self.has_iproute2,
            'has_permissions': self.has_permissions,
            'root_required': not self.has_permissions,
            'can_create_tun': self.has_tun_device and self.has_iproute2 and self.has_permissions
        }

    def create_tun_interface(self) -> bool:
        """
        Create TUN interface.

        Returns:
            True if successful
        """
        if not self.has_tun_device:
            print("❌ TUN device not available (/dev/net/tun)")
            return False

        if not self.has_iproute2:
            print("❌ ip command not available (iproute2 package)")
            return False

        try:
            print(f"🔧 Creating TUN interface: {self.tun_interface}")

            # Check if interface already exists
            result = subprocess.run(['ip', 'link', 'show', self.tun_interface],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                print(f"⚠️  Interface {self.tun_interface} already exists")
                # Clean up existing interface
                self.destroy_tun_interface()

            # Create TUN interface using ip command
            subprocess.run(['ip', 'tuntap', 'add', 'dev', self.tun_interface, 'mode', 'tun'],
                         check=True, capture_output=True)

            # Bring interface up
            subprocess.run(['ip', 'link', 'set', 'dev', self.tun_interface, 'up'],
                         check=True, capture_output=True)

            # Assign IP address
            subprocess.run(['ip', 'addr', 'add', '10.0.0.1/24', 'dev', self.tun_interface],
                         check=True, capture_output=True)

            print(f"✅ TUN interface {self.tun_interface} created successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create TUN interface: {e}")
            return False
        except Exception as e:
            print(f"❌ Error creating TUN interface: {e}")
            return False

    def destroy_tun_interface(self) -> bool:
        """
        Destroy TUN interface.

        Returns:
            True if successful
        """
        try:
            print(f"🧹 Destroying TUN interface: {self.tun_interface}")

            # Remove interface
            subprocess.run(['ip', 'link', 'del', self.tun_interface],
                         capture_output=True)  # Don't check return code as it might not exist

            print(f"✅ TUN interface {self.tun_interface} destroyed")
            return True

        except Exception as e:
            print(f"⚠️  Error destroying TUN interface: {e}")
            return False

    def setup_routing_table(self, dns_servers: List[str] = None) -> bool:
        """
        Setup routing rules for TUN interface.

        Args:
            dns_servers: List of DNS servers to use

        Returns:
            True if successful
        """
        try:
            print("🛣️  Setting up routing rules for TUN interface")

            # Save current routing for restoration
            self._save_current_routing()

            # Add default route through TUN interface
            subprocess.run(['ip', 'route', 'add', 'default', 'dev', self.tun_interface],
                         check=True)

            # Setup DNS if provided
            if dns_servers:
                self._setup_dns(dns_servers)

            # Add routing rules to bypass proxy for local networks
            self._setup_bypass_routing()

            print("✅ Routing rules configured")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup routing: {e}")
            return False

    def _save_current_routing(self):
        """Save current routing configuration"""
        try:
            # Save current default route
            result = subprocess.run(['ip', 'route', 'show', 'default'],
                                  capture_output=True, text=True)

            routing_data = {
                'default_route': result.stdout.strip(),
                'timestamp': time.time()
            }

            with open(self.routing_config, 'w') as f:
                json.dump(routing_data, f, indent=2)

            print("💾 Current routing configuration saved")

        except Exception as e:
            print(f"⚠️  Failed to save routing config: {e}")

    def _setup_dns(self, dns_servers: List[str]):
        """Setup DNS servers"""
        try:
            print(f"🌐 Configuring DNS servers: {dns_servers}")

            # Backup current resolv.conf
            resolv_backup = self.config_dir / "resolv.conf.backup"
            if os.path.exists('/etc/resolv.conf'):
                subprocess.run(['cp', '/etc/resolv.conf', str(resolv_backup)])

            # Create new resolv.conf
            resolv_content = "# Generated by VPN client\\n"
            for dns in dns_servers:
                resolv_content += f"nameserver {dns}\\n"

            # Try to update resolv.conf (requires root)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
                f.write(resolv_content)
                temp_resolv = f.name

            try:
                subprocess.run(['sudo', 'cp', temp_resolv, '/etc/resolv.conf'], check=True)
                print("✅ DNS configuration updated")
            except subprocess.CalledProcessError:
                print("⚠️  Could not update DNS (requires sudo permissions)")
                print(f"   Manual configuration required: {dns_servers}")
            finally:
                os.unlink(temp_resolv)

        except Exception as e:
            print(f"⚠️  DNS setup failed: {e}")

    def _setup_bypass_routing(self):
        """Setup routing to bypass VPN for local networks"""
        try:
            print("🔧 Setting up bypass routing for local networks")

            local_networks = [
                '192.168.0.0/16',
                '10.0.0.0/8',
                '172.16.0.0/12',
                '127.0.0.0/8',
                '169.254.0.0/16'  # Link-local
            ]

            # Add routes for local networks to bypass VPN
            for network in local_networks:
                try:
                    subprocess.run(['ip', 'route', 'add', network, 'dev', 'lo'],
                                 capture_output=True, check=True)
                    print(f"✅ Added bypass route: {network}")
                except subprocess.CalledProcessError:
                    # Route might already exist
                    pass

        except Exception as e:
            print(f"⚠️  Bypass routing setup failed: {e}")

    def restore_routing(self) -> bool:
        """
        Restore original routing configuration.

        Returns:
            True if successful
        """
        try:
            print("🔄 Restoring original routing configuration")

            # Remove VPN routing
            subprocess.run(['ip', 'route', 'del', 'default', 'dev', self.tun_interface],
                         capture_output=True)

            # Restore DNS if backup exists
            resolv_backup = self.config_dir / "resolv.conf.backup"
            if resolv_backup.exists():
                try:
                    subprocess.run(['sudo', 'cp', str(resolv_backup), '/etc/resolv.conf'], check=True)
                    print("✅ DNS configuration restored")
                    resolv_backup.unlink()  # Remove backup after restoration
                except subprocess.CalledProcessError:
                    print("⚠️  Could not restore DNS (requires sudo)")

            print("✅ Routing configuration restored")
            return True

        except Exception as e:
            print(f"⚠️  Error restoring routing: {e}")
            return False

    def enable_tun_mode(self, dns_servers: List[str] = None) -> bool:
        """
        Enable TUN mode with system-wide routing.

        Args:
            dns_servers: DNS servers to use

        Returns:
            True if successful
        """
        if not self.can_enable_tun():
            return False

        try:
            print("🚀 Enabling TUN mode")

            # Create TUN interface
            if not self.create_tun_interface():
                return False

            # Setup routing
            if not self.setup_routing_table(dns_servers):
                # Cleanup on failure
                self.destroy_tun_interface()
                return False

            self.is_active = True
            print("✅ TUN mode enabled successfully")

            # Show notification
            self._show_tun_notification(True)

            return True

        except Exception as e:
            print(f"❌ Failed to enable TUN mode: {e}")
            return False

    def disable_tun_mode(self) -> bool:
        """
        Disable TUN mode and restore original configuration.

        Returns:
            True if successful
        """
        try:
            print("🛑 Disabling TUN mode")

            # Restore routing
            self.restore_routing()

            # Destroy TUN interface
            self.destroy_tun_interface()

            self.is_active = False
            print("✅ TUN mode disabled")

            # Show notification
            self._show_tun_notification(False)

            return True

        except Exception as e:
            print(f"⚠️  Error disabling TUN mode: {e}")
            return False

    def can_enable_tun(self) -> bool:
        """
        Check if TUN mode can be enabled.

        Returns:
            True if TUN mode can be enabled
        """
        if not self.has_tun_device:
            print("❌ TUN device not available")
            return False

        if not self.has_iproute2:
            print("❌ iproute2 not installed")
            return False

        if not self.has_permissions:
            print("❌ Insufficient permissions for TUN mode")
            print("   Try: sudo chown $USER:$USER /dev/net/tun")
            return False

        return True

    def _show_tun_notification(self, enabled: bool):
        """Show system notification about TUN mode"""
        try:
            if enabled:
                title = "VPN TUN Mode Active"
                message = f"All traffic is now routed through VPN\\nInterface: {self.tun_interface}"
                icon = "network-vpn"
            else:
                title = "VPN TUN Mode Disabled"
                message = "System routing has been restored"
                icon = "network-idle"

            subprocess.run([
                'notify-send',
                title,
                message,
                '-i', icon,
                '-t', '3000'
            ], capture_output=True)

        except Exception:
            # Fallback to console message
            print(f"📢 {title}: {message.replace(chr(10), ' ')}")

    def get_status(self) -> Dict:
        """
        Get current TUN mode status.

        Returns:
            Dictionary with status information
        """
        # Check if interface exists
        result = subprocess.run(['ip', 'link', 'show', self.tun_interface],
                              capture_output=True, text=True)
        interface_exists = result.returncode == 0

        # Get routing info
        result = subprocess.run(['ip', 'route', 'show', 'default'],
                              capture_output=True, text=True)
        default_route = result.stdout.strip() if result.returncode == 0 else ""

        return {
            'requirements': self.check_requirements(),
            'interface_exists': interface_exists,
            'is_active': self.is_active,
            'interface_name': self.tun_interface if interface_exists else None,
            'default_route': default_route,
            'has_backup': self.routing_config.exists(),
            'backup_file': str(self.routing_config) if self.routing_config.exists() else None
        }

    def test_connectivity(self) -> Dict:
        """
        Test network connectivity through TUN interface.

        Returns:
            Dictionary with test results
        """
        results = {
            'dns_resolution': False,
            'external_connectivity': False,
            'internal_connectivity': False,
            'latency_ms': None
        }

        try:
            import time
            import socket

            # Test DNS resolution
            start_time = time.time()
            try:
                socket.gethostbyname('google.com')
                results['dns_resolution'] = True
                dns_time = (time.time() - start_time) * 1000
            except socket.gaierror:
                dns_time = None

            # Test external connectivity
            start_time = time.time()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect(('8.8.8.8', 53))
                sock.close()
                results['external_connectivity'] = True
                latency = (time.time() - start_time) * 1000
                results['latency_ms'] = round(latency, 2)
            except Exception:
                pass

            # Test internal connectivity (localhost)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect(('127.0.0.1', 22))  # SSH port if available
                sock.close()
                results['internal_connectivity'] = True
            except Exception:
                pass

        except Exception as e:
            print(f"⚠️  Connectivity test error: {e}")

        return results