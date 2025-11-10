"""
Server Card Widget

Displays individual server information with flag, ping, and connect button.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QColor
from pathlib import Path
from ui.animated_button import AnimatedConnectButton


class ServerCard(QWidget):
    """Widget displaying server information with connect button."""
    
    connect_clicked = pyqtSignal(dict)  # Emits server configuration
    
    def __init__(self, server: dict, parent=None):
        """
        Initialize server card with server data.
        
        Args:
            server: Dictionary containing server configuration
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.server = server
        self.is_connected_state = False
        
        # Set object name for styling
        self.setObjectName("ServerCard")
        self.setProperty("class", "ServerCard")
        
        # Set fixed size for card
        self.setFixedSize(220, 180)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Server name with flag
        name_layout = QHBoxLayout()
        name_layout.setSpacing(8)
        
        # Flag icon
        self.flag_label = QLabel()
        self.flag_label.setFixedSize(24, 24)
        self._load_flag_icon()
        name_layout.addWidget(self.flag_label)
        
        # Server name
        self.name_label = QLabel(server.get("name", "Unknown"))
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.name_label.setWordWrap(True)
        name_layout.addWidget(self.name_label, 1)
        
        layout.addLayout(name_layout)
        
        # Server IP and port
        ip_port = f"{server.get('ip', 'N/A')}:{server.get('port', 'N/A')}"
        self.ip_label = QLabel(ip_port)
        self.ip_label.setStyleSheet("font-size: 11px; color: #b0b0ff;")
        layout.addWidget(self.ip_label)
        
        # Protocol type
        protocol = server.get("type", "unknown").upper()
        self.protocol_label = QLabel(f"Protocol: {protocol}")
        self.protocol_label.setStyleSheet("font-size: 10px; color: #9090dd;")
        layout.addWidget(self.protocol_label)
        
        # Ping visualization
        ping_layout = QVBoxLayout()
        ping_layout.setSpacing(4)
        
        self.ping_label = QLabel("Ping: --")
        self.ping_label.setStyleSheet("font-size: 11px;")
        ping_layout.addWidget(self.ping_label)
        
        # Ping bar
        self.ping_bar = QWidget()
        self.ping_bar.setFixedHeight(8)
        self.ping_bar.setStyleSheet("""
            background-color: rgba(50, 50, 70, 0.5);
            border-radius: 4px;
        """)
        ping_layout.addWidget(self.ping_bar)
        
        layout.addLayout(ping_layout)
        
        # Spacer
        layout.addStretch()
        
        # Connect button with animation
        self.connect_button = AnimatedConnectButton("Connect")
        self.connect_button.setObjectName("connectButton")
        self.connect_button.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_button)
        
        # Update ping if available
        if "ping" in server and server["ping"] > 0:
            self.update_ping(server["ping"])
        
        # Enable hover effects
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
    
    def _load_flag_icon(self) -> None:
        """Load country flag icon for the server."""
        country_code = self.server.get("country_code", "").lower()
        
        if not country_code:
            # Try to extract from name if it contains emoji or country code
            name = self.server.get("name", "")
            # For now, show placeholder
            self.flag_label.setText("🌐")
            self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return
        
        # Try to load flag icon from ui/icons/flags/
        flag_path = Path(__file__).parent / "icons" / "flags" / f"{country_code}.png"
        
        if flag_path.exists():
            pixmap = QPixmap(str(flag_path))
            scaled_pixmap = pixmap.scaled(
                24, 24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.flag_label.setPixmap(scaled_pixmap)
        else:
            # Use emoji or placeholder
            self.flag_label.setText("🌐")
            self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def update_ping(self, ping_ms: int) -> None:
        """
        Update ping display with latency value.
        
        Args:
            ping_ms: Ping latency in milliseconds (-1 if unreachable)
        """
        if ping_ms < 0:
            self.ping_label.setText("Ping: Timeout")
            self.ping_label.setStyleSheet("font-size: 11px; color: #ff6b6b;")
            self._update_ping_bar(0)
        else:
            self.ping_label.setText(f"Ping: {ping_ms}ms")
            
            # Color code based on ping
            if ping_ms < 50:
                color = "#38ef7d"  # Green - excellent
            elif ping_ms < 100:
                color = "#90ee90"  # Light green - good
            elif ping_ms < 200:
                color = "#ffd700"  # Yellow - fair
            else:
                color = "#ff6b6b"  # Red - poor
            
            self.ping_label.setStyleSheet(f"font-size: 11px; color: {color};")
            
            # Update ping bar (inverse scale: lower ping = fuller bar)
            # Max 300ms for scale
            bar_percentage = max(0, min(100, 100 - (ping_ms / 3)))
            self._update_ping_bar(bar_percentage)
    
    def _update_ping_bar(self, percentage: float) -> None:
        """
        Update ping bar visualization.
        
        Args:
            percentage: Fill percentage (0-100)
        """
        # Determine color based on percentage
        if percentage > 66:
            color = "#38ef7d"  # Green
        elif percentage > 33:
            color = "#ffd700"  # Yellow
        else:
            color = "#ff6b6b"  # Red
        
        # Create gradient background
        self.ping_bar.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color},
                    stop:{percentage/100} {color},
                    stop:{percentage/100} rgba(50, 50, 70, 0.5),
                    stop:1 rgba(50, 50, 70, 0.5)
                );
                border-radius: 4px;
            }}
        """)
    
    def set_connected(self, connected: bool, animate: bool = True) -> None:
        """
        Update visual state for connection status.
        
        Args:
            connected: True if this server is currently connected
            animate: Whether to animate the transition
        """
        # Animate transition if requested
        if animate and self.is_connected_state != connected:
            from_state = "connected" if self.is_connected_state else "disconnected"
            to_state = "connected" if connected else "disconnected"
            self.connect_button.animate_transition(from_state, to_state)
        
        self.is_connected_state = connected
        
        if connected:
            self.connect_button.setText("Disconnect")
            self.connect_button.setObjectName("disconnectButton")
            # Force style refresh
            self.connect_button.style().unpolish(self.connect_button)
            self.connect_button.style().polish(self.connect_button)
            
            # Add connected indicator to card
            self.setStyleSheet("""
                #ServerCard {
                    border: 2px solid rgba(56, 239, 125, 0.8);
                }
            """)
        else:
            self.connect_button.setText("Connect")
            self.connect_button.setObjectName("connectButton")
            # Force style refresh
            self.connect_button.style().unpolish(self.connect_button)
            self.connect_button.style().polish(self.connect_button)
            
            # Remove connected indicator
            self.setStyleSheet("")
    
    def set_loading(self, loading: bool) -> None:
        """
        Set loading state on connect button.
        
        Args:
            loading: True to show loading spinner
        """
        self.connect_button.set_loading(loading)
    
    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        self.connect_clicked.emit(self.server)
    
    def enterEvent(self, event) -> None:
        """Handle mouse enter for hover effect."""
        super().enterEvent(event)
        # Hover effect is handled by QSS
    
    def leaveEvent(self, event) -> None:
        """Handle mouse leave."""
        super().leaveEvent(event)
        # Hover effect is handled by QSS
