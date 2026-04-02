"""Base extractor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VideoInfo:
    """Metadata and download URL for an extracted video."""

    url: str  # Direct MP4 download URL
    platform: str
    post_id: str
    width: Optional[int] = None
    height: Optional[int] = None
    bitrate: Optional[int] = None
    duration_ms: Optional[int] = None
    author: Optional[str] = None
    description: Optional[str] = None
    filename: Optional[str] = None  # Suggested filename
    headers: dict[str, str] = field(default_factory=dict)  # Headers needed for download

    def suggested_filename(self) -> str:
        """Generate a filename if none was set."""
        if self.filename:
            return self.filename
        parts = [self.platform]
        if self.author:
            parts.append(self.author)
        parts.append(self.post_id)
        return "_".join(parts) + ".mp4"


class ScraperError(Exception):
    """Base error for all scraper errors."""

    pass


class PlatformNotSupported(ScraperError):
    """URL doesn't match any supported platform."""

    pass


class AuthenticationRequired(ScraperError):
    """Cookies are missing or expired."""

    pass


class VideoNotFound(ScraperError):
    """Video was deleted, private, or doesn't exist."""

    pass


class ExtractionFailed(ScraperError):
    """Platform API returned unexpected data or changed format."""

    pass


class DownloadFailed(ScraperError):
    """Network error during download."""

    pass


class BaseExtractor(ABC):
    """Abstract base class for platform-specific video extractors."""

    def __init__(self, cookies: dict[str, str]):
        self.cookies = cookies

    @abstractmethod
    def extract(self, url: str, post_id: str) -> VideoInfo:
        """
        Extract the highest-quality video URL from a post.

        Args:
            url: The full URL of the post
            post_id: The extracted post/video ID

        Returns:
            VideoInfo with the direct MP4 URL and metadata

        Raises:
            AuthenticationRequired: If cookies are missing/expired
            VideoNotFound: If the video doesn't exist
            ExtractionFailed: If extraction logic fails
        """
        ...
