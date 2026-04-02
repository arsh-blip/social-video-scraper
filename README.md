# Social Video Scraper (svs)

Download videos from Twitter/X, Instagram, TikTok, and Facebook. Works as a CLI tool or as a Claude Code plugin (MCP server).

---

## Setup for the Team (Claude Code Plugin)

### Step 1: Install Python (one time)

Open Terminal and run:

```bash
python3 --version
```

If you see a version number (like `Python 3.9.6`), you're good. If not, download Python from https://www.python.org/downloads/

### Step 2: Install the tool (one time)

Open Terminal and paste this entire command:

```bash
pip3 install "git+https://github.com/arsh-blip/social-video-scraper.git"
```

### Step 3: Add to Claude Code (one time)

Open Claude Code and run this command:

```
/config
```

Then add this to the MCP servers section of your settings:

```json
{
  "mcpServers": {
    "social-video-scraper": {
      "command": "python3",
      "args": ["-m", "social_video_scraper.mcp_server"]
    }
  }
}
```

Or ask Claude Code: *"Add social-video-scraper as an MCP server"* and paste the above config.

### Step 4: Use it

Once set up, just paste any video link into Claude Code and ask:

> "Download this video: https://x.com/user/status/123456"

Claude will use the scraper tool automatically.

---

## Supported Platforms

| Platform | Example URL | Login Required? |
|---|---|---|
| Twitter/X | `https://x.com/user/status/123456` | Yes (be logged in on Chrome) |
| Instagram | `https://instagram.com/reel/ABC123/` | Yes (be logged in on Chrome) |
| TikTok | `https://tiktok.com/@user/video/123` | No |
| Facebook | `https://facebook.com/reel/123456` | Yes (be logged in on Chrome) |

**Important:** You need to be logged into each platform in Chrome on your Mac. The tool reads your browser cookies to authenticate.

---

## CLI Usage (Optional)

You can also use it directly from Terminal:

```bash
# Download a video
svs "https://x.com/user/status/123456"

# Download to a specific folder
svs "https://instagram.com/reel/ABC123/" -o ~/Downloads

# Just get the video URL without downloading
svs "https://x.com/user/status/123456" --no-download

# Get JSON output
svs "https://x.com/user/status/123456" --json-output
```

## Troubleshooting

**"Authentication required" error:** Make sure you're logged into the platform (Twitter, Instagram, etc.) in Chrome on your Mac.

**"pip3 not found":** Install Python from https://www.python.org/downloads/

**"Permission denied":** Try `pip3 install --user "git+https://github.com/arsh-blip/social-video-scraper.git"`

**Updating to latest version:** Run `pip3 install --upgrade "git+https://github.com/arsh-blip/social-video-scraper.git"`
