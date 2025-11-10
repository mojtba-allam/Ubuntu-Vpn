"""
Theme loader module for V2Ray Client.
Handles loading, validation, and persistence of UI themes.
"""

import os
import json
from pathlib import Path
from typing import Optional


class ThemeLoader:
    """Manages theme loading and persistence for the application."""
    
    AVAILABLE_THEMES = ["dark", "light", "neon"]
    DEFAULT_THEME = "dark"
    
    def __init__(self, config_dir: str = "~/.config/v2ray-client"):
        """
        Initialize theme loader.
        
        Args:
            config_dir: Directory for storing configuration files
        """
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.config_dir / "settings.json"
        
        # Get the themes directory relative to this file
        self.themes_dir = Path(__file__).parent / "themes"
    
    def load_theme(self, theme_name: str) -> Optional[str]:
        """
        Load a theme stylesheet.
        
        Args:
            theme_name: Name of the theme to load (dark, light, neon)
            
        Returns:
            Theme stylesheet content as string, or None if theme not found
        """
        if not self.validate_theme(theme_name):
            print(f"Warning: Theme '{theme_name}' not found, falling back to default")
            theme_name = self.DEFAULT_THEME
        
        theme_file = self.themes_dir / f"{theme_name}.qss"
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Theme file '{theme_file}' not found")
            return None
        except Exception as e:
            print(f"Error loading theme: {e}")
            return None
    
    def validate_theme(self, theme_name: str) -> bool:
        """
        Validate that a theme exists.
        
        Args:
            theme_name: Name of the theme to validate
            
        Returns:
            True if theme exists, False otherwise
        """
        if theme_name not in self.AVAILABLE_THEMES:
            return False
        
        theme_file = self.themes_dir / f"{theme_name}.qss"
        return theme_file.exists()
    
    def get_available_themes(self) -> list:
        """
        Get list of available themes.
        
        Returns:
            List of theme names
        """
        return self.AVAILABLE_THEMES.copy()
    
    def save_theme_preference(self, theme_name: str) -> bool:
        """
        Save theme preference to settings file.
        
        Args:
            theme_name: Name of the theme to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Load existing settings or create new
            settings = self.load_settings()
            settings["theme"] = theme_name
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving theme preference: {e}")
            return False
    
    def load_theme_preference(self) -> str:
        """
        Load saved theme preference from settings file.
        
        Returns:
            Theme name from settings, or default theme if not found
        """
        settings = self.load_settings()
        theme = settings.get("theme", self.DEFAULT_THEME)
        
        # Validate the loaded theme
        if not self.validate_theme(theme):
            print(f"Warning: Saved theme '{theme}' not found, using default")
            return self.DEFAULT_THEME
        
        return theme
    
    def load_settings(self) -> dict:
        """
        Load all settings from settings file.
        
        Returns:
            Dictionary of settings, or empty dict if file doesn't exist
        """
        if not self.settings_file.exists():
            return {}
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Settings file is corrupted, using defaults")
            return {}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}
    
    def save_settings(self, settings: dict) -> bool:
        """
        Save all settings to settings file.
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False


def apply_theme_to_app(app, theme_name: str, config_dir: str = "~/.config/v2ray-client") -> bool:
    """
    Convenience function to apply a theme to a QApplication.
    
    Args:
        app: QApplication instance
        theme_name: Name of the theme to apply
        config_dir: Configuration directory path
        
    Returns:
        True if theme applied successfully, False otherwise
    """
    loader = ThemeLoader(config_dir)
    stylesheet = loader.load_theme(theme_name)
    
    if stylesheet:
        app.setStyleSheet(stylesheet)
        loader.save_theme_preference(theme_name)
        return True
    
    return False
