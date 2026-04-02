"""Platform detection from URL."""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional


class Platform(Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"


# Map platform -> list of (regex_pattern, group_index_for_post_id)
PATTERNS: dict[Platform, list[str]] = {
    Platform.TWITTER: [
        r"(?:twitter\.com|x\.com)/\w+/status/(\d+)",
    ],
    Platform.INSTAGRAM: [
        r"instagram\.com/(?:reel|p|reels)/([A-Za-z0-9_-]+)",
    ],
    Platform.TIKTOK: [
        r"tiktok\.com/@[\w.]+/video/(\d+)",
        r"vm\.tiktok\.com/([\w]+)",
        r"tiktok\.com/t/([\w]+)",
    ],
    Platform.FACEBOOK: [
        r"facebook\.com/.+/videos/(\d+)",
        r"facebook\.com/reel/(\d+)",
        r"facebook\.com/watch/?\?v=(\d+)",
        r"fb\.watch/([\w]+)",
    ],
}

# Short URL domains that need redirect resolution
SHORT_URL_DOMAINS = {"vm.tiktok.com", "fb.watch"}


def detect_platform(url: str) -> Optional[tuple[Platform, str]]:
    """
    Detect the platform and extract the post/video ID from a URL.

    Returns (Platform, post_id) or None if unrecognized.
    """
    for platform, patterns in PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return platform, match.group(1)
    return None


def is_short_url(url: str) -> bool:
    """Check if a URL is a short/redirect URL that needs resolution."""
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname or ""
    return hostname in SHORT_URL_DOMAINS
