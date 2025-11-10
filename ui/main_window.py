"""
Main Window for V2Ray Client

Provides the main application window with tabbed interface.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QCloseEvent
from ui.theme_loader import ThemeLoader
from ui.servers_tab import ServersTab
from ui.settings_tab import SettingsTab
from ui.logs_tab import LogsTab
from v2ray_manager import V2RayManager
from hysteria2_manager import Hysteria2Manager
from subscription_manager import SubscriptionManager
from server_updater import ServerUpdater
from config_generator import generate_v2ray_config


class ToastNotification(QWidget):
    """Floating toast notification widget"""
    
    def __init__(self, message: str, toast_type: str, parent=None):
        """
        Initialize toast notification.
        
        Args:
            message: Message to display
            toast_type: Type of toast - "success", "error", or "info"
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create label
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setMinimumWidth(200)
        self.label.setMaximumWidth(400)
        
        # Set style based on type
        if toast_type == "success":
            self.label.setObjectName("toastSuccess")
        elif toast_type == "error":
            self.label.setObjectName("toastError")
        else:
            self.label.setObjectName("toastInfo")
        
        layout.addWidget(self.label)
        
        # Adjust size
        self.adjustSize()


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self, config_dir: str = "~/.config/v2ray-client"):
        """
        Initialize main window with tabs and theme.
        
        Args:
            config_dir: Configuration directory path
        """
        super().__init__()
        
        # Store config directory
        self.config_dir = config_dir
        
        # Initialize theme loader
        self.theme_loader = ThemeLoader(config_dir)
        
        # Initialize managers
        self.v2ray_manager = V2RayManager(config_dir)
        self.hysteria2_manager = Hysteria2Manager(config_dir)
        self.subscription_manager = SubscriptionManager(config_dir)
        self.server_updater = ServerUpdater(self.subscription_manager, interval=10)
        
        # Setup window
        self.setWindowTitle("V2Ray Client")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.servers_tab = ServersTab(self.v2ray_manager)
        self.settings_tab = SettingsTab(self.subscription_manager, config_dir)
        self.logs_tab = LogsTab(self.v2ray_manager)
        
        # Add tabs
        self.tab_widget.addTab(self.servers_tab, "Servers")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.logs_tab, "Logs")
        
        # Load saved settings and apply theme
        self._load_settings()
        
        # Connect signals between components
        self._connect_signals()
        
        # List to track active toasts
        self.active_toasts = []
        
        # Preload common icons for better performance
        from ui.icon_loader import IconLoader
        QTimer.singleShot(0, IconLoader.preload_common_icons)
        
        # Start server updater
        self.server_updater.start()
    
    def load_theme(self, theme_name: str) -> None:
        """
        Load CSS theme file and apply to application.
        
        Args:
            theme_name: Name of theme to load (dark, light, neon)
        """
        stylesheet = self.theme_loader.load_theme(theme_name)
        
        if stylesheet:
            # Apply to application
            QApplication.instance().setStyleSheet(stylesheet)
            
            # Save preference
            self.theme_loader.save_theme_preference(theme_name)
    
    def show_toast(self, message: str, toast_type: str = "info") -> None:
        """
        Display floating toast notification.
        
        Args:
            message: Message to display
            toast_type: Type of toast - "success", "error", or "info"
        """
        # Create toast widget
        toast = ToastNotification(message, toast_type, self)
        
        # Position toast at top center of window
        window_rect = self.geometry()
        toast_width = toast.width()
        toast_height = toast.height()
        
        # Calculate position (top center, with some margin)
        x = window_rect.x() + (window_rect.width() - toast_width) // 2
        y = window_rect.y() + 50 + (len(self.active_toasts) * (toast_height + 10))
        
        toast.move(x, y)
        toast.show()
        
        # Add to active toasts
        self.active_toasts.append(toast)
        
        # Show toast immediately (no fade animation to avoid opacity issues)
        toast.show()
        
        # Auto-hide after 3 seconds
        QTimer.singleShot(3000, lambda: self._hide_toast(toast))
    
    def _hide_toast(self, toast: ToastNotification) -> None:
        """
        Hide and remove toast notification.
        
        Args:
            toast: Toast widget to hide
        """
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
        toast.deleteLater()
    
    def _load_settings(self) -> None:
        """Load saved settings from disk and apply them"""
        # Load settings from settings tab
        settings = self.settings_tab.load_settings()
        
        # Apply settings to UI
        self.settings_tab.apply_loaded_settings(settings)
        
        # Apply saved theme
        saved_theme = settings.get("theme", self.theme_loader.DEFAULT_THEME)
        self.load_theme(saved_theme)
        
        # Apply refresh interval if saved
        if "refresh_interval" in settings:
            interval = max(5, settings["refresh_interval"])  # Minimum 5 seconds
            self.server_updater.set_interval(interval)
    
    def _connect_signals(self) -> None:
        """Connect signals between components"""
        # Connect servers tab signals
        self.servers_tab.connection_requested.connect(self._on_connection_requested)
        self.servers_tab.disconnection_requested.connect(self._on_disconnection_requested)
        self.servers_tab.refresh_requested.connect(self._on_refresh_requested)
        
        # Connect server updater to update servers tab
        self.server_updater.servers_updated.connect(self._on_servers_updated)
        
        # Connect settings tab signals
        self.settings_tab.theme_changed.connect(self._on_theme_changed)
        self.settings_tab.interval_changed.connect(self._on_interval_changed)
        self.settings_tab.subscriptions_changed.connect(self._on_subscriptions_changed)
    
    def _on_connection_requested(self, server: dict) -> None:
        """
        Handle connection request from servers tab.
        
        Args:
            server: Server configuration dictionary
        """
        # Show connecting toast
        server_name = server.get("name", "Unknown")
        self.show_toast(f"Connecting to {server_name}...", "info")
        
        # Generate V2Ray config from server info
        try:
            v2ray_config = generate_v2ray_config(server)
        except Exception as e:
            self.show_toast(f"Invalid server configuration: {e}", "error")
            return
        
        # Connect in background using QTimer to avoid blocking UI
        QTimer.singleShot(100, lambda: self._do_connection(v2ray_config, server_name))
    
    def _do_connection(self, config: dict, server_name: str) -> None:
        """
        Perform actual connection in background.

        Args:
            config: Server configuration dictionary
            server_name: Name of server for display
        """
        print(f"\n🔌 Attempting to connect to: {server_name}")

        server_type = config.get("type", "vmess")

        if server_type == "hysteria2":
            # Use Hysteria2 manager
            success, error_message = self.hysteria2_manager.connect(config)
            manager = self.hysteria2_manager
        else:
            # Use V2Ray manager
            v2ray_config = config
            success, error_message = self.v2ray_manager.connect(v2ray_config)
            manager = self.v2ray_manager

        if success:
            print(f"✅ Successfully connected to {server_name}")

            # Fetch public IP info in background
            QTimer.singleShot(2000, lambda: self._fetch_ip_info(server_name, manager))

            # Update UI immediately
            self.servers_tab.set_connection_status(True, server_name, {})

            # Show success toast
            self.show_toast(f"Connected to {server_name}", "success")
        else:
            print(f"❌ Failed to connect to {server_name}")
            print(f"Error: {error_message}")

            # Show error dialog with details
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("Connection Failed")
            error_dialog.setText(f"Failed to connect to {server_name}")
            error_dialog.setDetailedText(error_message)
            error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_dialog.exec()

            # Show error toast
            self.show_toast("Failed to connect to server", "error")
            self.servers_tab.set_connection_status(False)
    
    def _fetch_ip_info(self, server_name: str) -> None:
        """
        Fetch IP info after connection is established.
        
        Args:
            server_name: Name of connected server
        """
        ip_info = self.v2ray_manager.get_public_ip()
        if ip_info:
            self.servers_tab.set_connection_status(True, server_name, ip_info)
    
    def _on_disconnection_requested(self) -> None:
        """Handle disconnection request from servers tab."""
        # Disconnect from V2Ray
        success = self.v2ray_manager.disconnect()
        
        if success:
            # Update UI
            self.servers_tab.set_connection_status(False)
            
            # Show success toast
            self.show_toast("Disconnected from server", "info")
        else:
            # Show error toast
            self.show_toast("Failed to disconnect", "error")
    
    def _on_refresh_requested(self) -> None:
        """Handle manual refresh request from servers tab."""
        # Trigger immediate refresh
        self.server_updater.refresh_now()
        
        # Show info toast
        self.show_toast("Refreshing server list...", "info")
    
    def _on_servers_updated(self, servers: list) -> None:
        """
        Handle server list update from server updater.
        
        Args:
            servers: Updated list of servers
        """
        # Update servers tab with new list
        self.servers_tab.update_servers(servers)
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """
        Handle theme change from settings tab.
        
        Args:
            theme_name: Name of the new theme
        """
        # Apply the new theme
        self.load_theme(theme_name)
        
        # Save settings
        self.settings_tab.save_settings()
        
        # Show confirmation toast
        self.show_toast(f"Theme changed to {theme_name.capitalize()}", "success")
    
    def _on_interval_changed(self, interval: int) -> None:
        """
        Handle refresh interval change from settings tab.
        
        Args:
            interval: New interval in seconds
        """
        # Update server updater interval
        self.server_updater.set_interval(interval)
        
        # Save settings
        self.settings_tab.save_settings()
        
        # Show confirmation toast
        self.show_toast(f"Refresh interval set to {interval} seconds", "success")
    
    def _on_subscriptions_changed(self) -> None:
        """Handle subscription list change from settings tab"""
        # Trigger immediate refresh to fetch new subscription
        self.server_updater.refresh_now()
        
        # Show info toast
        self.show_toast("Subscription list updated, refreshing servers...", "info")
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle cleanup on window close.
        
        Args:
            event: Close event
        """
        # Save current settings
        if self.settings_tab:
            self.settings_tab.save_settings()
        
        # Stop server updater
        if self.server_updater:
            self.server_updater.stop()
        
        # Disconnect V2Ray if connected
        if self.v2ray_manager and self.v2ray_manager.is_connected():
            self.v2ray_manager.disconnect()
        
        # Accept the close event
        event.accept()
