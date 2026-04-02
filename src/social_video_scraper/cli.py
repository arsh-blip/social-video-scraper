"""CLI interface for social-video-scraper."""

from __future__ import annotations

import json
import os
import sys

import click

from social_video_scraper.core import scrape_video, extract_video_info
from social_video_scraper.extractors.base import ScraperError


@click.command()
@click.argument("url")
@click.option(
    "-o", "--output",
    default=".",
    help="Output directory (default: current directory)",
)
@click.option(
    "-n", "--name",
    default=None,
    help="Custom filename (without extension)",
)
@click.option(
    "-b", "--browser",
    default="chrome",
    help="Browser to extract cookies from (default: chrome)",
)
@click.option(
    "--no-download",
    is_flag=True,
    help="Only extract the video URL, don't download",
)
@click.option(
    "--json-output", "json_out",
    is_flag=True,
    help="Output result as JSON",
)
def main(url: str, output: str, name: str, browser: str, no_download: bool, json_out: bool):
    """Download videos from Twitter/X, Instagram, TikTok, and Facebook.

    Pass a URL from any supported platform and the video will be downloaded
    to the output directory.

    \b
    Examples:
        svs "https://x.com/user/status/123456"
        svs "https://www.instagram.com/reel/ABC123/" -o ~/Videos
        svs "https://vm.tiktok.com/ZMhXYZ/" --no-download --json-output
        svs "https://www.facebook.com/reel/123456" -n "my_video"
    """
    try:
        if no_download:
            info = extract_video_info(url, browser)
            if json_out:
                click.echo(json.dumps({
                    "url": info.url,
                    "platform": info.platform,
                    "post_id": info.post_id,
                    "author": info.author,
                    "width": info.width,
                    "height": info.height,
                    "bitrate": info.bitrate,
                    "duration_ms": info.duration_ms,
                    "filename": info.suggested_filename(),
                }, indent=2))
            else:
                click.echo(f"\n✓ Video URL extracted")
                click.echo(f"  URL: {info.url}")
                click.echo(f"  Platform: {info.platform}")
                if info.author:
                    click.echo(f"  Author: @{info.author}")
                if info.width and info.height:
                    click.echo(f"  Quality: {info.width}x{info.height}")
        else:
            output_dir = os.path.expanduser(output)
            click.echo(f"\nScraping video from: {url}\n")

            result = scrape_video(
                url=url,
                output_dir=output_dir,
                browser=browser,
                filename=name,
                show_progress=not json_out,
            )

            if json_out:
                click.echo(json.dumps({
                    "filepath": result.filepath,
                    "filesize_mb": round(result.filesize_mb, 2),
                    "platform": result.video_info.platform,
                    "post_id": result.video_info.post_id,
                    "author": result.video_info.author,
                    "width": result.video_info.width,
                    "height": result.video_info.height,
                }, indent=2))
            else:
                click.echo(f"\n✓ Downloaded! {result.filesize_mb:.1f} MB → {result.filepath}")

    except ScraperError as e:
        if json_out:
            click.echo(json.dumps({"error": str(e)}), err=True)
        else:
            click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if json_out:
            click.echo(json.dumps({"error": f"Unexpected: {e}"}), err=True)
        else:
            click.echo(f"\n✗ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
