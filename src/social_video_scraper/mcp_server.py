"""MCP server for social-video-scraper.

Exposes video scraping as tools that can be used from Claude Code
or any MCP-compatible client.

Usage:
    python -m social_video_scraper.mcp_server

Configure in Claude Code settings:
    {
        "mcpServers": {
            "social-video-scraper": {
                "command": "python",
                "args": ["-m", "social_video_scraper.mcp_server"]
            }
        }
    }
"""

from __future__ import annotations

import json
import os
import sys


def serve():
    """Run the MCP server."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    except ImportError:
        print(
            "MCP dependencies not installed. Install with:\n"
            "  pip install 'social-video-scraper[mcp]'",
            file=sys.stderr,
        )
        sys.exit(1)

    from social_video_scraper.core import scrape_video, extract_video_info
    from social_video_scraper.extractors.base import ScraperError

    server = Server("social-video-scraper")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="scrape_video",
                description=(
                    "Download a video from Twitter/X, Instagram, TikTok, or Facebook. "
                    "Provide the post URL and it will extract and download the highest-quality MP4."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the social media post containing the video",
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Directory to save the video (default: ~/Downloads)",
                            "default": "~/Downloads",
                        },
                        "filename": {
                            "type": "string",
                            "description": "Custom filename without extension (optional)",
                        },
                    },
                    "required": ["url"],
                },
            ),
            Tool(
                name="extract_video_url",
                description=(
                    "Extract the direct MP4 download URL from a social media post "
                    "without downloading. Returns the URL and video metadata."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the social media post containing the video",
                        },
                    },
                    "required": ["url"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "scrape_video":
                output_dir = os.path.expanduser(arguments.get("output_dir", "~/Downloads"))
                result = scrape_video(
                    url=arguments["url"],
                    output_dir=output_dir,
                    filename=arguments.get("filename"),
                    show_progress=False,
                )
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "success",
                            "filepath": result.filepath,
                            "filesize_mb": round(result.filesize_mb, 2),
                            "platform": result.video_info.platform,
                            "post_id": result.video_info.post_id,
                            "author": result.video_info.author,
                            "width": result.video_info.width,
                            "height": result.video_info.height,
                            "bitrate": result.video_info.bitrate,
                        }, indent=2),
                    )
                ]

            elif name == "extract_video_url":
                info = extract_video_info(arguments["url"])
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "success",
                            "video_url": info.url,
                            "platform": info.platform,
                            "post_id": info.post_id,
                            "author": info.author,
                            "width": info.width,
                            "height": info.height,
                            "bitrate": info.bitrate,
                            "duration_ms": info.duration_ms,
                            "suggested_filename": info.suggested_filename(),
                        }, indent=2),
                    )
                ]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except ScraperError as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "error": str(e)}, indent=2),
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "error": f"Unexpected: {e}"}, indent=2),
                )
            ]

    import asyncio
    asyncio.run(_run_server(server))


async def _run_server(server):
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    serve()
