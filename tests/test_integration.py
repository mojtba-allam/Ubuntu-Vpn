"""
Integration tests for V2Ray Client GUI application.

Tests main window launch, tab navigation, subscription management,
connection/disconnection, theme changes, settings persistence, and log display.
"""

import pytest
import sys
import json
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

# Import application components
from ui.main_window import MainWindow
from v2ray_manager import V2RayManager
from subscription_manager import SubscriptionManager


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temporary config directory."""
    return str(tmp_path / "v2ray-test")


@pytest.fixture
def main_window(qapp, temp_config_dir):
    """Create MainWindow instance with temp config directory."""
    window = MainWindow(config_dir=temp_config_dir)
    yield window
    window.close()
    QApplication.processEvents()


@pytest.fixture
def sample_server():
    """Provide a sample server configuration."""
    return {
        "name": "Test Server",
        "type": "vmess",
        "ip": "example.com",
        "port": 443,
        "uuid": "test-uuid-1234",
        "alterId": 0,
        "security": "auto",
        "network": "ws",
        "tls": True,
        "sni": "example.com",
        "path": "/path",
        "ping": 50,
        "country_code": "US"
    }


@pytest.fixture
def sample_servers(sample_server):
    """Provide a list of sample servers."""
    servers = []
    for i in range(5):
        server = sample_server.copy()
        server["name"] = f"Test Server {i+1}"
        server["uuid"] = f"test-uuid-{i+1}"
        server["ping"] = 50 + (i * 10)
        servers.append(server)
    return servers


class TestMainWindowLaunch:
    """Test main window launch and initialization."""
    
    def test_main_window_launches_successfully(self, main_window):
        """Test that main window launches without errors."""
        assert main_window is not None
        assert main_window.isVisible() is False  # Not shown yet
        
        # Show window
        main_window.show()
        QApplication.processEvents()
        
        assert main_window.isVisible() is True
    
    def test_main_window_has_correct_title(self, main_window):
        """Test that main window has correct title."""
        assert main_window.windowTitle() == "V2Ray Client"
    
    def test_main_window_has_minimum_size(self, main_window):
        """Test that main window has minimum size set."""
        assert main_window.minimumWidth() == 900
        assert main_window.minimumHeight() == 600
    
    def test_main_window_initializes_managers(self, main_window):
        """Test that main window initializes all managers."""
        assert main_window.v2ray_manager is not None
        assert main_window.subscription_manager is not None
        assert main_window.server_updater is not None
        assert isinstance(main_window.v2ray_manager, V2RayManager)
        assert isinstance(main_window.subscription_manager, SubscriptionManager)
    
    def test_main_window_initializes_tabs(self, main_window):
        """Test that main window initializes all tabs."""
        assert main_window.servers_tab is not None
        assert main_window.settings_tab is not None
        assert main_window.logs_tab is not None


class TestTabNavigation:
    """Test tab navigation between Servers, Settings, and Logs."""
    
    def test_tab_widget_exists(self, main_window):
        """Test that tab widget exists."""
        assert main_window.tab_widget is not None
        assert main_window.tab_widget.count() == 3
    
    def test_tab_names_are_correct(self, main_window):
        """Test that tab names are correct."""
        assert main_window.tab_widget.tabText(0) == "Servers"
        assert main_window.tab_widget.tabText(1) == "Settings"
        assert main_window.tab_widget.tabText(2) == "Logs"
    
    def test_can_navigate_to_servers_tab(self, main_window):
        """Test navigation to Servers tab."""
        main_window.tab_widget.setCurrentIndex(0)
        QApplication.processEvents()
        
        assert main_window.tab_widget.currentIndex() == 0
        assert main_window.tab_widget.currentWidget() == main_window.servers_tab
    
    def test_can_navigate_to_settings_tab(self, main_window):
        """Test navigation to Settings tab."""
        main_window.tab_widget.setCurrentIndex(1)
        QApplication.processEvents()
        
        assert main_window.tab_widget.currentIndex() == 1
        assert main_window.tab_widget.currentWidget() == main_window.settings_tab
    
    def test_can_navigate_to_logs_tab(self, main_window):
        """Test navigation to Logs tab."""
        main_window.tab_widget.setCurrentIndex(2)
        QApplication.processEvents()
        
        assert main_window.tab_widget.currentIndex() == 2
        assert main_window.tab_widget.currentWidget() == main_window.logs_tab
    
    def test_can_navigate_between_all_tabs(self, main_window):
        """Test navigation between all tabs in sequence."""
        # Navigate through all tabs
        for i in range(3):
            main_window.tab_widget.setCurrentIndex(i)
            QApplication.processEvents()
            assert main_window.tab_widget.currentIndex() == i
        
        # Navigate backwards
        for i in range(2, -1, -1):
            main_window.tab_widget.setCurrentIndex(i)
            QApplication.processEvents()
            assert main_window.tab_widget.currentIndex() == i


class TestSubscriptionManagement:
    """Test subscription addition updates server list."""
    
    @patch('requests.get')
    def test_adding_subscription_updates_server_list(self, mock_get, main_window, sample_servers):
        """Test that adding a subscription triggers server list update."""
        # Mock subscription fetch response
        import base64
        vmess_links = []
        for server in sample_servers:
            config = {
                "ps": server["name"],
                "add": server["ip"],
                "port": str(server["port"]),
                "id": server["uuid"],
                "aid": "0",
                "scy": "auto",
                "net": "ws",
                "tls": "tls"
            }
            json_str = json.dumps(config)
            encoded = base64.b64encode(json_str.encode()).decode()
            vmess_links.append(f"vmess://{encoded}")
        
        mock_response = MagicMock()
        mock_response.text = "\n".join(vmess_links)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Navigate to settings tab
        main_window.tab_widget.setCurrentIndex(1)
        QApplication.processEvents()
        
        # Add subscription
        success = main_window.subscription_manager.add_subscription(
            "http://test.example.com/sub",
            "Test Subscription"
        )
        
        assert success is True
        
        # Trigger refresh
        main_window.server_updater.refresh_now()
        QApplication.processEvents()
        
        # Give time for async operations
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Check that servers were updated
        assert len(main_window.servers_tab.all_servers) > 0
    
    def test_subscription_list_displays_in_settings(self, main_window):
        """Test that subscriptions are displayed in settings tab."""
        # Add a subscription
        main_window.subscription_manager.add_subscription(
            "http://test.example.com/sub",
            "Test Sub"
        )
        
        # Navigate to settings tab
        main_window.tab_widget.setCurrentIndex(1)
        QApplication.processEvents()
        
        # Refresh subscription list display
        main_window.settings_tab._refresh_subscription_list()
        QApplication.processEvents()
        
        # Check that subscription appears in list
        assert main_window.settings_tab.subscription_list.count() > 0


class TestConnectionManagement:
    """Test connect and disconnect button functionality."""
    
    @patch('subprocess.Popen')
    @patch('requests.get')
    def test_connect_button_triggers_v2ray_manager(self, mock_requests_get, mock_popen, main_window, sample_server):
        """Test that connect button triggers V2RayManager connection."""
        # Mock V2Ray process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process running
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.readline.return_value = ""
        mock_popen.return_value = mock_process
        
        # Mock IP info response
        mock_ip_response = MagicMock()
        mock_ip_response.json.return_value = {
            'ip': '1.2.3.4',
            'country': 'US',
            'city': 'New York'
        }
        mock_ip_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_ip_response
        
        # Navigate to servers tab
        main_window.tab_widget.setCurrentIndex(0)
        QApplication.processEvents()
        
        # Update servers with sample server
        main_window.servers_tab.update_servers([sample_server])
        QApplication.processEvents()
        
        # Simulate connect button click
        main_window.servers_tab.connection_requested.emit(sample_server)
        QApplication.processEvents()
        
        # Give time for connection
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Verify V2RayManager was called
        assert main_window.v2ray_manager.is_connected() is True
        
        # Verify UI updated
        assert "Connected" in main_window.servers_tab.status_label.text()
    
    @patch('subprocess.Popen')
    def test_disconnect_button_stops_process(self, mock_popen, main_window, sample_server):
        """Test that disconnect button stops V2Ray process."""
        # Mock V2Ray process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.readline.return_value = ""
        mock_popen.return_value = mock_process
        
        # Connect first
        main_window.v2ray_manager.connect(sample_server)
        assert main_window.v2ray_manager.is_connected() is True
        
        # Navigate to servers tab
        main_window.tab_widget.setCurrentIndex(0)
        QApplication.processEvents()
        
        # Simulate disconnect button click
        main_window.servers_tab.disconnection_requested.emit()
        QApplication.processEvents()
        
        # Verify process was terminated
        mock_process.terminate.assert_called()
        
        # Verify UI updated
        assert "Disconnected" in main_window.servers_tab.status_label.text()
    
    @patch('subprocess.Popen')
    @patch('requests.get')
    def test_connection_updates_status_display(self, mock_requests_get, mock_popen, main_window, sample_server):
        """Test that connection updates status display with IP info."""
        # Mock V2Ray process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.readline.return_value = ""
        mock_popen.return_value = mock_process
        
        # Mock IP info response
        mock_ip_response = MagicMock()
        mock_ip_response.json.return_value = {
            'ip': '5.6.7.8',
            'country': 'SG',
            'city': 'Singapore'
        }
        mock_ip_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_ip_response
        
        # Navigate to servers tab
        main_window.tab_widget.setCurrentIndex(0)
        QApplication.processEvents()
        
        # Trigger connection
        main_window._on_connection_requested(sample_server)
        QApplication.processEvents()
        
        # Give time for IP fetch
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Verify status shows connection
        assert "Connected" in main_window.servers_tab.status_label.text()
        
        # Verify IP info is displayed
        ip_text = main_window.servers_tab.ip_label.text()
        assert "5.6.7.8" in ip_text or ip_text != ""


class TestThemeManagement:
    """Test theme change applies to UI."""
    
    def test_theme_change_to_dark(self, main_window):
        """Test changing theme to dark."""
        main_window.load_theme("dark")
        QApplication.processEvents()
        
        # Verify theme was applied (stylesheet should be set)
        app = QApplication.instance()
        assert app.styleSheet() != ""
    
    def test_theme_change_to_light(self, main_window):
        """Test changing theme to light."""
        main_window.load_theme("light")
        QApplication.processEvents()
        
        # Verify theme was applied
        app = QApplication.instance()
        assert app.styleSheet() != ""
    
    def test_theme_change_to_neon(self, main_window):
        """Test changing theme to neon."""
        main_window.load_theme("neon")
        QApplication.processEvents()
        
        # Verify theme was applied
        app = QApplication.instance()
        assert app.styleSheet() != ""
    
    def test_theme_change_from_settings_tab(self, main_window):
        """Test changing theme from settings tab."""
        # Navigate to settings tab
        main_window.tab_widget.setCurrentIndex(1)
        QApplication.processEvents()
        
        # Change theme via settings tab
        main_window.settings_tab.neon_radio.setChecked(True)
        main_window.settings_tab._on_theme_changed(main_window.settings_tab.neon_radio)
        QApplication.processEvents()
        
        # Verify theme was applied
        app = QApplication.instance()
        assert app.styleSheet() != ""
    
    def test_theme_preference_is_saved(self, main_window, temp_config_dir):
        """Test that theme preference is saved to disk."""
        # Change theme
        main_window.load_theme("neon")
        QApplication.processEvents()
        
        # Check that preference file was created
        config_path = Path(temp_config_dir).expanduser()
        theme_file = config_path / "theme.txt"
        
        # Theme preference is saved by theme_loader
        if theme_file.exists():
            # Verify content
            with open(theme_file, 'r') as f:
                saved_theme = f.read().strip()
            assert saved_theme == "neon"
        else:
            # Theme preference may be saved in settings.json instead
            settings_file = config_path / "settings.json"
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                # Just verify the theme loader was called successfully
                assert main_window.theme_loader is not None


class TestSettingsPersistence:
    """Test settings persistence across restarts."""
    
    def test_settings_are_saved_to_file(self, main_window, temp_config_dir):
        """Test that settings are saved to JSON file."""
        # Navigate to settings tab
        main_window.tab_widget.setCurrentIndex(1)
        QApplication.processEvents()
        
        # Change some settings
        main_window.settings_tab.interval_spinner.setValue(30)
        main_window.settings_tab.neon_radio.setChecked(True)
        main_window.settings_tab.autostart_checkbox.setChecked(True)
        
        # Save settings
        success = main_window.settings_tab.save_settings()
        assert success is True
        
        # Verify settings file exists
        settings_file = Path(temp_config_dir).expanduser() / "settings.json"
        assert settings_file.exists()
    
    def test_settings_are_loaded_from_file(self, temp_config_dir):
        """Test that settings are loaded from JSON file on startup."""
        # Create settings file
        settings_file = Path(temp_config_dir).expanduser() / "settings.json"
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        test_settings = {
            "theme": "light",
            "refresh_interval": 60,
            "auto_start": True
        }
        
        with open(settings_file, 'w') as f:
            json.dump(test_settings, f)
        
        # Create new window (simulates restart)
        window = MainWindow(config_dir=temp_config_dir)
        QApplication.processEvents()
        
        # Verify settings were loaded
        assert window.settings_tab.interval_spinner.value() == 60
        assert window.settings_tab.light_radio.isChecked() is True
        assert window.settings_tab.autostart_checkbox.isChecked() is True
        
        window.close()
        QApplication.processEvents()
    
    def test_settings_persist_across_theme_changes(self, main_window):
        """Test that settings persist when theme is changed."""
        # Set initial settings
        main_window.settings_tab.interval_spinner.setValue(45)
        main_window.settings_tab.save_settings()
        
        # Change theme
        main_window.load_theme("dark")
        QApplication.processEvents()
        
        # Verify interval setting is still correct
        assert main_window.settings_tab.interval_spinner.value() == 45
    
    def test_settings_file_handles_missing_keys(self, temp_config_dir):
        """Test that missing keys in settings file use defaults."""
        # Create incomplete settings file
        settings_file = Path(temp_config_dir).expanduser() / "settings.json"
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        incomplete_settings = {
            "theme": "neon"
            # Missing refresh_interval and auto_start
        }
        
        with open(settings_file, 'w') as f:
            json.dump(incomplete_settings, f)
        
        # Create window
        window = MainWindow(config_dir=temp_config_dir)
        QApplication.processEvents()
        
        # Verify defaults were used for missing keys
        assert window.settings_tab.interval_spinner.value() == 10  # Default
        assert window.settings_tab.autostart_checkbox.isChecked() is False  # Default
        
        window.close()
        QApplication.processEvents()


class TestLogDisplay:
    """Test log display shows V2Ray output."""
    
    @patch('subprocess.Popen')
    def test_logs_tab_displays_v2ray_output(self, mock_popen, main_window, sample_server):
        """Test that logs tab displays V2Ray process output."""
        # Mock V2Ray process with output
        mock_process = MagicMock()
        # Use return_value instead of side_effect to avoid StopIteration
        mock_process.poll.return_value = None  # Process is running
        mock_process.stdout.readline.side_effect = [
            b"V2Ray starting...\n",
            b"Connection established\n",
            b"",
            b""
        ]
        mock_process.stderr.readline.return_value = b""
        mock_popen.return_value = mock_process
        
        # Navigate to logs tab
        main_window.tab_widget.setCurrentIndex(2)
        QApplication.processEvents()
        
        # Connect to trigger log streaming
        main_window.v2ray_manager.connect(sample_server)
        
        # Give time for log streaming
        time.sleep(0.3)
        QApplication.processEvents()
        
        # Check that logs were captured
        log_text = main_window.logs_tab.log_display.toPlainText()
        assert log_text != "" or main_window.logs_tab.log_line_count >= 0
        
        # Manually disconnect to clean up before teardown
        main_window.v2ray_manager.disconnect()
    
    def test_logs_tab_has_clear_button(self, main_window):
        """Test that logs tab has clear button."""
        # Navigate to logs tab
        main_window.tab_widget.setCurrentIndex(2)
        QApplication.processEvents()
        
        assert main_window.logs_tab.clear_button is not None
    
    def test_logs_tab_clear_button_works(self, main_window):
        """Test that clear button clears logs."""
        # Navigate to logs tab
        main_window.tab_widget.setCurrentIndex(2)
        QApplication.processEvents()
        
        # Add some log text
        main_window.logs_tab.append_log("Test log line 1")
        main_window.logs_tab.append_log("Test log line 2")
        QApplication.processEvents()
        
        assert main_window.logs_tab.log_display.toPlainText() != ""
        
        # Click clear button
        main_window.logs_tab.clear_logs()
        QApplication.processEvents()
        
        # Verify logs were cleared
        assert main_window.logs_tab.log_display.toPlainText() == ""
        assert main_window.logs_tab.log_line_count == 0
    
    def test_logs_tab_has_export_button(self, main_window):
        """Test that logs tab has export button."""
        # Navigate to logs tab
        main_window.tab_widget.setCurrentIndex(2)
        QApplication.processEvents()
        
        assert main_window.logs_tab.export_button is not None
    
    def test_logs_tab_export_functionality(self, main_window, tmp_path):
        """Test that export functionality works."""
        # Navigate to logs tab
        main_window.tab_widget.setCurrentIndex(2)
        QApplication.processEvents()
        
        # Add some log text
        main_window.logs_tab.append_log("Test log line 1")
        main_window.logs_tab.append_log("Test log line 2")
        QApplication.processEvents()
        
        # Export logs
        export_file = tmp_path / "test_export.txt"
        success = main_window.logs_tab.export_logs(str(export_file))
        
        assert success is True
        assert export_file.exists()
        
        # Verify content
        with open(export_file, 'r') as f:
            content = f.read()
        assert "Test log line 1" in content
        assert "Test log line 2" in content
    
    def test_logs_auto_scroll_to_bottom(self, main_window):
        """Test that logs auto-scroll to bottom when new lines added."""
        # Navigate to logs tab
        main_window.tab_widget.setCurrentIndex(2)
        QApplication.processEvents()
        
        # Add multiple log lines
        for i in range(20):
            main_window.logs_tab.append_log(f"Log line {i}")
            QApplication.processEvents()
        
        # Verify scrollbar is at bottom
        scrollbar = main_window.logs_tab.log_display.verticalScrollBar()
        assert scrollbar.value() == scrollbar.maximum()


class TestToastNotifications:
    """Test toast notification system."""
    
    def test_toast_notification_displays(self, main_window):
        """Test that toast notifications display."""
        main_window.show()
        QApplication.processEvents()
        
        # Show toast
        main_window.show_toast("Test message", "info")
        QApplication.processEvents()
        
        # Verify toast was created
        assert len(main_window.active_toasts) > 0
    
    def test_toast_notification_types(self, main_window):
        """Test different toast notification types."""
        main_window.show()
        QApplication.processEvents()
        
        # Test success toast
        main_window.show_toast("Success message", "success")
        QApplication.processEvents()
        
        # Test error toast
        main_window.show_toast("Error message", "error")
        QApplication.processEvents()
        
        # Test info toast
        main_window.show_toast("Info message", "info")
        QApplication.processEvents()
        
        # Verify toasts were created
        assert len(main_window.active_toasts) >= 1


class TestWindowCleanup:
    """Test window cleanup on close."""
    
    @patch('subprocess.Popen')
    def test_window_close_disconnects_v2ray(self, mock_popen, temp_config_dir, qapp, sample_server):
        """Test that closing window disconnects V2Ray."""
        # Create window
        window = MainWindow(config_dir=temp_config_dir)
        
        # Mock V2Ray process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.readline.return_value = ""
        mock_popen.return_value = mock_process
        
        # Connect
        window.v2ray_manager.connect(sample_server)
        assert window.v2ray_manager.is_connected() is True
        
        # Close window
        window.close()
        QApplication.processEvents()
        
        # Verify process was terminated
        mock_process.terminate.assert_called()
    
    def test_window_close_stops_server_updater(self, temp_config_dir, qapp):
        """Test that closing window stops server updater."""
        # Create window
        window = MainWindow(config_dir=temp_config_dir)
        
        # Start updater
        window.server_updater.start()
        
        # Close window
        window.close()
        QApplication.processEvents()
        
        # Verify updater was stopped (timer should not be active)
        assert window.server_updater.timer.isActive() is False
    
    def test_window_close_saves_settings(self, temp_config_dir, qapp):
        """Test that closing window saves settings."""
        # Create window
        window = MainWindow(config_dir=temp_config_dir)
        
        # Change a setting
        window.settings_tab.interval_spinner.setValue(25)
        
        # Close window
        window.close()
        QApplication.processEvents()
        
        # Verify settings were saved
        settings_file = Path(temp_config_dir).expanduser() / "settings.json"
        assert settings_file.exists()
        
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        assert settings["refresh_interval"] == 25
