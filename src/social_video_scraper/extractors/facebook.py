"""Facebook video extractor using page scraping."""

from __future__ import annotations

import re

import httpx

from social_video_scraper.extractors.base import (
    BaseExtractor,
    VideoInfo,
    AuthenticationRequired,
    VideoNotFound,
    ExtractionFailed,
)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


class FacebookExtractor(BaseExtractor):
    """Extract videos from Facebook posts, reels, and watch pages.

    Uses page scraping to find video URLs in serialized data within the HTML.
    Requires authenticated cookies for most content.
    """

    PLATFORM = "facebook"
    REQUIRED_COOKIES = ["c_user", "xs"]

    def extract(self, url: str, post_id: str) -> VideoInfo:
        c_user = self.cookies.get("c_user", "")
        xs = self.cookies.get("xs", "")

        if not c_user or not xs:
            raise AuthenticationRequired(
                "Facebook requires 'c_user' and 'xs' cookies. "
                "Please log into Facebook in Chrome first."
            )

        # Resolve short URLs
        canonical_url = self._resolve_url(url)

        # Try page scrape (most reliable for Facebook)
        try:
            return self._extract_via_page_scrape(canonical_url, post_id)
        except Exception as first_error:
            try:
                return self._extract_via_graphql(canonical_url, post_id)
            except Exception as second_error:
                raise ExtractionFailed(
                    f"All extraction methods failed.\n"
                    f"  Page scrape: {first_error}\n"
                    f"  GraphQL: {second_error}"
                )

    def _resolve_url(self, url: str) -> str:
        """Resolve fb.watch and other short URLs."""
        if "fb.watch" in url:
            try:
                resp = httpx.head(
                    url,
                    headers={"User-Agent": USER_AGENT},
                    follow_redirects=True,
                    timeout=15,
                )
                return str(resp.url)
            except Exception:
                pass
        return url

    def _get_cookies(self) -> dict[str, str]:
        return {k: v for k, v in self.cookies.items() if v}

    def _extract_via_page_scrape(self, url: str, post_id: str) -> VideoInfo:
        """Scrape the page HTML for embedded video URLs."""
        resp = httpx.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            cookies=self._get_cookies(),
            timeout=30,
            follow_redirects=True,
        )
        resp.raise_for_status()
        html = resp.text

        # Try to find video URLs in the serialized data
        # Facebook embeds these as JSON strings with escaped URLs
        video_url = None
        video_url_sd = None

        # Pattern 1: HD video URL
        hd_patterns = [
            r'"playable_url_quality_hd"\s*:\s*"(https?:[^"]+)"',
            r'"hd_src"\s*:\s*"(https?:[^"]+)"',
            r'"browser_native_hd_url"\s*:\s*"(https?:[^"]+)"',
        ]
        for pattern in hd_patterns:
            match = re.search(pattern, html)
            if match:
                video_url = match.group(1).encode().decode("unicode_escape")
                break

        # Pattern 2: SD video URL (fallback)
        sd_patterns = [
            r'"playable_url"\s*:\s*"(https?:[^"]+)"',
            r'"sd_src"\s*:\s*"(https?:[^"]+)"',
            r'"browser_native_sd_url"\s*:\s*"(https?:[^"]+)"',
        ]
        for pattern in sd_patterns:
            match = re.search(pattern, html)
            if match:
                video_url_sd = match.group(1).encode().decode("unicode_escape")
                break

        # Use HD if available, otherwise SD
        final_url = video_url or video_url_sd

        if not final_url:
            # Last resort: look for any video CDN URL
            cdn_match = re.search(
                r'"(https?://video[^"]*?\.fbcdn\.net/[^"]+)"', html
            )
            if cdn_match:
                final_url = cdn_match.group(1).encode().decode("unicode_escape")

        if not final_url:
            raise ExtractionFailed(
                "Could not find video URL in Facebook page HTML. "
                "The video may be private or the page structure may have changed."
            )

        # Try to extract author/title
        author = None
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html)

        return VideoInfo(
            url=final_url,
            platform=self.PLATFORM,
            post_id=post_id,
            author=author,
            description=title_match.group(1)[:100] if title_match else None,
        )

    def _extract_via_graphql(self, url: str, post_id: str) -> VideoInfo:
        """Try the GraphQL API approach."""
        # First, get the page to extract fb_dtsg token
        resp = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT},
            cookies=self._get_cookies(),
            timeout=30,
            follow_redirects=True,
        )
        resp.raise_for_status()
        html = resp.text

        # Extract fb_dtsg token
        dtsg_match = re.search(r'"DTSGInitData"\s*,\s*\[\]\s*,\s*\{"token"\s*:\s*"([^"]+)"', html)
        if not dtsg_match:
            dtsg_match = re.search(r'name="fb_dtsg"\s+value="([^"]+)"', html)
        if not dtsg_match:
            raise ExtractionFailed("Could not extract fb_dtsg token.")

        fb_dtsg = dtsg_match.group(1)

        # Extract video ID from URL if not numeric
        video_id = post_id
        video_id_match = re.search(r'/videos/(\d+)', url) or re.search(r'/reel/(\d+)', url)
        if video_id_match:
            video_id = video_id_match.group(1)

        # Query the GraphQL API
        resp = httpx.post(
            "https://www.facebook.com/api/graphql/",
            data={
                "fb_dtsg": fb_dtsg,
                "doc_id": "5279476072161634",  # Video query doc_id
                "variables": f'{{"videoID":"{video_id}"}}',
            },
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            cookies=self._get_cookies(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        # Navigate response for video URLs
        progressive = (
            data.get("data", {})
            .get("video", {})
            .get("videoDeliveryLegacyResponse", {})
            .get("progressive", [])
        )

        if not progressive:
            raise ExtractionFailed("No progressive URLs in GraphQL response.")

        # Pick HD first, then SD
        progressive.sort(
            key=lambda x: 0 if x.get("metadata", {}).get("quality") == "HD" else 1
        )
        best = progressive[0]

        return VideoInfo(
            url=best["progressive_url"],
            platform=self.PLATFORM,
            post_id=post_id,
            width=best.get("metadata", {}).get("width"),
            height=best.get("metadata", {}).get("height"),
        )
