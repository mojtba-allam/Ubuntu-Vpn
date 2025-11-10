"""
Unit tests for ThemeLoader class.
"""

import pytest
import json
from pathlib import Path
from ui.theme_loader import ThemeLoader, apply_theme_to_app


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temporary config directory."""
    return str(tmp_path / "v2ray-test")


@pytest.fixture
def loader(temp_config_dir):
    """Provide a ThemeLoader instance with temp directory."""
    return ThemeLoader(config_dir=temp_config_dir)


class TestThemeLoaderInit:
    """Test ThemeLoader initialization."""
    
    def test_init_creates_config_directory(self, temp_config_dir):
        """Test that __init__ creates the config directory."""
        loader = ThemeLoader(config_dir=temp_config_dir)
        
        assert loader.config_dir.exists()
        assert loader.config_dir.is_dir()
    
    def test_init_sets_themes_directory(self, loader):
        """Test that __init__ sets the themes directory correctly."""
        assert loader.themes_dir.exists()
        assert loader.themes_dir.is_dir()
    
    def test_available_themes_list(self, loader):
        """Test that available themes list is correct."""
        themes = loader.get_available_themes()
        assert "dark" in themes
        assert "light" in themes
        assert "neon" in themes


class TestThemeLoaderValidation:
    """Test theme validation."""
    
    def test_validate_theme_valid_dark(self, loader):
        """Test validation of dark theme."""
        assert loader.validate_theme("dark") is True
    
    def test_validate_theme_valid_light(self, loader):
        """Test validation of light theme."""
        assert loader.validate_theme("light") is True
    
    def test_validate_theme_valid_neon(self, loader):
        """Test validation of neon theme."""
        assert loader.validate_theme("neon") is True
    
    def test_validate_theme_invalid(self, loader):
        """Test validation of non-existent theme."""
        assert loader.validate_theme("nonexistent") is False
    
    def test_validate_theme_empty_string(self, loader):
        """Test validation with empty string."""
        assert loader.validate_theme("") is False


class TestThemeLoaderLoad:
    """Test theme loading."""
    
    def test_load_theme_dark(self, loader):
        """Test loading dark theme."""
        stylesheet = loader.load_theme("dark")
        
        assert stylesheet is not None
        assert len(stylesheet) > 0
        assert "QMainWindow" in stylesheet
    
    def test_load_theme_light(self, loader):
        """Test loading light theme."""
        stylesheet = loader.load_theme("light")
        
        assert stylesheet is not None
        assert len(stylesheet) > 0
        assert "QMainWindow" in stylesheet
    
    def test_load_theme_neon(self, loader):
        """Test loading neon theme."""
        stylesheet = loader.load_theme("neon")
        
        assert stylesheet is not None
        assert len(stylesheet) > 0
        assert "gradient" in stylesheet.lower()
    
    def test_load_theme_invalid_falls_back_to_default(self, loader):
        """Test that invalid theme falls back to default."""
        stylesheet = loader.load_theme("nonexistent")
        
        # Should fall back to dark theme
        assert stylesheet is not None
        assert len(stylesheet) > 0
    
    def test_load_theme_returns_different_content(self, loader):
        """Test that different themes return different content."""
        dark = loader.load_theme("dark")
        light = loader.load_theme("light")
        neon = loader.load_theme("neon")
        
        assert dark != light
        assert dark != neon
        assert light != neon


class TestThemeLoaderPersistence:
    """Test theme preference persistence."""
    
    def test_save_theme_preference(self, loader):
        """Test saving theme preference."""
        result = loader.save_theme_preference("neon")
        
        assert result is True
        assert loader.settings_file.exists()
        
        # Verify saved content
        with open(loader.settings_file, 'r') as f:
            settings = json.load(f)
        assert settings["theme"] == "neon"
    
    def test_load_theme_preference_default(self, loader):
        """Test loading theme preference when no file exists."""
        theme = loader.load_theme_preference()
        
        assert theme == "dark"  # Default theme
    
    def test_load_theme_preference_saved(self, loader):
        """Test loading saved theme preference."""
        loader.save_theme_preference("light")
        theme = loader.load_theme_preference()
        
        assert theme == "light"
    
    def test_save_and_load_theme_preference(self, loader):
        """Test save and load cycle."""
        loader.save_theme_preference("neon")
        
        # Create new loader instance to test persistence
        new_loader = ThemeLoader(config_dir=str(loader.config_dir))
        theme = new_loader.load_theme_preference()
        
        assert theme == "neon"
    
    def test_load_theme_preference_invalid_falls_back(self, loader):
        """Test that invalid saved theme falls back to default."""
        # Manually save invalid theme
        settings = {"theme": "invalid_theme"}
        with open(loader.settings_file, 'w') as f:
            json.dump(settings, f)
        
        theme = loader.load_theme_preference()
        
        assert theme == "dark"  # Should fall back to default


class TestThemeLoaderSettings:
    """Test general settings management."""
    
    def test_load_settings_empty_when_no_file(self, loader):
        """Test loading settings when file doesn't exist."""
        settings = loader.load_settings()
        
        assert settings == {}
    
    def test_save_settings(self, loader):
        """Test saving settings."""
        test_settings = {
            "theme": "neon",
            "refresh_interval": 30,
            "auto_start": True
        }
        
        result = loader.save_settings(test_settings)
        
        assert result is True
        assert loader.settings_file.exists()
    
    def test_save_and_load_settings(self, loader):
        """Test save and load settings cycle."""
        test_settings = {
            "theme": "light",
            "refresh_interval": 60,
            "subscriptions": []
        }
        
        loader.save_settings(test_settings)
        loaded = loader.load_settings()
        
        assert loaded["theme"] == "light"
        assert loaded["refresh_interval"] == 60
    
    def test_load_settings_corrupted_file(self, loader):
        """Test loading settings from corrupted file."""
        # Create corrupted JSON file
        with open(loader.settings_file, 'w') as f:
            f.write("not valid json{{{")
        
        settings = loader.load_settings()
        
        assert settings == {}
    
    def test_save_theme_preserves_other_settings(self, loader):
        """Test that saving theme preserves other settings."""
        # Save initial settings
        initial = {
            "theme": "dark",
            "refresh_interval": 30,
            "custom_setting": "value"
        }
        loader.save_settings(initial)
        
        # Save theme preference
        loader.save_theme_preference("neon")
        
        # Load and verify
        settings = loader.load_settings()
        assert settings["theme"] == "neon"
        assert settings["refresh_interval"] == 30
        assert settings["custom_setting"] == "value"
