"""Video file downloader with progress and retry."""

from __future__ import annotations

import os
import time

import httpx

from social_video_scraper.extractors.base import DownloadFailed


def download_video(
    url: str,
    output_path: str,
    headers: dict[str, str] | None = None,
    max_retries: int = 3,
    show_progress: bool = True,
) -> str:
    """
    Download a video file to disk.

    Args:
        url: Direct MP4 download URL
        output_path: Where to save the file
        headers: Additional headers needed for the download
        max_retries: Number of retry attempts
        show_progress: Whether to print progress to stdout

    Returns:
        The output file path

    Raises:
        DownloadFailed: If download fails after all retries
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    default_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ),
    }
    if headers:
        default_headers.update(headers)

    last_error = None
    for attempt in range(max_retries):
        try:
            return _do_download(url, output_path, default_headers, show_progress)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                if show_progress:
                    print(f"  Retry {attempt + 1}/{max_retries} in {wait}s... ({e})")
                time.sleep(wait)

    # Clean up partial file on failure
    if os.path.exists(output_path):
        os.unlink(output_path)

    raise DownloadFailed(f"Download failed after {max_retries} attempts. Last error: {last_error}")


def _do_download(
    url: str, output_path: str, headers: dict[str, str], show_progress: bool
) -> str:
    """Perform the actual download with streaming."""
    with httpx.stream("GET", url, headers=headers, follow_redirects=True, timeout=120) as resp:
        resp.raise_for_status()

        total = int(resp.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in resp.iter_bytes(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)

                if show_progress and total > 0:
                    pct = downloaded / total * 100
                    mb = downloaded / (1024 * 1024)
                    total_mb = total / (1024 * 1024)
                    print(
                        f"\r  Downloading: {mb:.1f}/{total_mb:.1f} MB ({pct:.0f}%)",
                        end="",
                        flush=True,
                    )

        if show_progress:
            print()  # newline after progress

    # Verify file was written
    file_size = os.path.getsize(output_path)
    if file_size < 1000:
        raise DownloadFailed(f"Downloaded file is suspiciously small ({file_size} bytes).")

    return output_path
