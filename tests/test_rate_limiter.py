"""Tests for rate limiter functionality."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.chatbot.rate_limiter import check_rate_limit, request_history, MAX_REQUESTS_PER_MINUTE


class TestRateLimiter:
    """Tests for rate limiter functionality."""

    def setup_method(self):
        """Clear request history before each test."""
        request_history.clear()

    def test_single_request_allowed(self):
        """Test that a single request is allowed."""
        result = check_rate_limit("192.168.1.1")
        assert result is True

    def test_multiple_requests_under_limit(self):
        """Test that multiple requests under the limit are allowed."""
        for _ in range(MAX_REQUESTS_PER_MINUTE - 1):
            result = check_rate_limit("192.168.1.1")
            assert result is True

    def test_request_at_limit_allowed(self):
        """Test that request at limit is allowed."""
        for _ in range(MAX_REQUESTS_PER_MINUTE):
            result = check_rate_limit("192.168.1.1")
            assert result is True

    def test_request_exceeds_limit(self):
        """Test that request exceeding limit is rejected."""
        # Fill up the limit
        for _ in range(MAX_REQUESTS_PER_MINUTE):
            check_rate_limit("192.168.1.1")

        # Next request should be rejected
        result = check_rate_limit("192.168.1.1")
        assert result is False

    def test_different_ips_separate_limits(self):
        """Test that different IP addresses have separate limits."""
        # Fill up limit for first IP
        for _ in range(MAX_REQUESTS_PER_MINUTE):
            check_rate_limit("192.168.1.1")

        # Second IP should still be able to make requests
        result = check_rate_limit("192.168.1.2")
        assert result is True

    @patch('src.chatbot.rate_limiter.datetime')
    def test_old_requests_removed_after_minute(self, mock_datetime):
        """Test that requests older than 1 minute are removed."""
        # Set initial time
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = now

        # Make requests up to the limit
        for _ in range(MAX_REQUESTS_PER_MINUTE):
            check_rate_limit("192.168.1.1")

        # Next request should be rejected
        result = check_rate_limit("192.168.1.1")
        assert result is False

        # Advance time by 1 minute and 1 second
        mock_datetime.now.return_value = now + timedelta(minutes=1, seconds=1)

        # Request should now be allowed (old ones cleaned up)
        result = check_rate_limit("192.168.1.1")
        assert result is True

    def test_unknown_ip_allowed(self):
        """Test that unknown IPs are allowed."""
        result = check_rate_limit("unknown")
        assert result is True
