"""
Tests for website service.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from sitepulse.database import init_database
from sitepulse.services import WebsiteService
from sitepulse.models import CheckResult, CheckStatus


@pytest.fixture
def website_service():
    """Create a website service with a temporary database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db_manager = init_database(db_path)
        service = WebsiteService(db_manager)
        yield service


class TestWebsiteService:
    """Tests for WebsiteService class."""
    
    def test_add_website(self, website_service):
        """Test adding a new website."""
        website = website_service.add_website("Example Site", "https://example.com")
        
        assert website is not None
        assert website.id is not None
        assert website.name == "Example Site"
        assert website.url == "https://example.com/"
        assert website.created_at is not None
    
    def test_add_duplicate_website(self, website_service):
        """Test that duplicate URLs are rejected."""
        website_service.add_website("Example 1", "https://example.com")
        duplicate = website_service.add_website("Example 2", "https://example.com")
        
        assert duplicate is None
    
    def test_add_website_normalizes_url(self, website_service):
        """Test that URLs are normalized when adding."""
        website = website_service.add_website("Example", "example.com")
        
        assert website is not None
        assert website.url == "https://example.com/"
    
    def test_get_website(self, website_service):
        """Test getting a website by ID."""
        created = website_service.add_website("Example", "https://example.com")
        retrieved = website_service.get_website(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
        assert retrieved.url == created.url
    
    def test_get_nonexistent_website(self, website_service):
        """Test getting a website that doesn't exist."""
        website = website_service.get_website(999)
        assert website is None
    
    def test_get_all_websites(self, website_service):
        """Test getting all websites."""
        website_service.add_website("Site 1", "https://example1.com")
        website_service.add_website("Site 2", "https://example2.com")
        website_service.add_website("Site 3", "https://example3.com")
        
        websites = website_service.get_all_websites()
        
        assert len(websites) == 3
        # Should be sorted by name
        assert websites[0].name == "Site 1"
        assert websites[1].name == "Site 2"
        assert websites[2].name == "Site 3"
    
    def test_get_all_websites_empty(self, website_service):
        """Test getting all websites when none exist."""
        websites = website_service.get_all_websites()
        assert len(websites) == 0
    
    def test_update_website_name(self, website_service):
        """Test updating a website's name."""
        website = website_service.add_website("Old Name", "https://example.com")
        success = website_service.update_website(website.id, name="New Name")
        
        assert success is True
        
        updated = website_service.get_website(website.id)
        assert updated.name == "New Name"
        assert updated.url == website.url
    
    def test_update_website_url(self, website_service):
        """Test updating a website's URL."""
        website = website_service.add_website("Example", "https://example.com")
        success = website_service.update_website(website.id, url="https://new-example.com")
        
        assert success is True
        
        updated = website_service.get_website(website.id)
        assert updated.name == "Example"
        assert updated.url == "https://new-example.com/"
    
    def test_update_website_both(self, website_service):
        """Test updating both name and URL."""
        website = website_service.add_website("Old Name", "https://example.com")
        success = website_service.update_website(
            website.id,
            name="New Name",
            url="https://new-example.com"
        )
        
        assert success is True
        
        updated = website_service.get_website(website.id)
        assert updated.name == "New Name"
        assert updated.url == "https://new-example.com/"
    
    def test_update_website_duplicate_url(self, website_service):
        """Test that updating to a duplicate URL fails."""
        website1 = website_service.add_website("Site 1", "https://example1.com")
        website2 = website_service.add_website("Site 2", "https://example2.com")
        
        # Try to update website2's URL to website1's URL
        success = website_service.update_website(website2.id, url="https://example1.com")
        
        assert success is False
    
    def test_update_nonexistent_website(self, website_service):
        """Test updating a website that doesn't exist."""
        success = website_service.update_website(999, name="New Name")
        assert success is False
    
    def test_delete_website(self, website_service):
        """Test deleting a website."""
        website = website_service.add_website("Example", "https://example.com")
        success = website_service.delete_website(website.id)
        
        assert success is True
        
        deleted = website_service.get_website(website.id)
        assert deleted is None
    
    def test_delete_nonexistent_website(self, website_service):
        """Test deleting a website that doesn't exist."""
        success = website_service.delete_website(999)
        assert success is False
    
    def test_save_check_result(self, website_service):
        """Test saving a check result."""
        website = website_service.add_website("Example", "https://example.com")
        
        result = CheckResult(
            id=None,
            website_id=website.id,
            checked_at=datetime.now().timestamp(),
            status_code=200,
            response_time_ms=150,
            result_status=CheckStatus.SUCCESS,
            final_url=None,
            error_message=None,
            ssl_valid=True,
            ssl_expiry_date="2025-12-31T00:00:00",
            ssl_days_remaining=100
        )
        
        result_id = website_service.save_check_result(result)
        
        assert result_id is not None
        assert result_id > 0
    
    def test_get_latest_check_result(self, website_service):
        """Test getting the latest check result."""
        website = website_service.add_website("Example", "https://example.com")
        
        # Save multiple results
        for i in range(3):
            result = CheckResult(
                id=None,
                website_id=website.id,
                checked_at=datetime.now().timestamp(),
                status_code=200 + i,
                response_time_ms=100 + i,
                result_status=CheckStatus.SUCCESS
            )
            website_service.save_check_result(result)
        
        latest = website_service.get_latest_check_result(website.id)
        
        assert latest is not None
        assert latest.status_code == 202  # Last one saved
    
    def test_get_latest_check_result_none(self, website_service):
        """Test getting latest check result when none exist."""
        website = website_service.add_website("Example", "https://example.com")
        latest = website_service.get_latest_check_result(website.id)
        
        assert latest is None
    
    def test_get_check_history(self, website_service):
        """Test getting check history."""
        website = website_service.add_website("Example", "https://example.com")
        
        # Save some results
        for i in range(5):
            result = CheckResult(
                id=None,
                website_id=website.id,
                checked_at=datetime.now().timestamp(),
                status_code=200,
                response_time_ms=100 + i,
                result_status=CheckStatus.SUCCESS
            )
            website_service.save_check_result(result)
        
        history = website_service.get_check_history(website_id=website.id)
        
        assert len(history) == 5
        # Should be ordered by checked_at DESC
        assert history[0].response_time_ms > history[-1].response_time_ms
    
    def test_get_check_history_with_limit(self, website_service):
        """Test getting check history with a limit."""
        website = website_service.add_website("Example", "https://example.com")
        
        # Save some results
        for i in range(5):
            result = CheckResult(
                id=None,
                website_id=website.id,
                checked_at=datetime.now().timestamp(),
                status_code=200,
                response_time_ms=100,
                result_status=CheckStatus.SUCCESS
            )
            website_service.save_check_result(result)
        
        history = website_service.get_check_history(website_id=website.id, limit=2)
        
        assert len(history) == 2
    
    def test_get_check_history_all_websites(self, website_service):
        """Test getting check history for all websites."""
        website1 = website_service.add_website("Site 1", "https://example1.com")
        website2 = website_service.add_website("Site 2", "https://example2.com")
        
        # Save results for both
        for website in [website1, website2]:
            for i in range(2):
                result = CheckResult(
                    id=None,
                    website_id=website.id,
                    checked_at=datetime.now().timestamp(),
                    status_code=200,
                    response_time_ms=100,
                    result_status=CheckStatus.SUCCESS
                )
                website_service.save_check_result(result)
        
        history = website_service.get_check_history()
        
        assert len(history) == 4
