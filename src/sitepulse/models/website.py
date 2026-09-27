"""
Website model representing a monitored website.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Website:
    """Represents a website being monitored."""
    
    id: Optional[int]
    name: str
    url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Convert string timestamps to datetime objects if needed."""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    @classmethod
    def from_row(cls, row) -> "Website":
        """
        Create a Website instance from a database row.
        
        Args:
            row: A database row (sqlite3.Row)
            
        Returns:
            Website: A new Website instance
        """
        return cls(
            id=row["id"],
            name=row["name"],
            url=row["url"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
