"""Rate limiting for the chatbot."""

from collections import defaultdict
from datetime import datetime, timedelta

request_history = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 15


def check_rate_limit(ip_address: str) -> bool:
    """Check if IP address has exceeded rate limit.

    Args:
        ip_address: Client IP address

    Returns:
        True if request is allowed, False if rate limit exceeded
    """
    now = datetime.now()
    cutoff = now - timedelta(minutes=1)

    # Remove old requests
    request_history[ip_address] = [
        req_time for req_time in request_history[ip_address]
        if req_time > cutoff
    ]

    # Check limit
    if len(request_history[ip_address]) >= MAX_REQUESTS_PER_MINUTE:
        return False

    # Add this request
    request_history[ip_address].append(now)
    return True
