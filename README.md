# Bandcamp MCP

MCP server for Bandcamp music discovery and research. Deploy on Render (free tier) and use with Claude.

## Tools

| Tool | Description |
|------|-------------|
| `bandcamp_search` | Search for albums, artists, tracks, labels |
| `bandcamp_get_album` | Get album details with tracklist, tags, credits, pricing |
| `bandcamp_get_artist` | Get artist info, bio, discography, links |
| `bandcamp_get_track` | Get track details with lyrics |
| `bandcamp_browse_tag` | Browse music by genre/tag |
| `bandcamp_discover` | Discover new music by genre, format, popularity |

## Deploy to Render

1. Fork this repo
2. Go to [Render Dashboard](https://dashboard.render.com/select-repo?type=blueprint)
3. Select your forked repo
4. Click **Apply** - uses `render.yaml` automatically

No environment variables needed.

## Configure Claude

Add to `~/.mcp.json`:

```json
{
  "mcpServers": {
    "bandcamp": {
      "url": "https://your-app.onrender.com/sse"
    }
  }
}
```

Restart Claude Code to activate.

## Example Usage

```
"Search for Aphex Twin on Bandcamp"
"Find new ambient albums"
"Get info about this album: https://artist.bandcamp.com/album/..."
"Discover top electronic vinyl releases"
```

## Popular Tags

`ambient`, `electronic`, `synthwave`, `vaporwave`, `lofi`, `techno`, `house`, `shoegaze`, `post-punk`, `indie-rock`, `dark-ambient`, `drone`, `noise`, `chiptune`, `lo-fi-hip-hop`

## Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.server_remote
```

Server runs on `http://localhost:8000`

## License

MIT
