"""
Logs Tab Widget

Displays live V2Ray logs with clear and export functionality.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSlot
from v2ray_manager import V2RayManager


class LogsTab(QWidget):
    """Logs tab widget with log display and controls."""
    
    def __init__(self, v2ray_manager: V2RayManager, parent=None):
        """
        Initialize logs tab.
        
        Args:
            v2ray_manager: V2RayManager instance for log streaming
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.v2ray_manager = v2ray_manager
        self.log_line_count = 0
        self.max_log_lines = 10000
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.setLayout(layout)
        
        # Create control bar
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        
        # Clear logs button
        self.clear_button = QPushButton("🗑️ Clear Logs")
        self.clear_button.setFixedHeight(36)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_logs)
        control_layout.addWidget(self.clear_button)
        
        # Export logs button
        self.export_button = QPushButton("💾 Export Logs")
        self.export_button.setFixedHeight(36)
        self.export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_button.clicked.connect(self._on_export_clicked)
        control_layout.addWidget(self.export_button)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Create log display text area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_display.setPlaceholderText("V2Ray logs will appear here when connected...")
        
        # Set monospace font for logs
        font = self.log_display.font()
        font.setFamily("Monospace")
        font.setPointSize(10)
        self.log_display.setFont(font)
        
        layout.addWidget(self.log_display)
        
        # Connect to V2RayManager log stream
        self.v2ray_manager.stream_logs(self.append_log)
    
    @pyqtSlot(str)
    def append_log(self, text: str) -> None:
        """
        Add log line to display with auto-scroll.
        
        Args:
            text: Log line to add
        """
        # Check if we need to trim old logs
        if self.log_line_count >= self.max_log_lines:
            # Remove first line
            cursor = self.log_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # Remove the newline
            self.log_line_count -= 1
        
        # Append new log line
        self.log_display.append(text)
        self.log_line_count += 1
        
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self) -> None:
        """Clear all logs from display."""
        self.log_display.clear()
        self.log_line_count = 0
    
    def _on_export_clicked(self) -> None:
        """Handle export button click - show file dialog."""
        # Open file dialog to select export location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            "v2ray_logs.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.export_logs(file_path)
    
    def export_logs(self, filepath: str) -> bool:
        """
        Export logs to file.
        
        Args:
            filepath: Path to save logs to
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get all log text
            log_text = self.log_display.toPlainText()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(log_text)
            
            return True
            
        except Exception as e:
            # Handle file write errors
            return False
