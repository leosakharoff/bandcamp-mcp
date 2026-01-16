# Bandcamp MCP

MCP server til Bandcamp musik-research og discovery.

## Tools

### bandcamp_search
Søg efter musik på Bandcamp.
- `query` (required): Søgeord (kunstner, album, etc.)
- `item_type`: "all", "album", "artist", "track", "label"
- `page`: Sidetal for pagination

### bandcamp_get_album
Hent album-detaljer fra URL.
- `url` (required): Bandcamp album URL (f.eks. https://artist.bandcamp.com/album/name)

Returnerer: titel, kunstner, tracklist, tags, pris, credits, about.

### bandcamp_get_artist
Hent kunstner/label info fra URL.
- `url` (required): Bandcamp artist URL (f.eks. https://artist.bandcamp.com)

Returnerer: navn, lokation, bio, discography, eksterne links.

### bandcamp_get_track
Hent track-detaljer fra URL.
- `url` (required): Bandcamp track URL

Returnerer: titel, kunstner, album, duration, lyrics, tags.

### bandcamp_browse_tag
Browse musik efter genre/tag.
- `tag` (required): Genre-tag (f.eks. "ambient", "synthwave", "post-punk")
- `sort`: "pop" (populær), "new" (nyeste), "rec" (anbefalet)
- `page`: Sidetal

Populære tags: electronic, ambient, synthwave, vaporwave, lofi, techno, house, shoegaze, post-punk, indie-rock, death-metal, black-metal, dark-ambient, drone, noise, chiptune.

### bandcamp_discover
Opdag ny musik via Bandcamps discovery.
- `genre`: Hovedgenre (electronic, rock, ambient, jazz, etc.)
- `subgenre`: Mere specifik genre
- `sort`: "top" (bestsellers), "new" (nyeste), "rec" (anbefalet)
- `format`: "all", "vinyl", "cd", "cassette"

## Eksempler

```
# Søg efter kunstner
bandcamp_search(query="Aphex Twin", item_type="artist")

# Hent album info
bandcamp_get_album(url="https://aphextwin.bandcamp.com/album/selected-ambient-works-85-92")

# Find nye ambient releases
bandcamp_browse_tag(tag="ambient", sort="new")

# Discover electronic vinyl
bandcamp_discover(genre="electronic", format="vinyl", sort="top")
```
