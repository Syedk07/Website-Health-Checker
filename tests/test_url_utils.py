"""
Tests for URL utility functions.
"""

import pytest
from sitepulse.utils import normalize_url, validate_url, validate_redirect_url, extract_hostname


class TestNormalizeUrl:
    """Tests for URL normalization."""
    
    def test_normalize_url_without_scheme(self):
        """Test that URLs without scheme get https:// added."""
        assert normalize_url("example.com") == "https://example.com/"
        assert normalize_url("www.example.com") == "https://www.example.com/"
    
    def test_normalize_url_with_http(self):
        """Test that HTTP URLs are preserved."""
        assert normalize_url("http://example.com") == "http://example.com/"
    
    def test_normalize_url_with_https(self):
        """Test that HTTPS URLs are preserved."""
        assert normalize_url("https://example.com") == "https://example.com/"
    
    def test_normalize_url_lowercase_hostname(self):
        """Test that hostnames are lowercased."""
        assert normalize_url("https://EXAMPLE.COM") == "https://example.com/"
        assert normalize_url("EXAMPLE.COM") == "https://example.com/"
    
    def test_normalize_url_with_path(self):
        """Test URLs with paths."""
        assert normalize_url("example.com/path/to/page") == "https://example.com/path/to/page"
    
    def test_normalize_url_strips_whitespace(self):
        """Test that whitespace is stripped."""
        assert normalize_url("  example.com  ") == "https://example.com/"


class TestValidateUrl:
    """Tests for URL validation."""
    
    def test_valid_http_url(self):
        """Test that valid HTTP URLs pass validation."""
        is_valid, error = validate_url("http://example.com")
        assert is_valid is True
        assert error is None
    
    def test_valid_https_url(self):
        """Test that valid HTTPS URLs pass validation."""
        is_valid, error = validate_url("https://example.com")
        assert is_valid is True
        assert error is None
    
    def test_valid_url_with_port(self):
        """Test URLs with port numbers."""
        is_valid, error = validate_url("https://example.com:8080")
        assert is_valid is True
        assert error is None
    
    def test_valid_url_with_path(self):
        """Test URLs with paths."""
        is_valid, error = validate_url("https://example.com/path/to/page")
        assert is_valid is True
        assert error is None
    
    def test_invalid_scheme_ftp(self):
        """Test that FTP URLs are rejected."""
        is_valid, error = validate_url("ftp://example.com")
        assert is_valid is False
        assert "Unsupported URL scheme" in error
    
    def test_invalid_scheme_file(self):
        """Test that file:// URLs are rejected."""
        is_valid, error = validate_url("file:///etc/passwd")
        assert is_valid is False
        assert "Unsupported URL scheme" in error
    
    def test_localhost_rejected(self):
        """Test that localhost URLs are rejected."""
        is_valid, error = validate_url("http://localhost")
        assert is_valid is False
        assert "Localhost" in error or "localhost" in error
    
    def test_private_ip_rejected(self):
        """Test that private IP addresses are rejected."""
        private_ips = [
            "http://127.0.0.1",
            "http://10.0.0.1",
            "http://192.168.1.1",
            "http://172.16.0.1",
        ]
        
        for ip_url in private_ips:
            is_valid, error = validate_url(ip_url)
            assert is_valid is False, f"Private IP should be rejected: {ip_url}"
            assert "Private IP" in error or "private" in error.lower()
    
    def test_cloud_metadata_endpoint_rejected(self):
        """Test that cloud metadata endpoints are rejected."""
        is_valid, error = validate_url("http://169.254.169.254/latest/meta-data/")
        assert is_valid is False
        # This IP is caught by the private IP check, which is fine
        assert "private" in error.lower() or "metadata" in error.lower()
    
    def test_url_without_hostname(self):
        """Test that URLs without hostname are rejected."""
        is_valid, error = validate_url("https://")
        assert is_valid is False
        assert "hostname" in error.lower()


class TestValidateRedirectUrl:
    """Tests for redirect URL validation."""
    
    def test_valid_redirect(self):
        """Test that valid redirects pass validation."""
        is_valid, error = validate_redirect_url(
            "https://www.example.com",
            "https://example.com"
        )
        assert is_valid is True
        assert error is None
    
    def test_https_to_http_redirect_rejected(self):
        """Test that HTTPS to HTTP redirects are rejected."""
        is_valid, error = validate_redirect_url(
            "http://example.com",
            "https://example.com"
        )
        assert is_valid is False
        assert "HTTPS to HTTP" in error
    
    def test_http_to_https_redirect_allowed(self):
        """Test that HTTP to HTTPS redirects are allowed."""
        is_valid, error = validate_redirect_url(
            "https://example.com",
            "http://example.com"
        )
        assert is_valid is True
        assert error is None
    
    def test_redirect_to_private_ip_rejected(self):
        """Test that redirects to private IPs are rejected."""
        is_valid, error = validate_redirect_url(
            "http://192.168.1.1",
            "https://example.com"
        )
        assert is_valid is False


class TestExtractHostname:
    """Tests for hostname extraction."""
    
    def test_extract_hostname_simple(self):
        """Test extracting hostname from simple URL."""
        assert extract_hostname("https://example.com") == "example.com"
    
    def test_extract_hostname_with_port(self):
        """Test extracting hostname from URL with port."""
        assert extract_hostname("https://example.com:8080") == "example.com"
    
    def test_extract_hostname_with_path(self):
        """Test extracting hostname from URL with path."""
        assert extract_hostname("https://example.com/path/to/page") == "example.com"
    
    def test_extract_hostname_invalid_url(self):
        """Test extracting hostname from invalid URL."""
        assert extract_hostname("not a url") is None
