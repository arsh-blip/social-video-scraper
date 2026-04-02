"""Twitter/X video extractor using the GraphQL TweetDetail API."""

from __future__ import annotations

import json
from typing import Any

import httpx

from social_video_scraper.extractors.base import (
    BaseExtractor,
    VideoInfo,
    AuthenticationRequired,
    VideoNotFound,
    ExtractionFailed,
)

# Public bearer token — same for all Twitter web clients (used by yt-dlp, gallery-dl, etc.)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

# GraphQL query ID for TweetDetail — these rotate but are stable for months
TWEET_DETAIL_QUERY_IDS = [
    "CysGzLIZa76UzZ3WTe-Bhg",
    "xOhkmRac04YFZDOzSHt3ng",
    "V7H0Ap3_Hh2FyS75OCDO3Q",
]

# Feature flags required by the API
FEATURES = {
    "rweb_video_screen_enabled": False,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "responsive_web_profile_redirect_enabled": False,
    "rweb_tipjar_consumption_enabled": False,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "premium_content_api_read_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
    "responsive_web_grok_analyze_post_followups_enabled": True,
    "responsive_web_jetfuel_frame": True,
    "responsive_web_grok_share_attachment_enabled": True,
    "responsive_web_grok_annotations_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "content_disclosure_indicator_enabled": True,
    "content_disclosure_ai_generated_indicator_enabled": True,
    "responsive_web_grok_show_grok_translated_post": True,
    "responsive_web_grok_analysis_button_from_backend": True,
    "post_ctas_fetch_enabled": True,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": False,
    "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_grok_imagine_annotation_enabled": True,
    "responsive_web_grok_community_note_auto_translation_is_enabled": False,
    "responsive_web_enhance_cards_enabled": False,
}

FIELD_TOGGLES = {
    "withArticleRichContentState": True,
    "withArticlePlainText": False,
    "withArticleSummaryText": True,
    "withArticleVoiceOver": True,
    "withGrokAnalyze": False,
    "withDisallowedReplyControls": False,
}


class TwitterExtractor(BaseExtractor):
    """Extract videos from Twitter/X posts."""

    PLATFORM = "twitter"
    REQUIRED_COOKIES = ["auth_token", "ct0"]

    def extract(self, url: str, post_id: str) -> VideoInfo:
        ct0 = self.cookies.get("ct0", "")
        auth_token = self.cookies.get("auth_token", "")

        if not ct0 or not auth_token:
            raise AuthenticationRequired(
                "Twitter requires 'auth_token' and 'ct0' cookies. "
                "Please log into Twitter/X in Chrome first."
            )

        # Try each known query ID
        data = None
        last_error = None
        for query_id in TWEET_DETAIL_QUERY_IDS:
            try:
                data = self._fetch_tweet_detail(post_id, query_id, ct0, auth_token)
                if data:
                    break
            except Exception as e:
                last_error = e
                continue

        if data is None:
            raise ExtractionFailed(
                f"All GraphQL query IDs failed. Last error: {last_error}"
            )

        # Navigate the response to find video info
        video_info = self._find_video_info(data)
        if not video_info:
            raise VideoNotFound(
                f"No video found in tweet {post_id}. It may be an image-only post."
            )

        # Get the best quality MP4 variant
        variants = video_info.get("variants", [])
        mp4_variants = [v for v in variants if v.get("content_type") == "video/mp4"]

        if not mp4_variants:
            raise ExtractionFailed("No MP4 variants found in video info.")

        # Sort by bitrate descending, pick the best
        mp4_variants.sort(key=lambda v: v.get("bitrate", 0), reverse=True)
        best = mp4_variants[0]

        # Try to get author info
        author = self._find_author(data)
        aspect_ratio = video_info.get("aspect_ratio", [])
        duration_ms = video_info.get("duration_millis")

        # Calculate dimensions from aspect ratio if available
        width, height = None, None
        if aspect_ratio and len(aspect_ratio) == 2:
            # Estimate from the URL (e.g., /vid/avc1/720x1280/)
            url_str = best["url"]
            import re
            dim_match = re.search(r"/(\d+)x(\d+)/", url_str)
            if dim_match:
                width, height = int(dim_match.group(1)), int(dim_match.group(2))

        return VideoInfo(
            url=best["url"],
            platform=self.PLATFORM,
            post_id=post_id,
            width=width,
            height=height,
            bitrate=best.get("bitrate"),
            duration_ms=duration_ms,
            author=author,
        )

    def _fetch_tweet_detail(
        self, tweet_id: str, query_id: str, ct0: str, auth_token: str
    ) -> dict[str, Any]:
        """Fetch tweet detail from the GraphQL API."""
        variables = {
            "focalTweetId": tweet_id,
            "with_rux_injections": False,
            "rankingMode": "Relevance",
            "includePromotedContent": True,
            "withCommunity": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withBirdwatchNotes": True,
            "withVoice": True,
        }

        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(FEATURES),
            "fieldToggles": json.dumps(FIELD_TOGGLES),
        }

        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "x-csrf-token": ct0,
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Referer": f"https://x.com/i/status/{tweet_id}",
            "Origin": "https://x.com",
        }

        cookies = {"auth_token": auth_token, "ct0": ct0}

        resp = httpx.get(
            f"https://x.com/i/api/graphql/{query_id}/TweetDetail",
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=30,
        )

        if resp.status_code == 401:
            raise AuthenticationRequired("Twitter auth_token cookie is expired. Please re-login.")
        if resp.status_code == 404:
            raise VideoNotFound(f"Tweet {tweet_id} not found.")

        resp.raise_for_status()
        return resp.json()

    def _find_video_info(self, data: dict) -> dict | None:
        """Recursively search the API response for video_info."""
        if isinstance(data, dict):
            if "video_info" in data:
                return data["video_info"]
            for value in data.values():
                result = self._find_video_info(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_video_info(item)
                if result:
                    return result
        return None

    def _find_author(self, data: dict) -> str | None:
        """Try to extract the tweet author's screen_name."""
        try:
            entries = (
                data.get("data", {})
                .get("tweetResult", {})
                .get("result", {})
                .get("core", {})
                .get("user_results", {})
                .get("result", {})
                .get("legacy", {})
            )
            return entries.get("screen_name")
        except Exception:
            pass

        # Fallback: search for screen_name near the top level
        def find_screen_name(obj):
            if isinstance(obj, dict):
                if "screen_name" in obj:
                    return obj["screen_name"]
                for v in obj.values():
                    r = find_screen_name(v)
                    if r:
                        return r
            elif isinstance(obj, list):
                for item in obj[:5]:  # limit depth
                    r = find_screen_name(item)
                    if r:
                        return r
            return None

        return find_screen_name(data)
