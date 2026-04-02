"""Instagram video extractor using the web GraphQL API."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from social_video_scraper.extractors.base import (
    BaseExtractor,
    VideoInfo,
    AuthenticationRequired,
    VideoNotFound,
    ExtractionFailed,
)

# Instagram's public web app ID
IG_APP_ID = "936619743392459"

# Mobile-ish user agent that works better with IG APIs
USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)


def shortcode_to_media_id(shortcode: str) -> int:
    """Convert an Instagram shortcode to a numeric media ID."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    media_id = 0
    for char in shortcode:
        media_id = media_id * 64 + alphabet.index(char)
    return media_id


class InstagramExtractor(BaseExtractor):
    """Extract videos from Instagram posts and reels."""

    PLATFORM = "instagram"
    REQUIRED_COOKIES = ["sessionid"]

    def extract(self, url: str, post_id: str) -> VideoInfo:
        sessionid = self.cookies.get("sessionid", "")
        csrftoken = self.cookies.get("csrftoken", "")

        if not sessionid:
            raise AuthenticationRequired(
                "Instagram requires a 'sessionid' cookie. "
                "Please log into Instagram in Chrome first."
            )

        # Try the media info API first, then fall back to GraphQL
        try:
            return self._extract_via_media_api(post_id, sessionid, csrftoken)
        except Exception as first_error:
            try:
                return self._extract_via_graphql(post_id, sessionid, csrftoken)
            except Exception as second_error:
                try:
                    return self._extract_via_page_scrape(url, sessionid, csrftoken)
                except Exception as third_error:
                    raise ExtractionFailed(
                        f"All extraction methods failed.\n"
                        f"  Media API: {first_error}\n"
                        f"  GraphQL: {second_error}\n"
                        f"  Page scrape: {third_error}"
                    )

    def _get_headers(self, csrftoken: str) -> dict[str, str]:
        return {
            "User-Agent": USER_AGENT,
            "X-CSRFToken": csrftoken,
            "X-IG-App-ID": IG_APP_ID,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
        }

    def _get_cookies(self, sessionid: str, csrftoken: str) -> dict[str, str]:
        cookies = {"sessionid": sessionid}
        if csrftoken:
            cookies["csrftoken"] = csrftoken
        return cookies

    def _extract_via_media_api(
        self, shortcode: str, sessionid: str, csrftoken: str
    ) -> VideoInfo:
        """Use the /api/v1/media/{id}/info/ endpoint."""
        media_id = shortcode_to_media_id(shortcode)

        resp = httpx.get(
            f"https://www.instagram.com/api/v1/media/{media_id}/info/",
            headers=self._get_headers(csrftoken),
            cookies=self._get_cookies(sessionid, csrftoken),
            timeout=30,
        )

        if resp.status_code == 401:
            raise AuthenticationRequired("Instagram session expired.")
        resp.raise_for_status()

        data = resp.json()
        items = data.get("items", [])
        if not items:
            raise VideoNotFound(f"No media found for shortcode {shortcode}")

        return self._parse_media_item(items[0], shortcode)

    def _extract_via_graphql(
        self, shortcode: str, sessionid: str, csrftoken: str
    ) -> VideoInfo:
        """Use the GraphQL query endpoint."""
        variables = json.dumps({"shortcode": shortcode})

        resp = httpx.get(
            "https://www.instagram.com/graphql/query/",
            params={
                "query_hash": "b3055c01b4b222b8a47dc12b090e4e64",  # PostPage query
                "variables": variables,
            },
            headers=self._get_headers(csrftoken),
            cookies=self._get_cookies(sessionid, csrftoken),
            timeout=30,
        )

        resp.raise_for_status()
        data = resp.json()

        media = (
            data.get("data", {})
            .get("shortcode_media", {})
        )

        if not media:
            raise VideoNotFound(f"No media found via GraphQL for {shortcode}")

        if not media.get("is_video", False):
            raise VideoNotFound(f"Post {shortcode} is not a video.")

        video_url = media.get("video_url", "")
        if not video_url:
            raise ExtractionFailed("GraphQL response missing video_url")

        return VideoInfo(
            url=video_url,
            platform=self.PLATFORM,
            post_id=shortcode,
            width=media.get("dimensions", {}).get("width"),
            height=media.get("dimensions", {}).get("height"),
            author=media.get("owner", {}).get("username"),
            description=(media.get("edge_media_to_caption", {}).get("edges", [{}])[0]
                         .get("node", {}).get("text", ""))[:100] if media.get("edge_media_to_caption") else None,
        )

    def _extract_via_page_scrape(
        self, url: str, sessionid: str, csrftoken: str
    ) -> VideoInfo:
        """Scrape the page HTML for embedded video data."""
        resp = httpx.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Referer": "https://www.instagram.com/",
            },
            cookies=self._get_cookies(sessionid, csrftoken),
            timeout=30,
            follow_redirects=True,
        )
        resp.raise_for_status()

        # Look for video URL in various embedded data patterns
        html = resp.text

        # Pattern 1: og:video meta tag
        og_match = re.search(r'<meta\s+property="og:video"\s+content="([^"]+)"', html)
        if og_match:
            video_url = og_match.group(1).replace("&amp;", "&")
            shortcode_match = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
            post_id = shortcode_match.group(1) if shortcode_match else "unknown"
            return VideoInfo(
                url=video_url,
                platform=self.PLATFORM,
                post_id=post_id,
            )

        # Pattern 2: video_url in embedded JSON
        video_match = re.search(r'"video_url"\s*:\s*"(https?://[^"]+)"', html)
        if video_match:
            video_url = video_match.group(1).encode().decode("unicode_escape")
            shortcode_match = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
            post_id = shortcode_match.group(1) if shortcode_match else "unknown"
            return VideoInfo(
                url=video_url,
                platform=self.PLATFORM,
                post_id=post_id,
            )

        raise ExtractionFailed("Could not find video URL in page HTML.")

    def _parse_media_item(self, item: dict[str, Any], shortcode: str) -> VideoInfo:
        """Parse a media item from the API response."""
        video_versions = item.get("video_versions", [])
        if not video_versions:
            raise VideoNotFound(f"Post {shortcode} has no video versions (may be an image).")

        # First version is highest quality
        best = video_versions[0]

        user = item.get("user", {})
        caption = item.get("caption", {})

        return VideoInfo(
            url=best["url"],
            platform=self.PLATFORM,
            post_id=shortcode,
            width=best.get("width"),
            height=best.get("height"),
            author=user.get("username"),
            description=(caption.get("text", "")[:100] if caption else None),
        )
