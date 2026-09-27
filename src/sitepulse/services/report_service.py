"""
Report generation service.
"""

from datetime import datetime
from typing import Dict, Optional, List
from ..database import DatabaseManager
from ..models import CheckStatus


class ReportService:
    """Service for generating health reports."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the report service.
        
        Args:
            db_manager: The database manager instance
        """
        self.db_manager = db_manager
    
    def generate_summary_report(self, website_id: Optional[int] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict:
        """
        Generate a summary report for website checks.
        
        Args:
            website_id: Filter by website ID (optional)
            start_date: Start date for the report (optional)
            end_date: End date for the report (optional)
            
        Returns:
            Dict: Report data containing statistics
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Build query
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
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Calculate statistics
            total_checks = len(results)
            
            if total_checks == 0:
                return {
                    'total_checks': 0,
                    'successful_checks': 0,
                    'http_errors': 0,
                    'connection_failures': 0,
                    'ssl_errors': 0,
                    'timeouts': 0,
                    'dns_failures': 0,
                    'success_rate': 0.0,
                    'average_response_time': 0,
                    'min_response_time': 0,
                    'max_response_time': 0
                }
            
            successful_checks = 0
            http_errors = 0
            connection_failures = 0
            ssl_errors = 0
            timeouts = 0
            dns_failures = 0
            response_times = []
            
            for row in results:
                status = CheckStatus(row['result_status'])
                
                if status == CheckStatus.SUCCESS:
                    successful_checks += 1
                elif status == CheckStatus.HTTP_ERROR:
                    http_errors += 1
                elif status in [CheckStatus.CONNECTION_ERROR, CheckStatus.UNKNOWN_ERROR]:
                    connection_failures += 1
                elif status == CheckStatus.SSL_ERROR:
                    ssl_errors += 1
                elif status == CheckStatus.TIMEOUT:
                    timeouts += 1
                elif status == CheckStatus.DNS_FAILURE:
                    dns_failures += 1
                
                if row['response_time_ms'] is not None:
                    response_times.append(row['response_time_ms'])
            
            success_rate = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            return {
                'total_checks': total_checks,
                'successful_checks': successful_checks,
                'http_errors': http_errors,
                'connection_failures': connection_failures,
                'ssl_errors': ssl_errors,
                'timeouts': timeouts,
                'dns_failures': dns_failures,
                'success_rate': round(success_rate, 2),
                'average_response_time': round(avg_response_time, 2),
                'min_response_time': min_response_time,
                'max_response_time': max_response_time
            }
            
        finally:
            conn.close()
