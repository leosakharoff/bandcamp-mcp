"""
Remote MCP Server for Bandcamp (HTTP/SSE transport)
For deployment to Render, Railway, Fly.io, etc.
"""
import os
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn

from .bandcamp_client import BandcampClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("bandcamp-mcp")

# Global client instance
bandcamp_client: BandcampClient = None


def init_bandcamp_client():
    """Initialize Bandcamp client."""
    global bandcamp_client
    bandcamp_client = BandcampClient()
    logger.info("Bandcamp client initialized successfully")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for Bandcamp research."""
    return [
        Tool(
            name="bandcamp_search",
            description="Search Bandcamp for albums, artists, tracks, or labels. Returns titles, URLs, and basic info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (artist name, album title, etc.)",
                    },
                    "item_type": {
                        "type": "string",
                        "enum": ["all", "album", "artist", "track", "label"],
                        "description": "Type of result to filter by",
                        "default": "all",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 1,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="bandcamp_get_album",
            description="Get detailed album information including tracklist, tags, credits, and pricing from a Bandcamp album URL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full Bandcamp album URL (e.g., https://artist.bandcamp.com/album/album-name)",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="bandcamp_get_artist",
            description="Get artist/label information including bio, location, discography, and external links from a Bandcamp artist page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Bandcamp artist/label URL (e.g., https://artist.bandcamp.com)",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="bandcamp_get_track",
            description="Get detailed track information including lyrics (if available), tags, and album association.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full Bandcamp track URL (e.g., https://artist.bandcamp.com/track/track-name)",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="bandcamp_browse_tag",
            description="Browse albums by tag/genre on Bandcamp. Great for discovering music in specific genres.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Tag/genre to browse (e.g., 'ambient', 'electronic', 'jazz', 'punk')",
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["pop", "new", "rec"],
                        "description": "Sort order: pop (popular), new (newest), rec (recommended)",
                        "default": "pop",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number",
                        "default": 1,
                    },
                },
                "required": ["tag"],
            },
        ),
        Tool(
            name="bandcamp_discover",
            description="Discover new music on Bandcamp's discovery page. Filter by genre, format, and sort order.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "Main genre (e.g., 'electronic', 'rock', 'hip-hop-rap', 'ambient')",
                    },
                    "subgenre": {
                        "type": "string",
                        "description": "Subgenre for more specific filtering",
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["top", "new", "rec"],
                        "description": "Sort: top (best-selling), new (newest), rec (recommended)",
                        "default": "top",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["all", "vinyl", "cd", "cassette"],
                        "description": "Physical format filter",
                        "default": "all",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    try:
        if name == "bandcamp_search":
            results = await bandcamp_client.search(
                query=arguments["query"],
                item_type=arguments.get("item_type", "all"),
                page=arguments.get("page", 1),
            )

            items = results.get("results", [])
            pagination = results.get("pagination", {})

            if not items:
                return [TextContent(type="text", text="No results found.")]

            lines = [f"Found {len(items)} results (page {pagination.get('page', 1)}):\n"]

            for item in items:
                item_type = item.get("type", "unknown").title()
                title = item.get("title", "Unknown")
                url = item.get("url", "")

                lines.append(f"[{item_type}] {title}")
                if item.get("subhead"):
                    lines.append(f"  by {item['subhead']}")
                if item.get("genre"):
                    lines.append(f"  Genre: {item['genre']}")
                if item.get("released"):
                    lines.append(f"  Released: {item['released']}")
                if item.get("tags"):
                    lines.append(f"  Tags: {', '.join(item['tags'][:5])}")
                lines.append(f"  URL: {url}")
                lines.append("")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "bandcamp_get_album":
            album = await bandcamp_client.get_album(url=arguments["url"])

            lines = []
            lines.append(f"Album: {album.get('title', 'Unknown')}")
            lines.append(f"Artist: {album.get('artist', 'Unknown')}")

            if album.get("label"):
                lines.append(f"Label: {album['label']}")
            if album.get("release_date"):
                lines.append(f"Released: {album['release_date']}")

            if album.get("price"):
                price_str = f"{album['currency']} {album['price']}" if album.get("currency") else album["price"]
                lines.append(f"Price: {price_str}")

            if album.get("tags"):
                lines.append(f"Tags: {', '.join(album['tags'])}")

            if album.get("tracks"):
                lines.append(f"\nTracklist ({len(album['tracks'])} tracks):")
                for track in album["tracks"]:
                    pos = track.get("position", "")
                    title = track.get("title", "")
                    duration = track.get("duration", "")
                    if duration:
                        # Convert ISO duration to readable format
                        duration = duration.replace("P", "").replace("T", "").replace("M", ":").replace("S", "")
                    dur_str = f" ({duration})" if duration else ""
                    lines.append(f"  {pos}. {title}{dur_str}")

            if album.get("about"):
                about = album["about"][:500]
                lines.append(f"\nAbout:\n{about}{'...' if len(album.get('about', '')) > 500 else ''}")

            if album.get("credits"):
                credits = album["credits"][:300]
                lines.append(f"\nCredits:\n{credits}{'...' if len(album.get('credits', '')) > 300 else ''}")

            lines.append(f"\nURL: {album.get('url', '')}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "bandcamp_get_artist":
            artist = await bandcamp_client.get_artist(url=arguments["url"])

            lines = []
            lines.append(f"Artist: {artist.get('name', 'Unknown')}")

            if artist.get("location"):
                lines.append(f"Location: {artist['location']}")

            if artist.get("bio"):
                bio = artist["bio"][:800]
                lines.append(f"\nBio:\n{bio}{'...' if len(artist.get('bio', '')) > 800 else ''}")

            if artist.get("discography"):
                lines.append(f"\nDiscography ({len(artist['discography'])} releases):")
                for release in artist["discography"][:20]:
                    title = release.get("title", "Unknown")
                    url = release.get("url", "")
                    lines.append(f"  - {title}")
                    lines.append(f"    {url}")

            if artist.get("links"):
                lines.append("\nExternal Links:")
                for link in artist["links"]:
                    lines.append(f"  - {link.get('name', '')}: {link.get('url', '')}")

            lines.append(f"\nURL: {artist.get('url', '')}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "bandcamp_get_track":
            track = await bandcamp_client.get_track(url=arguments["url"])

            lines = []
            lines.append(f"Track: {track.get('title', 'Unknown')}")
            lines.append(f"Artist: {track.get('artist', 'Unknown')}")

            if track.get("album"):
                lines.append(f"Album: {track['album']}")
            if track.get("duration"):
                lines.append(f"Duration: {track['duration']}")
            if track.get("release_date"):
                lines.append(f"Released: {track['release_date']}")

            if track.get("price"):
                price_str = f"{track['currency']} {track['price']}" if track.get("currency") else track["price"]
                lines.append(f"Price: {price_str}")

            if track.get("tags"):
                lines.append(f"Tags: {', '.join(track['tags'])}")

            if track.get("lyrics"):
                lyrics = track["lyrics"][:1000]
                lines.append(f"\nLyrics:\n{lyrics}{'...' if len(track.get('lyrics', '')) > 1000 else ''}")

            if track.get("description"):
                desc = track["description"][:500]
                lines.append(f"\nDescription:\n{desc}")

            lines.append(f"\nURL: {track.get('url', '')}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "bandcamp_browse_tag":
            results = await bandcamp_client.get_tag_page(
                tag=arguments["tag"],
                sort=arguments.get("sort", "pop"),
                page=arguments.get("page", 1),
            )

            albums = results.get("albums", [])

            if not albums:
                return [TextContent(type="text", text=f"No albums found for tag '{arguments['tag']}'.")]

            lines = [f"Tag: {results['tag']} (sort: {results['sort']}, page {results['page']})\n"]
            lines.append(f"Found {len(albums)} albums:\n")

            for album in albums:
                lines.append(f"{album.get('title', 'Unknown')}")
                if album.get("artist"):
                    lines.append(f"  by {album['artist']}")
                lines.append(f"  URL: {album.get('url', '')}")
                lines.append("")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "bandcamp_discover":
            results = await bandcamp_client.discover(
                genre=arguments.get("genre", ""),
                subgenre=arguments.get("subgenre", ""),
                sort=arguments.get("sort", "top"),
                format=arguments.get("format", "all"),
            )

            albums = results.get("albums", [])

            if not albums:
                return [TextContent(type="text", text="No albums found in discovery.")]

            genre_str = results.get("genre") or "all genres"
            lines = [f"Discover: {genre_str} (sort: {results['sort']})\n"]
            lines.append(f"Found {len(albums)} albums:\n")

            for album in albums:
                lines.append(f"{album.get('title', 'Unknown')}")
                if album.get("artist"):
                    lines.append(f"  by {album['artist']}")
                if album.get("genre"):
                    lines.append(f"  Genre: {album['genre']}")
                lines.append(f"  URL: {album.get('url', '')}")
                lines.append("")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# SSE transport for MCP
sse = SseServerTransport("/messages/")


async def handle_sse(request):
    """Handle SSE connection for MCP."""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await app.run(
            streams[0], streams[1], app.create_initialization_options()
        )


async def handle_messages(request):
    """Handle POST messages for MCP."""
    await sse.handle_post_message(request.scope, request.receive, request._send)


async def health(request):
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "service": "bandcamp-mcp"})


# Starlette app with routes
starlette_app = Starlette(
    debug=False,
    routes=[
        Route("/health", health),
        Route("/sse", handle_sse),
        Route("/messages/", handle_messages, methods=["POST"]),
    ],
)


def main():
    """Run the HTTP server."""
    init_bandcamp_client()

    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Bandcamp MCP server on port {port}")

    uvicorn.run(starlette_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
