# Scraped Videos — Video Scripting Reference

Source material for building out video-scripting skills. Each video has three
files keyed by YouTube video ID:

- `<id>.md` — human-readable transcript with timestamps + metadata header
- `<id>.txt` — plain transcript text (useful for feeding into LLMs)
- `<id>.json` — full structured record (metadata + per-segment timing)

## Index

| Video | Channel | Duration (segments) | Files |
|---|---|---|---|
| [This AI Writes Better Scripts than 99% of YouTubers](https://www.youtube.com/watch?v=1wrYP4ayp4I) | Youri van Hofwegen | 582 | [`1wrYP4ayp4I.md`](./1wrYP4ayp4I.md) · [`.txt`](./1wrYP4ayp4I.txt) · [`.json`](./1wrYP4ayp4I.json) |
| [EXACTLY How to Write INSANELY Good YouTube Scripts with AI](https://www.youtube.com/watch?v=jaOIw-NiEPM) | Youri van Hofwegen | 375 | [`jaOIw-NiEPM.md`](./jaOIw-NiEPM.md) · [`.txt`](./jaOIw-NiEPM.txt) · [`.json`](./jaOIw-NiEPM.json) |

## Re-scraping / adding more videos

```bash
pip3 install youtube-transcript-api
python3 scripts/scrape_youtube_scripts.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The scraper script lives at [`scripts/scrape_youtube_scripts.py`](../scripts/scrape_youtube_scripts.py).
It writes to this directory.
