"""Core orchestrator — ties detection, extraction, and download together."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import httpx

from social_video_scraper.detector import Platform, detect_platform, is_short_url
from social_video_scraper.cookies import get_chrome_cookies
from social_video_scraper.extractors.base import (
    VideoInfo,
    PlatformNotSupported,
    ExtractionFailed,
)
from social_video_scraper.extractors.twitter import TwitterExtractor
from social_video_scraper.extractors.instagram import InstagramExtractor
from social_video_scraper.extractors.tiktok import TikTokExtractor
from social_video_scraper.extractors.facebook import FacebookExtractor
from social_video_scraper.downloader import download_video


# Which cookies each platform needs, and from which domain
PLATFORM_CONFIG = {
    Platform.TWITTER: {
        "extractor": TwitterExtractor,
        "cookie_domain": "x.com",
        "cookie_names": ["auth_token", "ct0"],
    },
    Platform.INSTAGRAM: {
        "extractor": InstagramExtractor,
        "cookie_domain": "instagram.com",
        "cookie_names": ["sessionid", "csrftoken", "ds_user_id"],
    },
    Platform.TIKTOK: {
        "extractor": TikTokExtractor,
        "cookie_domain": "tiktok.com",
        "cookie_names": None,  # Works without cookies for public videos
    },
    Platform.FACEBOOK: {
        "extractor": FacebookExtractor,
        "cookie_domain": "facebook.com",
        "cookie_names": ["c_user", "xs", "datr"],
    },
}


@dataclass
class ScrapeResult:
    """Result of a video scrape operation."""

    filepath: str
    video_info: VideoInfo
    filesize_bytes: int

    @property
    def filesize_mb(self) -> float:
        return self.filesize_bytes / (1024 * 1024)


def resolve_short_url(url: str) -> str:
    """Follow redirects on short URLs to get the canonical URL."""
    try:
        resp = httpx.head(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
                )
            },
            follow_redirects=True,
            timeout=15,
        )
        return str(resp.url)
    except Exception:
        return url


def extract_video_info(
    url: str,
    browser: str = "chrome",
) -> VideoInfo:
    """
    Extract video info (URL + metadata) without downloading.

    Args:
        url: The social media post URL
        browser: Browser to extract cookies from (currently only "chrome")

    Returns:
        VideoInfo with the direct MP4 URL and metadata
    """
    # Resolve short URLs
    if is_short_url(url):
        url = resolve_short_url(url)

    # Detect platform
    result = detect_platform(url)
    if result is None:
        raise PlatformNotSupported(
            f"URL not recognized: {url}\n"
            f"Supported platforms: Twitter/X, Instagram, TikTok, Facebook"
        )

    platform, post_id = result
    config = PLATFORM_CONFIG[platform]

    # Get cookies
    cookies = {}
    if config["cookie_names"] is not None:
        cookies = get_chrome_cookies(config["cookie_domain"], config["cookie_names"])

    # Create extractor and extract
    extractor_cls = config["extractor"]
    extractor = extractor_cls(cookies)

    return extractor.extract(url, post_id)


def scrape_video(
    url: str,
    output_dir: str = ".",
    browser: str = "chrome",
    filename: Optional[str] = None,
    show_progress: bool = True,
) -> ScrapeResult:
    """
    Main entry point: scrape and download a video from a social media URL.

    Args:
        url: The social media post URL
        output_dir: Directory to save the downloaded video
        browser: Browser to extract cookies from
        filename: Optional custom filename (without extension)
        show_progress: Whether to show download progress

    Returns:
        ScrapeResult with file path, metadata, and file size
    """
    # Extract video info
    info = extract_video_info(url, browser)

    # Determine output filename
    if filename:
        out_filename = filename if filename.endswith(".mp4") else f"{filename}.mp4"
    else:
        out_filename = info.suggested_filename()

    output_path = os.path.join(output_dir, out_filename)

    # Download
    if show_progress:
        print(f"  Platform: {info.platform}")
        if info.author:
            print(f"  Author:   @{info.author}")
        if info.width and info.height:
            print(f"  Quality:  {info.width}x{info.height}")
        if info.bitrate:
            print(f"  Bitrate:  {info.bitrate // 1000}kbps")
        print(f"  Saving:   {output_path}")

    download_video(
        url=info.url,
        output_path=output_path,
        headers=info.headers if info.headers else None,
        show_progress=show_progress,
    )

    filesize = os.path.getsize(output_path)

    return ScrapeResult(
        filepath=output_path,
        video_info=info,
        filesize_bytes=filesize,
    )
