"""
URL validation and normalization utilities.
"""

import re
from urllib.parse import urlparse, urlunparse
from typing import Optional, Tuple


# Private IP ranges (RFC 1918, RFC 4193, etc.)
PRIVATE_IP_PATTERNS = [
    r'^127\.',  # Loopback
    r'^10\.',   # Private class A
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Private class B
    r'^192\.168\.',  # Private class C
    r'^169\.254\.',  # Link-local
    r'^::1$',  # IPv6 loopback
    r'^fe80:',  # IPv6 link-local
    r'^fc00:',  # IPv6 unique local
    r'^fd00:',  # IPv6 unique local
]

# Cloud metadata endpoints
METADATA_ENDPOINTS = [
    '169.254.169.254',  # AWS, Azure, GCP
    'metadata.google.internal',
    '100.100.100.200',  # Alibaba Cloud
]


def normalize_url(url: str) -> str:
    """
    Normalize a URL by adding a scheme if missing and cleaning up the format.
    
    Args:
        url: The URL to normalize
        
    Returns:
        str: The normalized URL
    """
    url = url.strip()
    
    # Parse first to check if scheme exists
    parsed = urlparse(url)
    
    # If no scheme is present, add https://
    if not parsed.scheme:
        url = 'https://' + url
        parsed = urlparse(url)
    
    # Ensure we have a netloc (hostname)
    if not parsed.netloc:
        return url
    
    # Reconstruct with normalized components
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),  # Lowercase hostname
        parsed.path or '/',
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return normalized


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL for safety and correctness.
    
    Args:
        url: The URL to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
            - is_valid: True if the URL is valid, False otherwise
            - error_message: Description of the validation error, or None if valid
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False, f"Unsupported URL scheme: {parsed.scheme}. Only HTTP and HTTPS are supported."
        
        # Check if netloc (hostname) exists
        if not parsed.netloc:
            return False, "URL must contain a valid hostname."
        
        # Check for valid hostname format
        hostname = parsed.netloc.split(':')[0]  # Remove port if present
        
        if not hostname:
            return False, "URL must contain a valid hostname."
        
        # Check for localhost
        if hostname.lower() in ['localhost', 'localhost.localdomain']:
            return False, "Localhost URLs are not allowed for security reasons."
        
        # Check for private IP addresses
        for pattern in PRIVATE_IP_PATTERNS:
            if re.match(pattern, hostname, re.IGNORECASE):
                return False, f"Private IP addresses are not allowed for security reasons."
        
        # Check for cloud metadata endpoints
        if hostname in METADATA_ENDPOINTS:
            return False, "Cloud metadata endpoints are not allowed for security reasons."
        
        # Basic hostname validation (allow letters, numbers, dots, hyphens)
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$', hostname):
            return False, f"Invalid hostname format: {hostname}"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_redirect_url(url: str, original_url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a redirect destination URL for safety.
    
    Args:
        url: The redirect destination URL
        original_url: The original URL that was requested
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Perform standard validation
    is_valid, error_msg = validate_url(url)
    
    if not is_valid:
        return False, f"Redirect destination failed validation: {error_msg}"
    
    # Additional check: ensure redirect doesn't change scheme from HTTPS to HTTP
    original_parsed = urlparse(original_url)
    redirect_parsed = urlparse(url)
    
    if original_parsed.scheme == 'https' and redirect_parsed.scheme == 'http':
        return False, "HTTPS to HTTP redirect is not allowed for security reasons."
    
    return True, None


def extract_hostname(url: str) -> Optional[str]:
    """
    Extract the hostname from a URL.
    
    Args:
        url: The URL to extract hostname from
        
    Returns:
        Optional[str]: The hostname, or None if extraction fails
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.split(':')[0]  # Remove port
        return hostname if hostname else None
    except Exception:
        return None
