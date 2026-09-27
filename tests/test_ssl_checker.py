"""
Tests for SSL checker service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import ssl
import socket
from datetime import datetime, timedelta

from sitepulse.services.ssl_checker import SSLChecker


class TestSSLChecker:
    """Tests for SSLChecker class."""
    
    def test_initialization(self):
        """Test that SSLChecker initializes correctly."""
        checker = SSLChecker(timeout=5)
        assert checker.timeout == 5
    
    def test_http_url_rejected(self):
        """Test that HTTP URLs are rejected."""
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("http://example.com")
        
        assert success is False
        assert info['is_valid'] is False
        assert 'HTTPS' in info['error']
    
    @patch('sitepulse.services.ssl_checker.socket.create_connection')
    @patch('sitepulse.services.ssl_checker.ssl.create_default_context')
    def test_valid_certificate(self, mock_context, mock_connection):
        """Test checking a valid SSL certificate."""
        # Mock certificate with future expiry
        future_date = datetime.now() + timedelta(days=90)
        not_after_str = future_date.strftime('%b %d %H:%M:%S %Y GMT')
        
        mock_cert = {
            'notAfter': not_after_str
        }
        
        # Mock SSL socket
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = mock_cert
        mock_ssl_socket.__enter__ = Mock(return_value=mock_ssl_socket)
        mock_ssl_socket.__exit__ = Mock(return_value=False)
        
        # Mock regular socket
        mock_sock = MagicMock()
        mock_sock.__enter__ = Mock(return_value=mock_sock)
        mock_sock.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_sock
        
        # Mock SSL context
        mock_ctx = MagicMock()
        mock_ctx.wrap_socket.return_value = mock_ssl_socket
        mock_context.return_value = mock_ctx
        
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("https://example.com")
        
        assert success is True
        assert info['is_valid'] is True
        assert info['expiry_date'] is not None
        assert info['days_remaining'] > 0
        assert info['error'] is None
    
    @patch('sitepulse.services.ssl_checker.socket.create_connection')
    @patch('sitepulse.services.ssl_checker.ssl.create_default_context')
    def test_expired_certificate(self, mock_context, mock_connection):
        """Test checking an expired SSL certificate."""
        # Mock certificate with past expiry
        past_date = datetime.now() - timedelta(days=10)
        not_after_str = past_date.strftime('%b %d %H:%M:%S %Y GMT')
        
        mock_cert = {
            'notAfter': not_after_str
        }
        
        # Mock SSL socket
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = mock_cert
        mock_ssl_socket.__enter__ = Mock(return_value=mock_ssl_socket)
        mock_ssl_socket.__exit__ = Mock(return_value=False)
        
        # Mock regular socket
        mock_sock = MagicMock()
        mock_sock.__enter__ = Mock(return_value=mock_sock)
        mock_sock.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_sock
        
        # Mock SSL context
        mock_ctx = MagicMock()
        mock_ctx.wrap_socket.return_value = mock_ssl_socket
        mock_context.return_value = mock_ctx
        
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("https://example.com")
        
        assert success is True  # Check succeeded, but certificate is invalid
        assert info['is_valid'] is False
        assert info['days_remaining'] < 0
    
    @patch('sitepulse.services.ssl_checker.socket.create_connection')
    @patch('sitepulse.services.ssl_checker.ssl.create_default_context')
    def test_certificate_verification_error(self, mock_context, mock_connection):
        """Test handling certificate verification errors."""
        # Mock SSL context
        mock_ctx = MagicMock()
        mock_ctx.wrap_socket.side_effect = ssl.SSLCertVerificationError("Certificate verify failed")
        mock_context.return_value = mock_ctx
        
        # Mock regular socket
        mock_sock = MagicMock()
        mock_sock.__enter__ = Mock(return_value=mock_sock)
        mock_sock.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_sock
        
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("https://example.com")
        
        assert success is False
        assert info['is_valid'] is False
        assert 'verification failed' in info['error'].lower()
    
    @patch('sitepulse.services.ssl_checker.socket.create_connection')
    def test_connection_timeout(self, mock_connection):
        """Test handling connection timeout."""
        mock_connection.side_effect = socket.timeout("Connection timed out")
        
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("https://example.com")
        
        assert success is False
        assert 'timed out' in info['error'].lower()
    
    @patch('sitepulse.services.ssl_checker.socket.create_connection')
    def test_dns_failure(self, mock_connection):
        """Test handling DNS failure."""
        mock_connection.side_effect = socket.gaierror("Name or service not known")
        
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("https://nonexistent-website-12345.com")
        
        assert success is False
        assert 'DNS' in info['error'] or 'dns' in info['error'].lower()
    
    @patch('sitepulse.services.ssl_checker.socket.create_connection')
    def test_connection_refused(self, mock_connection):
        """Test handling connection refused."""
        mock_connection.side_effect = ConnectionRefusedError("Connection refused")
        
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("https://example.com")
        
        assert success is False
        assert 'refused' in info['error'].lower()
    
    @patch('sitepulse.services.ssl_checker.socket.create_connection')
    @patch('sitepulse.services.ssl_checker.ssl.create_default_context')
    def test_certificate_without_expiry(self, mock_context, mock_connection):
        """Test handling certificate without expiry information."""
        mock_cert = {}  # No notAfter field
        
        # Mock SSL socket
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = mock_cert
        mock_ssl_socket.__enter__ = Mock(return_value=mock_ssl_socket)
        mock_ssl_socket.__exit__ = Mock(return_value=False)
        
        # Mock regular socket
        mock_sock = MagicMock()
        mock_sock.__enter__ = Mock(return_value=mock_sock)
        mock_sock.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_sock
        
        # Mock SSL context
        mock_ctx = MagicMock()
        mock_ctx.wrap_socket.return_value = mock_ssl_socket
        mock_context.return_value = mock_ctx
        
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("https://example.com")
        
        assert success is False
        assert 'expiry information' in info['error'].lower()
    
    def test_invalid_url(self):
        """Test handling invalid URL."""
        checker = SSLChecker()
        success, info = checker.check_ssl_certificate("not a url")
        
        assert success is False
        assert info['error'] is not None
