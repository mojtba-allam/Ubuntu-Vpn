"""
Animated Connection Button

Provides animated button with color transitions and loading spinner.
"""

from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen


class AnimatedConnectButton(QPushButton):
    """Button with color transition animation and loading state."""
    
    def __init__(self, text: str = "Connect", parent=None):
        """
        Initialize animated button.
        
        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        self._is_loading = False
        self._loading_angle = 0
        self._loading_timer = QTimer()
        self._loading_timer.timeout.connect(self._update_loading_animation)
        
        # Animation for color transition
        self._transition_progress = 0.0
        self._transition_animation = None
        
        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def set_loading(self, loading: bool) -> None:
        """
        Set loading state with spinner animation.
        
        Args:
            loading: True to show loading spinner
        """
        self._is_loading = loading
        
        if loading:
            self.setEnabled(False)
            self._loading_timer.start(50)  # Update every 50ms
        else:
            self.setEnabled(True)
            self._loading_timer.stop()
            self._loading_angle = 0
            self.update()
    
    def animate_transition(self, from_state: str, to_state: str) -> None:
        """
        Animate color transition between states.
        
        Args:
            from_state: Starting state ("disconnected" or "connected")
            to_state: Target state ("disconnected" or "connected")
        """
        # Create property animation for smooth transition
        if self._transition_animation:
            self._transition_animation.stop()
        
        self._transition_animation = QPropertyAnimation(self, b"transitionProgress")
        self._transition_animation.setDuration(500)  # 500ms transition
        self._transition_animation.setStartValue(0.0)
        self._transition_animation.setEndValue(1.0)
        self._transition_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Store states for painting
        self._from_state = from_state
        self._to_state = to_state
        
        self._transition_animation.start()
    
    def get_transition_progress(self) -> float:
        """Get current transition progress."""
        return self._transition_progress
    
    def set_transition_progress(self, value: float) -> None:
        """Set transition progress and trigger repaint."""
        self._transition_progress = value
        self.update()
    
    # Property for animation
    transitionProgress = pyqtProperty(float, get_transition_progress, set_transition_progress)
    
    def _update_loading_animation(self) -> None:
        """Update loading spinner angle."""
        self._loading_angle = (self._loading_angle + 15) % 360
        self.update()
    
    def paintEvent(self, event) -> None:
        """
        Custom paint event to draw loading spinner.
        
        Args:
            event: Paint event
        """
        # Call parent paint event for normal button rendering
        super().paintEvent(event)
        
        # Draw loading spinner if in loading state
        if self._is_loading:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Calculate spinner position (right side of button)
            spinner_size = 20
            x = self.width() - spinner_size - 10
            y = (self.height() - spinner_size) // 2
            
            # Draw spinner arc
            pen = QPen(QColor(255, 255, 255, 200))
            pen.setWidth(3)
            painter.setPen(pen)
            
            # Draw arc
            painter.drawArc(
                x, y, spinner_size, spinner_size,
                self._loading_angle * 16,  # Qt uses 1/16th degree units
                120 * 16  # Arc span
            )
            
            painter.end()


class GlowButton(QPushButton):
    """Button with glow effect on hover."""
    
    def __init__(self, text: str = "", parent=None):
        """
        Initialize glow button.
        
        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        self._glow_intensity = 0.0
        self._glow_animation = None
        
        # Enable hover events
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def get_glow_intensity(self) -> float:
        """Get current glow intensity."""
        return self._glow_intensity
    
    def set_glow_intensity(self, value: float) -> None:
        """Set glow intensity and trigger style update."""
        self._glow_intensity = value
        # Update style with glow effect
        self._update_glow_style()
    
    # Property for animation
    glowIntensity = pyqtProperty(float, get_glow_intensity, set_glow_intensity)
    
    def _update_glow_style(self) -> None:
        """Update button style with current glow intensity."""
        # The glow effect is primarily handled by QSS
        # This method can be extended for custom glow rendering
        self.update()
    
    def enterEvent(self, event) -> None:
        """Handle mouse enter for glow animation."""
        super().enterEvent(event)
        
        # Animate glow on
        if self._glow_animation:
            self._glow_animation.stop()
        
        self._glow_animation = QPropertyAnimation(self, b"glowIntensity")
        self._glow_animation.setDuration(200)
        self._glow_animation.setStartValue(self._glow_intensity)
        self._glow_animation.setEndValue(1.0)
        self._glow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._glow_animation.start()
    
    def leaveEvent(self, event) -> None:
        """Handle mouse leave for glow animation."""
        super().leaveEvent(event)
        
        # Animate glow off
        if self._glow_animation:
            self._glow_animation.stop()
        
        self._glow_animation = QPropertyAnimation(self, b"glowIntensity")
        self._glow_animation.setDuration(200)
        self._glow_animation.setStartValue(self._glow_intensity)
        self._glow_animation.setEndValue(0.0)
        self._glow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._glow_animation.start()
