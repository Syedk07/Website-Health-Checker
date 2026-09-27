"""
SSL certificate checking service.
"""

import ssl
import socket
from datetime import datetime
from typing import Tuple, Optional, Dict
from urllib.parse import urlparse

from ..utils import extract_hostname


class SSLChecker:
    """Performs SSL/TLS certificate checks."""
    
    DEFAULT_TIMEOUT = 10  # seconds
    DEFAULT_PORT = 443
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the SSL checker.
        
        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout
    
    def check_ssl_certificate(self, url: str) -> Tuple[bool, Optional[Dict]]:
        """
        Check the SSL/TLS certificate for a given URL.
        
        Args:
            url: The URL to check (must be HTTPS)
            
        Returns:
            Tuple[bool, Optional[Dict]]: (success, certificate_info)
                - success: True if check succeeded, False otherwise
                - certificate_info: Dict containing SSL information, or None if check failed
                    Keys: 'is_valid', 'expiry_date', 'days_remaining', 'error'
        """
        # Parse URL to get hostname
        parsed = urlparse(url)
        
        if parsed.scheme != 'https':
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': 'SSL check only applies to HTTPS URLs'
            }
        
        hostname = extract_hostname(url)
        if not hostname:
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': 'Could not extract hostname from URL'
            }
        
        port = parsed.port or self.DEFAULT_PORT
        
        try:
            # Create SSL context with certificate verification enabled
            context = ssl.create_default_context()
            
            # Create socket and wrap with SSL
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate
                    cert = ssock.getpeercert()
                    
                    # Extract expiry date
                    not_after_str = cert.get('notAfter')
                    
                    if not_after_str:
                        # Parse the certificate expiry date
                        # Format: 'MMM DD HH:MM:SS YYYY GMT'
                        expiry_date = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                        
                        # Calculate days remaining
                        now = datetime.now()
                        days_remaining = (expiry_date - now).days
                        
                        is_valid = days_remaining > 0
                        
                        return True, {
                            'is_valid': is_valid,
                            'expiry_date': expiry_date.isoformat(),
                            'days_remaining': days_remaining,
                            'error': None
                        }
                    else:
                        return False, {
                            'is_valid': False,
                            'expiry_date': None,
                            'days_remaining': None,
                            'error': 'Certificate does not contain expiry information'
                        }
        
        except ssl.SSLCertVerificationError as e:
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': f'Certificate verification failed: {str(e)}'
            }
        
        except ssl.SSLError as e:
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': f'SSL error: {str(e)}'
            }
        
        except socket.timeout:
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': f'Connection timed out after {self.timeout} seconds'
            }
        
        except socket.gaierror as e:
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': f'DNS resolution failed: {str(e)}'
            }
        
        except ConnectionRefusedError:
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': 'Connection refused'
            }
        
        except Exception as e:
            return False, {
                'is_valid': False,
                'expiry_date': None,
                'days_remaining': None,
                'error': f'Unexpected error: {str(e)}'
            }
