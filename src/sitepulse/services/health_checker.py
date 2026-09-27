"""
Website health checking service.
"""

import time
import requests
from typing import Tuple, Optional
from urllib.parse import urlparse
import socket

from ..models import CheckResult, CheckStatus
from ..utils import normalize_url, validate_url, validate_redirect_url
from .ssl_checker import SSLChecker


class HealthChecker:
    """Performs website health checks."""
    
    # Configuration
    DEFAULT_TIMEOUT = 10  # seconds
    MAX_REDIRECTS = 5
    USER_AGENT = "SitePulse/1.0 (Website Health Monitor)"
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, check_ssl: bool = True):
        """
        Initialize the health checker.
        
        Args:
            timeout: Request timeout in seconds
            check_ssl: Whether to check SSL certificates for HTTPS URLs
        """
        self.timeout = timeout
        self.check_ssl = check_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT
        })
        self.ssl_checker = SSLChecker(timeout=timeout) if check_ssl else None
    
    def check_website(self, website_id: int, url: str) -> CheckResult:
        """
        Check the health of a website.
        
        Args:
            website_id: The ID of the website being checked
            url: The URL to check
            
        Returns:
            CheckResult: The result of the health check
        """
        # Normalize URL
        normalized_url = normalize_url(url)
        
        # Validate URL
        is_valid, error_msg = validate_url(normalized_url)
        if not is_valid:
            return CheckResult(
                id=None,
                website_id=website_id,
                checked_at=time.time(),
                status_code=None,
                response_time_ms=None,
                result_status=CheckStatus.INVALID_URL,
                error_message=error_msg
            )
        
        # Perform the HTTP request
        return self._perform_request(website_id, normalized_url)
    
    def _perform_request(self, website_id: int, url: str) -> CheckResult:
        """
        Perform the actual HTTP request and measure response time.
        
        Args:
            website_id: The ID of the website being checked
            url: The normalized and validated URL
            
        Returns:
            CheckResult: The result of the request
        """
        start_time = time.perf_counter()
        
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            end_time = time.perf_counter()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Validate redirect destination if redirected
            final_url = response.url
            if final_url != url:
                is_valid, error_msg = validate_redirect_url(final_url, url)
                if not is_valid:
                    return CheckResult(
                        id=None,
                        website_id=website_id,
                        checked_at=time.time(),
                        status_code=None,
                        response_time_ms=response_time_ms,
                        result_status=CheckStatus.UNKNOWN_ERROR,
                        error_message=error_msg,
                        final_url=final_url
                    )
            
            # Determine status based on HTTP status code
            status_code = response.status_code
            
            if 200 <= status_code < 400:
                result_status = CheckStatus.SUCCESS
            else:
                result_status = CheckStatus.HTTP_ERROR
            
            # Check SSL certificate if enabled and URL is HTTPS
            ssl_valid = None
            ssl_expiry_date = None
            ssl_days_remaining = None
            
            if self.check_ssl and final_url.startswith('https://'):
                ssl_success, ssl_info = self.ssl_checker.check_ssl_certificate(final_url)
                if ssl_success and ssl_info:
                    ssl_valid = ssl_info.get('is_valid')
                    ssl_expiry_date = ssl_info.get('expiry_date')
                    ssl_days_remaining = ssl_info.get('days_remaining')
            
            return CheckResult(
                id=None,
                website_id=website_id,
                checked_at=time.time(),
                status_code=status_code,
                response_time_ms=response_time_ms,
                result_status=result_status,
                final_url=final_url if final_url != url else None,
                ssl_valid=ssl_valid,
                ssl_expiry_date=ssl_expiry_date,
                ssl_days_remaining=ssl_days_remaining
            )
            
        except requests.exceptions.Timeout:
            return CheckResult(
                id=None,
                website_id=website_id,
                checked_at=time.time(),
                status_code=None,
                response_time_ms=None,
                result_status=CheckStatus.TIMEOUT,
                error_message=f"Request timed out after {self.timeout} seconds"
            )
            
        except requests.exceptions.SSLError as e:
            return CheckResult(
                id=None,
                website_id=website_id,
                checked_at=time.time(),
                status_code=None,
                response_time_ms=None,
                result_status=CheckStatus.SSL_ERROR,
                error_message=f"SSL/TLS error: {str(e)}"
            )
            
        except requests.exceptions.ConnectionError as e:
            # Try to determine if it's a DNS failure
            error_str = str(e).lower()
            
            if 'nodename nor servname provided' in error_str or \
               'name or service not known' in error_str or \
               'getaddrinfo failed' in error_str or \
               'no such host' in error_str:
                result_status = CheckStatus.DNS_FAILURE
                error_message = "DNS resolution failed - hostname not found"
            else:
                result_status = CheckStatus.CONNECTION_ERROR
                error_message = f"Connection failed: {str(e)}"
            
            return CheckResult(
                id=None,
                website_id=website_id,
                checked_at=time.time(),
                status_code=None,
                response_time_ms=None,
                result_status=result_status,
                error_message=error_message
            )
            
        except requests.exceptions.TooManyRedirects:
            return CheckResult(
                id=None,
                website_id=website_id,
                checked_at=time.time(),
                status_code=None,
                response_time_ms=None,
                result_status=CheckStatus.UNKNOWN_ERROR,
                error_message=f"Too many redirects (exceeded {self.MAX_REDIRECTS})"
            )
            
        except Exception as e:
            return CheckResult(
                id=None,
                website_id=website_id,
                checked_at=time.time(),
                status_code=None,
                response_time_ms=None,
                result_status=CheckStatus.UNKNOWN_ERROR,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def close(self):
        """Close the requests session."""
        self.session.close()
