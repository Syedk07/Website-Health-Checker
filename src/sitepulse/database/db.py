"""
Database initialization and management for SitePulse.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from ..utils.paths import get_database_path


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the database file. If None, uses the default location.
        """
        self.db_path = db_path or get_database_path()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a database connection.
        
        Returns:
            sqlite3.Connection: A connection to the database
        """
        conn = sqlite3.Connection(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script.
        
        Args:
            script: SQL script to execute
        """
        conn = self.get_connection()
        try:
            conn.executescript(script)
            conn.commit()
        finally:
            conn.close()


def init_database(db_path: Optional[Path] = None) -> DatabaseManager:
    """
    Initialize the database with required tables and indexes.
    
    Args:
        db_path: Path to the database file. If None, uses the default location.
        
    Returns:
        DatabaseManager: The initialized database manager
    """
    db_manager = DatabaseManager(db_path)
    
    # SQL schema for creating tables
    schema = """
    -- Websites table
    CREATE TABLE IF NOT EXISTS websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Check results table
    CREATE TABLE IF NOT EXISTS check_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website_id INTEGER NOT NULL,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status_code INTEGER,
        response_time_ms INTEGER,
        result_status TEXT NOT NULL,
        final_url TEXT,
        error_message TEXT,
        ssl_valid BOOLEAN,
        ssl_expiry_date TEXT,
        ssl_days_remaining INTEGER,
        FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
    );
    
    -- Indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_check_results_website_id 
        ON check_results(website_id);
    
    CREATE INDEX IF NOT EXISTS idx_check_results_checked_at 
        ON check_results(checked_at);
    
    CREATE INDEX IF NOT EXISTS idx_check_results_result_status 
        ON check_results(result_status);
    """
    
    db_manager.execute_script(schema)
    
    return db_manager
