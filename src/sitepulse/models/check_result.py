"""
Check result model representing a website health check result.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class CheckStatus(Enum):
    """Status classification for website checks."""
    
    SUCCESS = "success"  # HTTP 2xx response
    HTTP_ERROR = "http_error"  # HTTP 4xx, 5xx response
    TIMEOUT = "timeout"  # Connection timeout
    DNS_FAILURE = "dns_failure"  # DNS resolution failed
    CONNECTION_ERROR = "connection_error"  # Connection refused or failed
    SSL_ERROR = "ssl_error"  # SSL/TLS error
    INVALID_URL = "invalid_url"  # Invalid URL format
    UNKNOWN_ERROR = "unknown_error"  # Other errors


@dataclass
class CheckResult:
    """Represents the result of a website health check."""
    
    id: Optional[int]
    website_id: int
    checked_at: datetime
    status_code: Optional[int]
    response_time_ms: Optional[int]
    result_status: CheckStatus
    final_url: Optional[str] = None
    error_message: Optional[str] = None
    ssl_valid: Optional[bool] = None
    ssl_expiry_date: Optional[str] = None
    ssl_days_remaining: Optional[int] = None
    
    def __post_init__(self):
        """Convert string values to appropriate types if needed."""
        if isinstance(self.checked_at, str):
            self.checked_at = datetime.fromisoformat(self.checked_at)
        if isinstance(self.result_status, str):
            self.result_status = CheckStatus(self.result_status)
    
    @classmethod
    def from_row(cls, row) -> "CheckResult":
        """
        Create a CheckResult instance from a database row.
        
        Args:
            row: A database row (sqlite3.Row)
            
        Returns:
            CheckResult: A new CheckResult instance
        """
        return cls(
            id=row["id"],
            website_id=row["website_id"],
            checked_at=row["checked_at"],
            status_code=row["status_code"],
            response_time_ms=row["response_time_ms"],
            result_status=CheckStatus(row["result_status"]),
            final_url=row["final_url"],
            error_message=row["error_message"],
            ssl_valid=bool(row["ssl_valid"]) if row["ssl_valid"] is not None else None,
            ssl_expiry_date=row["ssl_expiry_date"],
            ssl_days_remaining=row["ssl_days_remaining"]
        )
    
    def is_successful(self) -> bool:
        """Check if the result represents a successful check."""
        return self.result_status == CheckStatus.SUCCESS
    
    def is_reachable(self) -> bool:
        """Check if the website was reachable (even if it returned an error status)."""
        return self.result_status in [CheckStatus.SUCCESS, CheckStatus.HTTP_ERROR]
