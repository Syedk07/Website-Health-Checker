"""
Utility functions for managing application data directories.
"""

from pathlib import Path
import sys


def get_app_data_dir() -> Path:
    """
    Get the platform-appropriate application data directory.
    
    Returns:
        Path: The application data directory path
        
    Platform-specific locations:
        - Windows: %LOCALAPPDATA%/SitePulse/
        - Linux: ~/.local/share/SitePulse/
        - macOS: ~/Library/Application Support/SitePulse/
    """
    if sys.platform == "win32":
        # Windows: Use LOCALAPPDATA
        base = Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        # macOS: Use Application Support
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux and others: Use XDG_DATA_HOME or fallback
        base = Path.home() / ".local" / "share"
    
    app_dir = base / "SitePulse"
    
    # Create directory if it doesn't exist
    app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir


def get_database_path() -> Path:
    """
    Get the full path to the SQLite database file.
    
    Returns:
        Path: The database file path
    """
    return get_app_data_dir() / "sitepulse.db"


def get_exports_dir() -> Path:
    """
    Get the directory for exported files.
    
    Returns:
        Path: The exports directory path
    """
    exports_dir = get_app_data_dir() / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir
