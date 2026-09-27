"""
Website management service.
"""

from datetime import datetime
from typing import List, Optional
from ..database import DatabaseManager
from ..models import Website, CheckResult
from ..utils import normalize_url


class WebsiteService:
    """Service for managing websites and check results."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the website service.
        
        Args:
            db_manager: The database manager instance
        """
        self.db_manager = db_manager
    
    def add_website(self, name: str, url: str) -> Optional[Website]:
        """
        Add a new website to the database.
        
        Args:
            name: Display name for the website
            url: URL of the website
            
        Returns:
            Optional[Website]: The created website, or None if a duplicate URL exists
        """
        normalized_url = normalize_url(url)
        
        conn = self.db_manager.get_connection()
        try:
            # Check if URL already exists
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM websites WHERE url = ?", (normalized_url,))
            if cursor.fetchone():
                return None  # Duplicate URL
            
            # Insert new website
            cursor.execute(
                """
                INSERT INTO websites (name, url, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, normalized_url, datetime.now().isoformat(), datetime.now().isoformat())
            )
            conn.commit()
            
            website_id = cursor.lastrowid
            
            # Fetch and return the created website
            cursor.execute("SELECT * FROM websites WHERE id = ?", (website_id,))
            row = cursor.fetchone()
            return Website.from_row(row) if row else None
            
        finally:
            conn.close()
    
    def get_website(self, website_id: int) -> Optional[Website]:
        """
        Get a website by ID.
        
        Args:
            website_id: The website ID
            
        Returns:
            Optional[Website]: The website, or None if not found
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM websites WHERE id = ?", (website_id,))
            row = cursor.fetchone()
            return Website.from_row(row) if row else None
        finally:
            conn.close()
    
    def get_all_websites(self) -> List[Website]:
        """
        Get all websites.
        
        Returns:
            List[Website]: List of all websites
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM websites ORDER BY name")
            rows = cursor.fetchall()
            return [Website.from_row(row) for row in rows]
        finally:
            conn.close()
    
    def update_website(self, website_id: int, name: Optional[str] = None, 
                      url: Optional[str] = None) -> bool:
        """
        Update a website's information.
        
        Args:
            website_id: The website ID
            name: New display name (optional)
            url: New URL (optional)
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        if not name and not url:
            return False
        
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            
            if url:
                normalized_url = normalize_url(url)
                
                # Check if new URL already exists for a different website
                cursor.execute(
                    "SELECT id FROM websites WHERE url = ? AND id != ?",
                    (normalized_url, website_id)
                )
                if cursor.fetchone():
                    return False  # Duplicate URL
                
                updates.append("url = ?")
                params.append(normalized_url)
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            # Add website_id to params
            params.append(website_id)
            
            query = f"UPDATE websites SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
            
        finally:
            conn.close()
    
    def delete_website(self, website_id: int) -> bool:
        """
        Delete a website and all its check results.
        
        Args:
            website_id: The website ID
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM websites WHERE id = ?", (website_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def save_check_result(self, result: CheckResult) -> Optional[int]:
        """
        Save a check result to the database.
        
        Args:
            result: The check result to save
            
        Returns:
            Optional[int]: The ID of the saved result, or None if failed
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO check_results (
                    website_id, checked_at, status_code, response_time_ms,
                    result_status, final_url, error_message,
                    ssl_valid, ssl_expiry_date, ssl_days_remaining
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.website_id,
                    datetime.fromtimestamp(result.checked_at).isoformat(),
                    result.status_code,
                    result.response_time_ms,
                    result.result_status.value,
                    result.final_url,
                    result.error_message,
                    result.ssl_valid,
                    result.ssl_expiry_date,
                    result.ssl_days_remaining
                )
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_latest_check_result(self, website_id: int) -> Optional[CheckResult]:
        """
        Get the most recent check result for a website.
        
        Args:
            website_id: The website ID
            
        Returns:
            Optional[CheckResult]: The latest check result, or None if not found
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM check_results
                WHERE website_id = ?
                ORDER BY checked_at DESC
                LIMIT 1
                """,
                (website_id,)
            )
            row = cursor.fetchone()
            return CheckResult.from_row(row) if row else None
        finally:
            conn.close()
    
    def get_check_history(self, website_id: Optional[int] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: Optional[int] = None) -> List[CheckResult]:
        """
        Get check history with optional filters.
        
        Args:
            website_id: Filter by website ID (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            limit: Maximum number of results (optional)
            
        Returns:
            List[CheckResult]: List of check results
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            query = "SELECT * FROM check_results WHERE 1=1"
            params = []
            
            if website_id:
                query += " AND website_id = ?"
                params.append(website_id)
            
            if start_date:
                query += " AND checked_at >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND checked_at <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY checked_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [CheckResult.from_row(row) for row in rows]
        finally:
            conn.close()
