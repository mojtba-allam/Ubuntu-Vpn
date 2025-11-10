"""
Servers Tab Widget

Displays server list with search, refresh, and connection controls.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QGridLayout, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from ui.server_card import ServerCard
from v2ray_manager import V2RayManager


class ServersTab(QWidget):
    """Main servers tab widget with server list and controls."""
    
    connection_requested = pyqtSignal(dict)  # Emits server config
    disconnection_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    
    def __init__(self, v2ray_manager: V2RayManager, parent=None):
        """
        Initialize servers tab.
        
        Args:
            v2ray_manager: V2RayManager instance for connection management
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.v2ray_manager = v2ray_manager
        self.server_cards = []
        self.all_servers = []
        self.connected_server = None
        self.sort_by = "ping"  # Default sort by ping
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.setLayout(layout)
        
        # Create top control bar
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search servers...")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self._on_search_changed)
        control_layout.addWidget(self.search_input, 1)
        
        # Sort button
        self.sort_button = QPushButton("⬇️ Sort by Ping")
        self.sort_button.setFixedHeight(36)
        self.sort_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_button.clicked.connect(self._on_sort_clicked)
        control_layout.addWidget(self.sort_button)
        
        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setFixedHeight(36)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        control_layout.addWidget(self.refresh_button)
        
        layout.addLayout(control_layout)
        
        # Connection status bar
        self.status_bar = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(12, 8, 12, 8)
        self.status_bar.setLayout(status_layout)
        
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.ip_label = QLabel("")
        self.ip_label.setStyleSheet("font-size: 12px; color: #b0b0ff;")
        status_layout.addWidget(self.ip_label)
        
        self.status_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(106, 17, 203, 0.2), stop:1 rgba(37, 117, 252, 0.2)
                );
                border-radius: 8px;
            }
        """)
        
        layout.addWidget(self.status_bar)
        
        # Create scroll area for server cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Create container widget for grid
        self.container_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.container_widget.setLayout(self.grid_layout)
        
        scroll_area.setWidget(self.container_widget)
        layout.addWidget(scroll_area)
        
        # Empty state label
        self.empty_label = QLabel("Loading servers...\nPlease wait while we fetch your subscriptions.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            font-size: 14px;
            color: #9090dd;
            padding: 40px;
        """)
        self.empty_label.show()  # Show by default
        layout.addWidget(self.empty_label)
    
    def update_servers(self, servers: list[dict]) -> None:
        """
        Refresh server list display.
        
        Args:
            servers: List of server configuration dictionaries
        """
        # Store all servers
        self.all_servers = servers
        
        # Apply sorting
        if self.sort_by == "ping":
            # Sort by ping, putting unreachable servers (-1) at the end
            servers = sorted(servers, key=lambda s: (s.get("ping", -1) == -1, s.get("ping", -1)))
        else:
            # Sort alphabetically by name
            servers = sorted(servers, key=lambda s: s.get("name", "").lower())
        
        # Apply current search filter
        search_text = self.search_input.text().lower()
        if search_text:
            filtered_servers = [
                s for s in servers
                if search_text in s.get("name", "").lower() or
                   search_text in s.get("ip", "").lower() or
                   search_text in s.get("country_code", "").lower()
            ]
        else:
            filtered_servers = servers
        
        # Clear existing cards
        self._clear_server_cards()
        
        # Show/hide empty state
        if not filtered_servers:
            if not self.all_servers:
                self.empty_label.setText("No servers available.\nAdd a subscription in Settings to get started.")
            else:
                self.empty_label.setText("No servers match your search.")
            self.empty_label.show()
            self.container_widget.hide()
            return
        else:
            self.empty_label.hide()
            self.container_widget.show()
        
        # Create new server cards in grid layout
        cards_per_row = 3
        
        for index, server in enumerate(filtered_servers):
            card = ServerCard(server)
            card.connect_clicked.connect(self._on_server_connect_clicked)
            
            # Update connection state if this is the connected server
            if self.connected_server and self._is_same_server(server, self.connected_server):
                card.set_connected(True)
            
            row = index // cards_per_row
            col = index % cards_per_row
            
            self.grid_layout.addWidget(card, row, col)
            self.server_cards.append(card)
        
        # Add stretch to push cards to top
        self.grid_layout.setRowStretch(len(filtered_servers) // cards_per_row + 1, 1)
    
    def set_connection_status(self, connected: bool, server_name: str = "", ip_info: dict = None) -> None:
        """
        Update connection status display.
        
        Args:
            connected: True if connected to a server
            server_name: Name of connected server
            ip_info: Dictionary with IP information (ip, country, city)
        """
        if connected:
            self.status_label.setText(f"Status: Connected to {server_name}")
            self.status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #38ef7d;")
            
            if ip_info:
                ip_text = f"IP: {ip_info.get('ip', 'N/A')}"
                if ip_info.get('city') or ip_info.get('country'):
                    location = f"{ip_info.get('city', '')}, {ip_info.get('country', '')}".strip(', ')
                    ip_text += f" ({location})"
                self.ip_label.setText(ip_text)
            
            self.status_bar.setStyleSheet("""
                QWidget {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(17, 153, 142, 0.3), stop:1 rgba(56, 239, 125, 0.3)
                    );
                    border-radius: 8px;
                    border: 2px solid rgba(56, 239, 125, 0.5);
                }
            """)
        else:
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #ff6b6b;")
            self.ip_label.setText("")
            
            self.status_bar.setStyleSheet("""
                QWidget {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(106, 17, 203, 0.2), stop:1 rgba(37, 117, 252, 0.2)
                    );
                    border-radius: 8px;
                }
            """)
            
            # Update all cards to show disconnected state
            for card in self.server_cards:
                card.set_connected(False)
            
            self.connected_server = None
    
    def _on_search_changed(self, text: str) -> None:
        """
        Handle search text change.
        
        Args:
            text: Search text
        """
        # Re-filter and update display
        self.update_servers(self.all_servers)
    
    def _on_refresh_clicked(self) -> None:
        """Handle refresh button click."""
        # Disable button and show loading state
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("🔄 Refreshing...")
        
        # Re-enable after 2 seconds
        QTimer.singleShot(2000, self._reset_refresh_button)
        
        self.refresh_requested.emit()
    
    def _reset_refresh_button(self) -> None:
        """Reset refresh button to normal state."""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("🔄 Refresh")
    
    def _on_sort_clicked(self) -> None:
        """Handle sort button click - toggle between ping and name."""
        if self.sort_by == "ping":
            self.sort_by = "name"
            self.sort_button.setText("🔤 Sort by Name")
        else:
            self.sort_by = "ping"
            self.sort_button.setText("⬇️ Sort by Ping")
        
        # Re-display servers with new sort order
        self.update_servers(self.all_servers)
    
    def _on_server_connect_clicked(self, server: dict) -> None:
        """
        Handle server card connect button click.
        
        Args:
            server: Server configuration dictionary
        """
        # Check if clicking on currently connected server (disconnect)
        if self.connected_server and self._is_same_server(server, self.connected_server):
            self.disconnection_requested.emit()
        else:
            # Request connection to new server
            self.connected_server = server
            self.connection_requested.emit(server)
    
    def _clear_server_cards(self) -> None:
        """Clear all server cards from grid layout."""
        # Remove all widgets from grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.server_cards.clear()
    
    def _is_same_server(self, server1: dict, server2: dict) -> bool:
        """
        Check if two server configurations represent the same server.
        
        Args:
            server1: First server configuration
            server2: Second server configuration
            
        Returns:
            True if servers are the same
        """
        return (
            server1.get("ip") == server2.get("ip") and
            server1.get("port") == server2.get("port") and
            server1.get("uuid") == server2.get("uuid")
        )
