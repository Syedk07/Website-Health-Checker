"""
Tests for health checker service.
"""

import pytest
from unittest.mock import Mock, patch
import requests

from sitepulse.services.health_checker import HealthChecker
from sitepulse.models import CheckStatus


class TestHealthChecker:
    """Tests for HealthChecker class."""
    
    def test_initialization(self):
        """Test that HealthChecker initializes correctly."""
        checker = HealthChecker(timeout=5)
        assert checker.timeout == 5
        assert checker.session is not None
        checker.close()
    
    def test_check_invalid_url(self):
        """Test checking an invalid URL."""
        checker = HealthChecker()
        result = checker.check_website(1, "ftp://example.com")
        
        assert result.website_id == 1
        assert result.result_status == CheckStatus.INVALID_URL
        assert result.error_message is not None
        assert "Unsupported URL scheme" in result.error_message
        checker.close()
    
    def test_check_localhost_rejected(self):
        """Test that localhost URLs are rejected."""
        checker = HealthChecker()
        result = checker.check_website(1, "http://localhost")
        
        assert result.result_status == CheckStatus.INVALID_URL
        assert "Localhost" in result.error_message or "localhost" in result.error_message
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_successful_response(self, mock_get):
        """Test checking a website with successful response."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com/"
        mock_get.return_value = mock_response
        
        checker = HealthChecker()
        result = checker.check_website(1, "example.com")
        
        assert result.website_id == 1
        assert result.result_status == CheckStatus.SUCCESS
        assert result.status_code == 200
        assert result.response_time_ms is not None
        assert result.response_time_ms >= 0
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_http_error_response(self, mock_get):
        """Test checking a website with HTTP error response."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.url = "https://example.com/notfound"
        mock_get.return_value = mock_response
        
        checker = HealthChecker()
        result = checker.check_website(1, "https://example.com/notfound")
        
        assert result.result_status == CheckStatus.HTTP_ERROR
        assert result.status_code == 404
        assert result.response_time_ms is not None
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_server_error_response(self, mock_get):
        """Test checking a website with server error response."""
        # Mock 500 response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.url = "https://example.com/"
        mock_get.return_value = mock_response
        
        checker = HealthChecker()
        result = checker.check_website(1, "example.com")
        
        assert result.result_status == CheckStatus.HTTP_ERROR
        assert result.status_code == 500
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_redirect(self, mock_get):
        """Test checking a website that redirects."""
        # Mock redirect response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://www.example.com/"  # Redirected URL
        mock_get.return_value = mock_response
        
        checker = HealthChecker()
        result = checker.check_website(1, "https://example.com")
        
        assert result.result_status == CheckStatus.SUCCESS
        assert result.final_url == "https://www.example.com/"
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_timeout(self, mock_get):
        """Test checking a website that times out."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        checker = HealthChecker()
        result = checker.check_website(1, "example.com")
        
        assert result.result_status == CheckStatus.TIMEOUT
        assert result.status_code is None
        assert result.response_time_ms is None
        assert "timed out" in result.error_message.lower()
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_connection_error(self, mock_get):
        """Test checking a website with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        checker = HealthChecker()
        result = checker.check_website(1, "example.com")
        
        assert result.result_status == CheckStatus.CONNECTION_ERROR
        assert "Connection failed" in result.error_message
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_dns_failure(self, mock_get):
        """Test checking a website with DNS failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Failed to resolve hostname: Name or service not known"
        )
        
        checker = HealthChecker()
        result = checker.check_website(1, "nonexistent-website-12345.com")
        
        assert result.result_status == CheckStatus.DNS_FAILURE
        assert "DNS" in result.error_message
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_ssl_error(self, mock_get):
        """Test checking a website with SSL error."""
        mock_get.side_effect = requests.exceptions.SSLError("SSL certificate verify failed")
        
        checker = HealthChecker()
        result = checker.check_website(1, "https://example.com")
        
        assert result.result_status == CheckStatus.SSL_ERROR
        assert "SSL" in result.error_message
        checker.close()
    
    @patch('sitepulse.services.health_checker.requests.Session.get')
    def test_check_too_many_redirects(self, mock_get):
        """Test checking a website with too many redirects."""
        mock_get.side_effect = requests.exceptions.TooManyRedirects("Exceeded max redirects")
        
        checker = HealthChecker()
        result = checker.check_website(1, "example.com")
        
        assert result.result_status == CheckStatus.UNKNOWN_ERROR
        assert "redirect" in result.error_message.lower()
        checker.close()
    
    def test_url_normalization(self):
        """Test that URLs are normalized before checking."""
        checker = HealthChecker()
        
        # Test that URL without scheme gets normalized
        with patch.object(checker.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = "https://example.com/"
            mock_get.return_value = mock_response
            
            result = checker.check_website(1, "example.com")
            
            # Verify the normalized URL was used
            mock_get.assert_called_once()
            called_url = mock_get.call_args[0][0]
            assert called_url.startswith("https://")
        
        checker.close()
