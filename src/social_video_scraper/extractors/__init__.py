"""Platform-specific video extractors."""

from __future__ import annotations

from social_video_scraper.extractors.base import VideoInfo, BaseExtractor
from social_video_scraper.extractors.twitter import TwitterExtractor
from social_video_scraper.extractors.instagram import InstagramExtractor
from social_video_scraper.extractors.tiktok import TikTokExtractor
from social_video_scraper.extractors.facebook import FacebookExtractor

__all__ = [
    "VideoInfo",
    "BaseExtractor",
    "TwitterExtractor",
    "InstagramExtractor",
    "TikTokExtractor",
    "FacebookExtractor",
]
