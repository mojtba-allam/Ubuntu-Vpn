"""
Settings Tab Widget

Provides interface for configuring application settings including
subscriptions, refresh interval, theme, and auto-start.
"""

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QListWidget, QListWidgetItem, QPushButton, QSpinBox,
    QRadioButton, QButtonGroup, QCheckBox, QLabel, QDialog,
    QLineEdit, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from subscription_manager import SubscriptionManager


class AddServerLinkDialog(QDialog):
    """Dialog for adding a single server link"""
    
    def __init__(self, parent=None):
        """
        Initialize add server link dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Add Server Link")
        self.setMinimumWidth(600)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Info label
        info_label = QLabel(
            "Paste a vmess://, vless://, or trojan:// server link below.\n"
            "The server will be added to your server list."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #9090dd; padding: 8px;")
        layout.addWidget(info_label)
        
        # Server link input
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("vmess://... or vless://... or trojan://...")
        self.link_input.setMinimumHeight(40)
        layout.addWidget(self.link_input)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_link(self):
        """
        Get entered server link.
        
        Returns:
            Server link string
        """
        return self.link_input.text().strip()


class AddSubscriptionDialog(QDialog):
    """Dialog for adding a new subscription URL"""
    
    def __init__(self, parent=None):
        """
        Initialize add subscription dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Add Subscription")
        self.setMinimumWidth(500)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create form
        form_layout = QFormLayout()
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/subscription")
        form_layout.addRow("Subscription URL:", self.url_input)
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Optional display name")
        form_layout.addRow("Name:", self.name_input)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_values(self):
        """
        Get entered values.
        
        Returns:
            Tuple of (url, name)
        """
        return self.url_input.text().strip(), self.name_input.text().strip()


class EditSubscriptionDialog(QDialog):
    """Dialog for editing an existing subscription"""
    
    def __init__(self, subscription: dict, parent=None):
        """
        Initialize edit subscription dialog.
        
        Args:
            subscription: Subscription dictionary to edit
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Edit Subscription")
        self.setMinimumWidth(500)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create form
        form_layout = QFormLayout()
        
        # URL input (read-only)
        self.url_input = QLineEdit()
        self.url_input.setText(subscription.get("url", ""))
        self.url_input.setReadOnly(True)
        form_layout.addRow("Subscription URL:", self.url_input)
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setText(subscription.get("name", ""))
        self.name_input.setPlaceholderText("Optional display name")
        form_layout.addRow("Name:", self.name_input)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_name(self):
        """
        Get edited name.
        
        Returns:
            New name string
        """
        return self.name_input.text().strip()


class SettingsTab(QWidget):
    """Settings tab widget for application configuration"""
    
    theme_changed = pyqtSignal(str)
    interval_changed = pyqtSignal(int)
    subscriptions_changed = pyqtSignal()
    
    def __init__(self, subscription_manager: SubscriptionManager, config_dir: str = "~/.config/v2ray-client", parent=None):
        """
        Initialize settings tab.
        
        Args:
            subscription_manager: SubscriptionManager instance
            config_dir: Configuration directory path
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.subscription_manager = subscription_manager
        self.config_dir = os.path.expanduser(config_dir)
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        self.setLayout(layout)
        
        # Create subscriptions group
        self._create_subscriptions_group(layout)
        
        # Create refresh interval group
        self._create_refresh_interval_group(layout)
        
        # Create theme selection group
        self._create_theme_group(layout)
        
        # Create auto-start group
        self._create_autostart_group(layout)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Load current settings
        self._load_current_settings()
    
    def _create_subscriptions_group(self, parent_layout: QVBoxLayout) -> None:
        """
        Create subscriptions management group.
        
        Args:
            parent_layout: Parent layout to add group to
        """
        group = QGroupBox("Subscription Management")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)
        
        # Subscription list
        self.subscription_list = QListWidget()
        self.subscription_list.setMinimumHeight(150)
        self.subscription_list.setAlternatingRowColors(True)
        group_layout.addWidget(self.subscription_list)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.add_sub_button = QPushButton("➕ Add Subscription")
        self.add_sub_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_sub_button.clicked.connect(self._on_add_subscription)
        buttons_layout.addWidget(self.add_sub_button)
        
        self.add_server_button = QPushButton("📋 Add Server Link")
        self.add_server_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_server_button.clicked.connect(self._on_add_server_link)
        self.add_server_button.setToolTip("Paste a vmess://, vless://, or trojan:// link")
        buttons_layout.addWidget(self.add_server_button)
        
        self.edit_sub_button = QPushButton("✏️ Edit")
        self.edit_sub_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_sub_button.clicked.connect(self._on_edit_subscription)
        self.edit_sub_button.setEnabled(False)
        buttons_layout.addWidget(self.edit_sub_button)
        
        self.remove_sub_button = QPushButton("🗑️ Remove")
        self.remove_sub_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_sub_button.clicked.connect(self._on_remove_subscription)
        self.remove_sub_button.setEnabled(False)
        buttons_layout.addWidget(self.remove_sub_button)
        
        buttons_layout.addStretch()
        
        group_layout.addLayout(buttons_layout)
        
        # Connect selection change
        self.subscription_list.itemSelectionChanged.connect(self._on_subscription_selection_changed)
        
        parent_layout.addWidget(group)
    
    def _create_refresh_interval_group(self, parent_layout: QVBoxLayout) -> None:
        """
        Create refresh interval configuration group.
        
        Args:
            parent_layout: Parent layout to add group to
        """
        group = QGroupBox("Server List Refresh")
        group_layout = QHBoxLayout()
        group.setLayout(group_layout)
        
        label = QLabel("Refresh Interval:")
        group_layout.addWidget(label)
        
        self.interval_spinner = QSpinBox()
        self.interval_spinner.setMinimum(5)
        self.interval_spinner.setMaximum(300)
        self.interval_spinner.setValue(10)
        self.interval_spinner.setSuffix(" seconds")
        self.interval_spinner.valueChanged.connect(self._on_interval_changed)
        group_layout.addWidget(self.interval_spinner)
        
        group_layout.addStretch()
        
        parent_layout.addWidget(group)
    
    def _create_theme_group(self, parent_layout: QVBoxLayout) -> None:
        """
        Create theme selection group.
        
        Args:
            parent_layout: Parent layout to add group to
        """
        group = QGroupBox("Theme Selection")
        group_layout = QHBoxLayout()
        group.setLayout(group_layout)
        
        label = QLabel("Theme:")
        group_layout.addWidget(label)
        
        # Create button group for radio buttons
        self.theme_button_group = QButtonGroup()
        
        # Create radio buttons for each theme
        self.dark_radio = QRadioButton("Dark")
        self.dark_radio.setChecked(True)
        self.theme_button_group.addButton(self.dark_radio, 0)
        group_layout.addWidget(self.dark_radio)
        
        self.light_radio = QRadioButton("Light")
        self.theme_button_group.addButton(self.light_radio, 1)
        group_layout.addWidget(self.light_radio)
        
        self.neon_radio = QRadioButton("Neon")
        self.theme_button_group.addButton(self.neon_radio, 2)
        group_layout.addWidget(self.neon_radio)
        
        # Connect signal
        self.theme_button_group.buttonClicked.connect(self._on_theme_changed)
        
        group_layout.addStretch()
        
        parent_layout.addWidget(group)
    
    def _create_autostart_group(self, parent_layout: QVBoxLayout) -> None:
        """
        Create auto-start configuration group.
        
        Args:
            parent_layout: Parent layout to add group to
        """
        group = QGroupBox("Startup Options")
        group_layout = QHBoxLayout()
        group.setLayout(group_layout)
        
        self.autostart_checkbox = QCheckBox("Auto-start on login")
        group_layout.addWidget(self.autostart_checkbox)
        
        group_layout.addStretch()
        
        parent_layout.addWidget(group)
    
    def _load_current_settings(self) -> None:
        """Load and display current settings"""
        # Load subscriptions
        self._refresh_subscription_list()
    
    def _refresh_subscription_list(self) -> None:
        """Refresh the subscription list display"""
        self.subscription_list.clear()
        
        subscriptions = self.subscription_manager.get_subscriptions()
        
        for sub in subscriptions:
            name = sub.get("name", sub.get("url", "Unknown"))
            url = sub.get("url", "")
            server_count = sub.get("server_count", 0)
            
            # Create display text
            display_text = f"{name} ({server_count} servers)"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, sub)
            self.subscription_list.addItem(item)
    
    def _on_subscription_selection_changed(self) -> None:
        """Handle subscription list selection change"""
        has_selection = len(self.subscription_list.selectedItems()) > 0
        self.edit_sub_button.setEnabled(has_selection)
        self.remove_sub_button.setEnabled(has_selection)
    
    def _on_add_subscription(self) -> None:
        """Handle add subscription button click"""
        dialog = AddSubscriptionDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            url, name = dialog.get_values()
            
            if not url:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter a subscription URL."
                )
                return
            
            # Add subscription
            success = self.subscription_manager.add_subscription(url, name or url)
            
            if success:
                self._refresh_subscription_list()
                self.subscriptions_changed.emit()
                QMessageBox.information(
                    self,
                    "Success",
                    "Subscription added successfully!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Duplicate",
                    "This subscription URL already exists."
                )
    
    def _on_add_server_link(self) -> None:
        """Handle add server link button click"""
        dialog = AddServerLinkDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            link = dialog.get_link()
            
            if not link:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please paste a server link."
                )
                return
            
            # Validate link format
            if not (link.startswith('vmess://') or link.startswith('vless://') or link.startswith('trojan://')):
                QMessageBox.warning(
                    self,
                    "Invalid Link",
                    "Server link must start with vmess://, vless://, or trojan://"
                )
                return
            
            # Parse the server link
            from subscription_manager import ServerParser
            
            server = None
            if link.startswith('vmess://'):
                server = ServerParser.parse_vmess(link)
            elif link.startswith('vless://'):
                server = ServerParser.parse_vless(link)
            elif link.startswith('trojan://'):
                server = ServerParser.parse_trojan(link)
            
            if not server:
                QMessageBox.warning(
                    self,
                    "Parse Error",
                    "Failed to parse server link. Please check the format."
                )
                return
            
            # Save as a special "manual" subscription
            manual_sub_url = f"manual://{server.get('name', 'Manual Server')}"
            
            # Create a manual servers file
            manual_servers_file = os.path.join(self.config_dir, "manual_servers.json")
            
            # Load existing manual servers
            manual_servers = []
            if os.path.exists(manual_servers_file):
                try:
                    with open(manual_servers_file, 'r') as f:
                        manual_servers = json.load(f)
                except:
                    manual_servers = []
            
            # Add new server
            manual_servers.append(server)
            
            # Save manual servers
            try:
                with open(manual_servers_file, 'w') as f:
                    json.dump(manual_servers, f, indent=2)
                
                # Trigger refresh
                self.subscriptions_changed.emit()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Server '{server.get('name', 'Unknown')}' added successfully!"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to save server: {e}"
                )
    
    def _on_edit_subscription(self) -> None:
        """Handle edit subscription button click"""
        selected_items = self.subscription_list.selectedItems()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        subscription = item.data(Qt.ItemDataRole.UserRole)
        
        dialog = EditSubscriptionDialog(subscription, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_name()
            
            # Update subscription name
            subscription["name"] = new_name or subscription.get("url", "")
            
            # Save changes
            self.subscription_manager._save_subscriptions()
            self._refresh_subscription_list()
            
            QMessageBox.information(
                self,
                "Success",
                "Subscription updated successfully!"
            )
    
    def _on_remove_subscription(self) -> None:
        """Handle remove subscription button click"""
        selected_items = self.subscription_list.selectedItems()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        subscription = item.data(Qt.ItemDataRole.UserRole)
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove this subscription?\n\n{subscription.get('name', 'Unknown')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            url = subscription.get("url", "")
            success = self.subscription_manager.remove_subscription(url)
            
            if success:
                self._refresh_subscription_list()
                self.subscriptions_changed.emit()
                QMessageBox.information(
                    self,
                    "Success",
                    "Subscription removed successfully!"
                )
    
    def _on_interval_changed(self, value: int) -> None:
        """
        Handle refresh interval change.
        
        Args:
            value: New interval value in seconds
        """
        self.interval_changed.emit(value)
    
    def _on_theme_changed(self, button: QRadioButton) -> None:
        """
        Handle theme selection change.
        
        Args:
            button: Selected radio button
        """
        if button == self.dark_radio:
            self.theme_changed.emit("dark")
        elif button == self.light_radio:
            self.theme_changed.emit("light")
        elif button == self.neon_radio:
            self.theme_changed.emit("neon")
    
    def set_theme(self, theme_name: str) -> None:
        """
        Set the current theme selection.
        
        Args:
            theme_name: Name of theme to select
        """
        if theme_name == "dark":
            self.dark_radio.setChecked(True)
        elif theme_name == "light":
            self.light_radio.setChecked(True)
        elif theme_name == "neon":
            self.neon_radio.setChecked(True)
    
    def set_interval(self, seconds: int) -> None:
        """
        Set the refresh interval value.
        
        Args:
            seconds: Interval in seconds
        """
        self.interval_spinner.setValue(seconds)
    
    def set_autostart(self, enabled: bool) -> None:
        """
        Set the auto-start checkbox state.
        
        Args:
            enabled: True to enable auto-start
        """
        self.autostart_checkbox.setChecked(enabled)
    
    def get_autostart(self) -> bool:
        """
        Get the auto-start checkbox state.
        
        Returns:
            True if auto-start is enabled
        """
        return self.autostart_checkbox.isChecked()
    
    def save_settings(self) -> bool:
        """
        Save current settings to JSON file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Determine current theme
            current_theme = "dark"
            if self.light_radio.isChecked():
                current_theme = "light"
            elif self.neon_radio.isChecked():
                current_theme = "neon"
            
            # Build settings dictionary
            settings = {
                "theme": current_theme,
                "refresh_interval": self.interval_spinner.value(),
                "auto_start": self.autostart_checkbox.isChecked()
            }
            
            # Write to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self) -> dict:
        """
        Load settings from JSON file.
        
        Returns:
            Dictionary of settings, or default settings if file doesn't exist
        """
        default_settings = {
            "theme": "dark",
            "refresh_interval": 10,
            "auto_start": False
        }
        
        if not os.path.exists(self.settings_file):
            return default_settings
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Merge with defaults to handle missing keys
            return {**default_settings, **settings}
            
        except json.JSONDecodeError:
            print("Warning: Settings file is corrupted, using defaults")
            return default_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
    
    def apply_loaded_settings(self, settings: dict) -> None:
        """
        Apply loaded settings to UI controls.
        
        Args:
            settings: Dictionary of settings to apply
        """
        # Apply theme
        theme = settings.get("theme", "dark")
        self.set_theme(theme)
        
        # Apply refresh interval
        interval = settings.get("refresh_interval", 10)
        self.set_interval(interval)
        
        # Apply auto-start
        auto_start = settings.get("auto_start", False)
        self.set_autostart(auto_start)
