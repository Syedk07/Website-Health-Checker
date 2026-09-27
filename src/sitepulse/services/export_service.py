"""
Export service for saving data to CSV.
"""

import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..models import CheckResult, Website


class ExportService:
    """Service for exporting data to CSV files."""
    
    @staticmethod
    def export_check_history(results: List[CheckResult], websites: List[Website],
                            file_path: Path) -> bool:
        """
        Export check history to a CSV file.
        
        Args:
            results: List of check results to export
            websites: List of websites for name lookup
            file_path: Path where the CSV file should be saved
            
        Returns:
            bool: True if export succeeded, False otherwise
        """
        try:
            # Create website lookup
            website_lookup = {w.id: w.name for w in websites}
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Date/Time',
                    'Website Name',
                    'Website URL',
                    'Status',
                    'HTTP Status Code',
                    'Response Time (ms)',
                    'Error Message',
                    'Final URL',
                    'SSL Valid',
                    'SSL Expiry Date',
                    'SSL Days Remaining'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    # Find website
                    website = next((w for w in websites if w.id == result.website_id), None)
                    website_name = website_lookup.get(result.website_id, f"ID: {result.website_id}")
                    website_url = website.url if website else "Unknown"
                    
                    # Format datetime
                    checked_at = datetime.fromisoformat(result.checked_at).strftime("%Y-%m-%d %H:%M:%S") if isinstance(result.checked_at, str) else result.checked_at.strftime("%Y-%m-%d %H:%M:%S")
                    
                    writer.writerow({
                        'Date/Time': checked_at,
                        'Website Name': website_name,
                        'Website URL': website_url,
                        'Status': result.result_status.value,
                        'HTTP Status Code': result.status_code if result.status_code else '',
                        'Response Time (ms)': result.response_time_ms if result.response_time_ms else '',
                        'Error Message': result.error_message if result.error_message else '',
                        'Final URL': result.final_url if result.final_url else '',
                        'SSL Valid': result.ssl_valid if result.ssl_valid is not None else '',
                        'SSL Expiry Date': result.ssl_expiry_date if result.ssl_expiry_date else '',
                        'SSL Days Remaining': result.ssl_days_remaining if result.ssl_days_remaining is not None else ''
                    })
            
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_websites(websites: List[Website], file_path: Path) -> bool:
        """
        Export websites list to a CSV file.
        
        Args:
            websites: List of websites to export
            file_path: Path where the CSV file should be saved
            
        Returns:
            bool: True if export succeeded, False otherwise
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Name', 'URL', 'Created At', 'Updated At']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for website in websites:
                    writer.writerow({
                        'ID': website.id,
                        'Name': website.name,
                        'URL': website.url,
                        'Created At': website.created_at.isoformat() if website.created_at else '',
                        'Updated At': website.updated_at.isoformat() if website.updated_at else ''
                    })
            
            return True
            
        except Exception as e:
            print(f"Error exporting websites to CSV: {e}")
            return False
