# Bandcamp MCP - Endpoints Reference

**Server URL:** `https://bandcamp-mcp.onrender.com/sse`

## Endpoints

### bandcamp_search
Søg på Bandcamp.

```json
{
  "query": "Aphex Twin",
  "item_type": "all|album|artist|track|label",
  "page": 1
}
```

**Returnerer:** title, url, type, subhead (artist), tags, released, genre.

**Brug til:** Find kunstnere/albums, få URLs til videre research.

---

### bandcamp_get_album
Fuld album info fra URL.

```json
{
  "url": "https://artist.bandcamp.com/album/album-name"
}
```

**Returnerer:**
- title, artist, release_date
- tracks[] med position, title, duration
- tags[], about, credits
- price, currency
- label, label_url

**Brug til:** Dyb research. Læs "about" for kunstnerens egne ord!

---

### bandcamp_get_artist
Kunstner/label side.

```json
{
  "url": "https://artist.bandcamp.com"
}
```

**Returnerer:**
- name, location, bio
- discography[] med title, url
- links[] (sociale medier, website)

**Brug til:** Se hele diskografi, find lokation (geografisk kontekst).

---

### bandcamp_get_track
Enkelt track info.

```json
{
  "url": "https://artist.bandcamp.com/track/track-name"
}
```

**Returnerer:**
- title, artist, duration
- album, album_url
- lyrics (hvis tilgængelig!)
- tags[], price

**Brug til:** Lyrics research, find hvilket album track er fra.

---

### bandcamp_browse_tag
Browse musik efter tag/genre.

```json
{
  "tag": "ambient",
  "sort": "pop|new|rec",
  "page": 1
}
```

**Sort options:**
- `pop` = Populære/klassikere
- `new` = Nyeste udgivelser
- `rec` = Bandcamp's anbefalinger

**Populære tags:**
```
ambient, electronic, synthwave, vaporwave, lofi,
techno, house, drone, noise, shoegaze, post-punk,
darkwave, coldwave, krautrock, kosmische,
experimental, avant-garde, musique-concrete,
dark-ambient, field-recordings, fourth-world
```

**Brug til:** DISCOVERY! Find nye kunstnere i specifikke nicher.

---

### bandcamp_discover
Bandcamp's discovery side.

```json
{
  "genre": "electronic",
  "subgenre": "ambient",
  "sort": "top|new|rec",
  "format": "all|vinyl|cd|cassette"
}
```

**Sort options:**
- `top` = Bestsellers
- `new` = Nyeste
- `rec` = Anbefalede

**Brug til:** Bred discovery, filter på fysisk format (vinyl collectors!).

---

## Tag Mapping fra Discogs

| Discogs Style | Bandcamp Tags |
|--------------|---------------|
| Ambient | ambient, dark-ambient, drone |
| Krautrock | krautrock, motorik, kosmische |
| Post-Punk | post-punk, coldwave, darkwave |
| Synth-pop | synthpop, synthwave |
| Industrial | industrial, power-electronics, noise |
| Minimal | minimal, minimal-wave |
| Experimental | experimental, avant-garde |
| IDM | idm, glitch, braindance |

---

## Prioriteret Workflow

1. Brug Discogs styles → map til Bandcamp tags
2. `bandcamp_browse_tag(sort="pop")` → Klassikere i genren
3. `bandcamp_browse_tag(sort="new")` → Nyeste i genren
4. `bandcamp_get_album` → Dyb research på interessante fund
5. `bandcamp_get_artist` → Se diskografi, find mere

---

## Tips

- Bandcamp tags er mere granulære end Discogs
- "Supported by" sektion på albums = peer validation
- Læs album descriptions - kunstnere forklarer ofte deres inspirationer
- Location på artist page = geografisk scene-kontekst
