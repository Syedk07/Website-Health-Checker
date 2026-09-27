"""
Tests for database functionality.
"""

import sqlite3
import tempfile
from pathlib import Path
import pytest

from sitepulse.database import init_database, DatabaseManager


def test_database_initialization():
    """Test that the database initializes with correct schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db_manager = init_database(db_path)
        
        # Verify database file was created
        assert db_path.exists()
        
        # Verify tables were created
        conn = db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check websites table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='websites'"
            )
            assert cursor.fetchone() is not None
            
            # Check check_results table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='check_results'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()


def test_database_manager_connection():
    """Test DatabaseManager connection handling."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db_manager = DatabaseManager(db_path)
        
        # Test connection creation
        conn = db_manager.get_connection()
        assert isinstance(conn, sqlite3.Connection)
        conn.close()


def test_database_row_factory():
    """Test that database connections have row factory enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db_manager = init_database(db_path)
        
        conn = db_manager.get_connection()
        try:
            # Insert a test website
            conn.execute(
                "INSERT INTO websites (name, url) VALUES (?, ?)",
                ("Test Site", "https://example.com")
            )
            conn.commit()
            
            # Query and verify row factory works
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM websites")
            row = cursor.fetchone()
            
            # Should be able to access by column name
            assert row["name"] == "Test Site"
            assert row["url"] == "https://example.com"
        finally:
            conn.close()
