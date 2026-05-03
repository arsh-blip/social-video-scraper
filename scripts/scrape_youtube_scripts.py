"""Scrape YouTube videos for transcripts and metadata, save as Markdown + JSON.

Usage:
    python scripts/scrape_youtube_scripts.py <youtube_url> [<youtube_url> ...]

Output goes to scraped_videos/<video_id>.{md,json,txt}.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import IpBlocked, RequestBlocked

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "scraped_videos"


@dataclass
class VideoRecord:
    video_id: str
    url: str
    title: str
    author: str
    author_url: str
    thumbnail_url: str
    transcript_segments: list[dict]
    transcript_text: str


def extract_video_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname in {"youtu.be"}:
        return parsed.path.lstrip("/")
    qs = urllib.parse.parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]
    m = re.search(r"/(?:embed|shorts|live)/([A-Za-z0-9_-]{11})", parsed.path)
    if m:
        return m.group(1)
    raise ValueError(f"Could not extract video ID from {url!r}")


def fetch_oembed(url: str) -> dict:
    api = "https://www.youtube.com/oembed?" + urllib.parse.urlencode(
        {"url": url, "format": "json"}
    )
    with urllib.request.urlopen(api, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_transcript(video_id: str, max_attempts: int = 6) -> list[dict]:
    api = YouTubeTranscriptApi()
    delay = 30
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            fetched = api.fetch(video_id)
            return [
                {"text": s.text, "start": s.start, "duration": s.duration}
                for s in fetched
            ]
        except (IpBlocked, RequestBlocked) as e:
            last_err = e
            print(f"  [transcript] blocked (attempt {attempt}/{max_attempts}); sleeping {delay}s")
            time.sleep(delay)
            delay = min(delay * 2, 240)
    raise last_err or RuntimeError("transcript fetch failed")


def format_timestamp(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"


def scrape(url: str) -> VideoRecord:
    video_id = extract_video_id(url)
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    meta = fetch_oembed(canonical_url)
    segments = fetch_transcript(video_id)
    transcript_text = " ".join(seg["text"].replace("\n", " ") for seg in segments)
    return VideoRecord(
        video_id=video_id,
        url=canonical_url,
        title=meta.get("title", ""),
        author=meta.get("author_name", ""),
        author_url=meta.get("author_url", ""),
        thumbnail_url=meta.get("thumbnail_url", ""),
        transcript_segments=segments,
        transcript_text=transcript_text,
    )


def write_outputs(record: VideoRecord) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUT_DIR / f"{record.video_id}.json"
    json_path.write_text(json.dumps(asdict(record), indent=2, ensure_ascii=False))

    txt_path = OUT_DIR / f"{record.video_id}.txt"
    txt_path.write_text(record.transcript_text + "\n")

    md_lines = [
        f"# {record.title}",
        "",
        f"- **Channel:** [{record.author}]({record.author_url})",
        f"- **URL:** {record.url}",
        f"- **Video ID:** `{record.video_id}`",
        f"- **Thumbnail:** {record.thumbnail_url}",
        "",
        "## Transcript",
        "",
    ]
    for seg in record.transcript_segments:
        md_lines.append(f"- `{format_timestamp(seg['start'])}` {seg['text']}")
    md_lines.append("")
    md_lines.append("## Plain transcript")
    md_lines.append("")
    md_lines.append(record.transcript_text)
    md_lines.append("")
    (OUT_DIR / f"{record.video_id}.md").write_text("\n".join(md_lines))


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    failures: list[tuple[str, str]] = []
    for i, url in enumerate(argv):
        if i > 0:
            time.sleep(5)
        print(f"Scraping {url} ...")
        try:
            record = scrape(url)
            write_outputs(record)
            print(
                f"  -> {record.video_id} | {record.title} "
                f"({len(record.transcript_segments)} segments)"
            )
        except Exception as e:
            print(f"  !! FAILED: {type(e).__name__}: {e}")
            failures.append((url, str(e)))
    if failures:
        print(f"\n{len(failures)} failure(s):")
        for u, err in failures:
            print(f"  - {u}: {err[:120]}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
