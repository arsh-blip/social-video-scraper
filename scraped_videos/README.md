# Scraped Videos — Video Scripting Reference

Source material for building out video-scripting and hook-direction skills.
Each video has three files keyed by YouTube video ID:

- `<id>.md` — human-readable transcript with timestamps + metadata header
- `<id>.txt` — plain transcript text (useful for feeding into LLMs)
- `<id>.json` — full structured record (metadata + per-segment timing)

## Index

### Long-form scripting frameworks

| Video | Channel | Files |
|---|---|---|
| [This AI Writes Better Scripts than 99% of YouTubers](https://www.youtube.com/watch?v=1wrYP4ayp4I) | Youri van Hofwegen | [`md`](./1wrYP4ayp4I.md) · [`txt`](./1wrYP4ayp4I.txt) · [`json`](./1wrYP4ayp4I.json) |
| [EXACTLY How to Write INSANELY Good YouTube Scripts with AI](https://www.youtube.com/watch?v=jaOIw-NiEPM) | Youri van Hofwegen | [`md`](./jaOIw-NiEPM.md) · [`txt`](./jaOIw-NiEPM.txt) · [`json`](./jaOIw-NiEPM.json) |

### Hooks (long-form)

| Video | Channel | Files |
|---|---|---|
| [I studied 100+ hooks, this strategy will make you go viral](https://www.youtube.com/watch?v=dNT7gd3ulAg) | Jade Beason | [`md`](./dNT7gd3ulAg.md) · [`txt`](./dNT7gd3ulAg.txt) · [`json`](./dNT7gd3ulAg.json) |
| [Give me 15 mins, and I'll make your hooks impossible to skip](https://www.youtube.com/watch?v=2byPP_9F0-Q) | Kallaway | [`md`](./2byPP_9F0-Q.md) · [`txt`](./2byPP_9F0-Q.txt) · [`json`](./2byPP_9F0-Q.json) |
| [The NEW Way to WIN on Social Media in 2026](https://www.youtube.com/watch?v=ImzoNTrgvFg) | Kallaway | [`md`](./ImzoNTrgvFg.md) · [`txt`](./ImzoNTrgvFg.txt) · [`json`](./ImzoNTrgvFg.json) |

### Hook templates (shorts)

| Video | Channel | Files |
|---|---|---|
| [Steal These 5 Viral Storytelling Hooks Pt.4](https://www.youtube.com/shorts/GsfbnzN77NY) | Ryan Spenner | [`md`](./GsfbnzN77NY.md) · [`txt`](./GsfbnzN77NY.txt) · [`json`](./GsfbnzN77NY.json) |
| [Steal These 5 Visual Hooks Pt. 7](https://www.youtube.com/shorts/xbi3CKpvUAI) | Ryan Spenner | [`md`](./xbi3CKpvUAI.md) · [`txt`](./xbi3CKpvUAI.txt) · [`json`](./xbi3CKpvUAI.json) |

## Synthesis docs

The reusable frameworks distilled from these transcripts live in
[`../lessons/`](../lessons/):

- [`dr-ad-script-frameworks.md`](../lessons/dr-ad-script-frameworks.md) — full scripting frameworks adapted for 30–60s direct-response ads.
- [`visual-hooks-for-ai-scene-generation.md`](../lessons/visual-hooks-for-ai-scene-generation.md) — visual hook archetypes and direction prompts for AI scene generation.

## Re-scraping / adding more videos

```bash
pip3 install youtube-transcript-api
python3 scripts/scrape_youtube_scripts.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The scraper script lives at [`../scripts/scrape_youtube_scripts.py`](../scripts/scrape_youtube_scripts.py).
It writes to this directory and handles `/watch?v=`, `/shorts/`, and `youtu.be/`
URLs. Includes exponential backoff + per-video error isolation for YouTube's
transient IP rate limits.
