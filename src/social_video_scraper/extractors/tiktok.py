"""TikTok video extractor using page HTML scraping."""

from __future__ import annotations

import json
import re

import httpx

from social_video_scraper.extractors.base import (
    BaseExtractor,
    VideoInfo,
    VideoNotFound,
    ExtractionFailed,
)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


class TikTokExtractor(BaseExtractor):
    """Extract videos from TikTok posts.

    TikTok embeds video data in the page HTML via a hydration script tag.
    For public videos, cookies are not required.
    """

    PLATFORM = "tiktok"
    REQUIRED_COOKIES = []  # Public videos don't need auth

    def extract(self, url: str, post_id: str) -> VideoInfo:
        # Resolve short URLs first
        canonical_url, resolved_id = self._resolve_url(url, post_id)

        # Try HTML scrape first (most reliable), then API
        try:
            return self._extract_via_html(canonical_url, resolved_id)
        except Exception as first_error:
            try:
                return self._extract_via_api(resolved_id)
            except Exception as second_error:
                raise ExtractionFailed(
                    f"All extraction methods failed.\n"
                    f"  HTML scrape: {first_error}\n"
                    f"  API: {second_error}"
                )

    def _resolve_url(self, url: str, post_id: str) -> tuple[str, str]:
        """Resolve short URLs (vm.tiktok.com, tiktok.com/t/) to canonical form."""
        if "vm.tiktok.com" in url or "/t/" in url:
            try:
                resp = httpx.head(
                    url,
                    headers={"User-Agent": USER_AGENT},
                    follow_redirects=True,
                    timeout=15,
                )
                canonical = str(resp.url)
                # Extract video ID from canonical URL
                match = re.search(r"/video/(\d+)", canonical)
                if match:
                    return canonical, match.group(1)
            except Exception:
                pass
        return url, post_id

    def _extract_via_html(self, url: str, video_id: str) -> VideoInfo:
        """Extract video data from the hydration script in page HTML."""
        resp = httpx.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.tiktok.com/",
            },
            cookies=self.cookies,
            timeout=30,
            follow_redirects=True,
        )
        resp.raise_for_status()
        html = resp.text

        # Look for the universal data hydration script
        # Pattern: <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">...</script>
        match = re.search(
            r'<script\s+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
            html,
            re.DOTALL,
        )

        if not match:
            # Fallback: look for SIGI_STATE
            match = re.search(
                r'<script\s+id="SIGI_STATE"[^>]*>(.*?)</script>',
                html,
                re.DOTALL,
            )

        if not match:
            raise ExtractionFailed("Could not find hydration data in TikTok page HTML.")

        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            raise ExtractionFailed(f"Failed to parse hydration JSON: {e}")

        # Navigate to video data
        # Path: __DEFAULT_SCOPE__ -> webapp.video-detail -> itemInfo -> itemStruct
        video_detail = (
            data.get("__DEFAULT_SCOPE__", {})
            .get("webapp.video-detail", {})
            .get("itemInfo", {})
            .get("itemStruct", {})
        )

        if not video_detail:
            # Try SIGI_STATE path
            video_detail = (
                data.get("ItemModule", {})
                .get(video_id, {})
            )

        if not video_detail:
            raise ExtractionFailed("Could not find video detail in hydration data.")

        video = video_detail.get("video", {})
        author_info = video_detail.get("author", {})

        # Get the best video URL
        # downloadAddr is sometimes higher quality than playAddr
        download_url = video.get("downloadAddr", "") or video.get("playAddr", "")

        if not download_url:
            # Try bitrateInfo for multiple quality levels
            bitrate_info = video.get("bitrateInfo", [])
            if bitrate_info:
                # Sort by bitrate descending
                bitrate_info.sort(key=lambda x: x.get("Bitrate", 0), reverse=True)
                download_url = bitrate_info[0].get("PlayAddr", {}).get("UrlList", [""])[0]

        if not download_url:
            raise ExtractionFailed("No video URL found in TikTok data.")

        return VideoInfo(
            url=download_url,
            platform=self.PLATFORM,
            post_id=video_id,
            width=video.get("width"),
            height=video.get("height"),
            duration_ms=video.get("duration", 0) * 1000 if video.get("duration") else None,
            author=author_info.get("uniqueId") or author_info.get("nickname"),
            description=video_detail.get("desc", "")[:100],
            headers={
                "User-Agent": USER_AGENT,
                "Referer": "https://www.tiktok.com/",
            },
        )

    def _extract_via_api(self, video_id: str) -> VideoInfo:
        """Try the web API endpoint as a fallback."""
        resp = httpx.get(
            "https://www.tiktok.com/api/item/detail/",
            params={"itemId": video_id},
            headers={
                "User-Agent": USER_AGENT,
                "Referer": f"https://www.tiktok.com/@user/video/{video_id}",
            },
            cookies=self.cookies,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        item_info = data.get("itemInfo", {}).get("itemStruct", {})
        if not item_info:
            raise VideoNotFound(f"TikTok video {video_id} not found via API.")

        video = item_info.get("video", {})
        download_url = video.get("downloadAddr", "") or video.get("playAddr", "")

        if not download_url:
            raise ExtractionFailed("No video URL in API response.")

        author_info = item_info.get("author", {})

        return VideoInfo(
            url=download_url,
            platform=self.PLATFORM,
            post_id=video_id,
            width=video.get("width"),
            height=video.get("height"),
            duration_ms=video.get("duration", 0) * 1000 if video.get("duration") else None,
            author=author_info.get("uniqueId"),
            description=item_info.get("desc", "")[:100],
            headers={
                "User-Agent": USER_AGENT,
                "Referer": "https://www.tiktok.com/",
            },
        )
