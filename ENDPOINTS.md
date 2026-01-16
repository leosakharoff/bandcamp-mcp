# Bandcamp MCP - Endpoints Reference

**Server URL:** `https://bandcamp-mcp.onrender.com/sse`

---

## Endpoints

### bandcamp_search
Søg på Bandcamp.

| Argument | Type | Required | Default | Beskrivelse |
|----------|------|----------|---------|-------------|
| `query` | string | ✅ | - | Søgeord (kunstner, album, etc.) |
| `item_type` | string | ❌ | "all" | `all`, `album`, `artist`, `track`, `label` |
| `page` | integer | ❌ | 1 | Sidetal |

```json
{
  "query": "Aphex Twin",
  "item_type": "artist",
  "page": 1
}
```

**Returnerer:** title, url, type, subhead (artist), tags, released, genre.

**Brug til:** Find kunstnere/albums, få URLs til videre research.

---

### bandcamp_get_album
Fuld album info fra URL.

| Argument | Type | Required | Default | Beskrivelse |
|----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | Bandcamp album URL |

```json
{
  "url": "https://aphextwin.bandcamp.com/album/selected-ambient-works"
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

| Argument | Type | Required | Default | Beskrivelse |
|----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | Bandcamp artist URL |

```json
{
  "url": "https://aphextwin.bandcamp.com"
}
```

**Returnerer:**
- name, location, bio
- discography[] med title, url, image
- links[] (sociale medier, website)

**Brug til:** Se hele diskografi, find lokation (geografisk kontekst).

---

### bandcamp_get_track
Enkelt track info.

| Argument | Type | Required | Default | Beskrivelse |
|----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | Bandcamp track URL |

```json
{
  "url": "https://artist.bandcamp.com/track/track-name"
}
```

**Returnerer:**
- title, artist, duration
- album, album_url
- lyrics (hvis tilgængelig!)
- tags[], price, currency

**Brug til:** Lyrics research, find hvilket album track er fra.

---

### bandcamp_browse_tag
Browse musik efter tag/genre.

| Argument | Type | Required | Default | Beskrivelse |
|----------|------|----------|---------|-------------|
| `tag` | string | ✅ | - | Tag/genre at browse |
| `sort` | string | ❌ | "pop" | `pop` (populære), `new` (nyeste), `rec` (anbefalede) |
| `page` | integer | ❌ | 1 | Sidetal |

```json
{
  "tag": "dark-ambient",
  "sort": "new",
  "page": 1
}
```

**Brug til:** DISCOVERY! Find nye kunstnere i specifikke nicher.

**Populære tags:**
```
ambient, electronic, synthwave, vaporwave, lofi,
techno, house, drone, noise, shoegaze, post-punk,
darkwave, coldwave, krautrock, kosmische,
experimental, avant-garde, musique-concrete,
dark-ambient, field-recordings, fourth-world,
lo-fi-hip-hop, chiptune, minimal, dub-techno
```

---

### bandcamp_discover
Bandcamp's discovery side.

| Argument | Type | Required | Default | Beskrivelse |
|----------|------|----------|---------|-------------|
| `genre` | string | ❌ | - | Hovedgenre (electronic, rock, ambient, jazz) |
| `subgenre` | string | ❌ | - | Mere specifik genre |
| `sort` | string | ❌ | "top" | `top` (bestsellers), `new` (nyeste), `rec` (anbefalede) |
| `format` | string | ❌ | "all" | `all`, `vinyl`, `cd`, `cassette` |

```json
{
  "genre": "electronic",
  "subgenre": "ambient",
  "sort": "new",
  "format": "vinyl"
}
```

**Brug til:** Bred discovery, filter på fysisk format (vinyl collectors!).

---

## Tag Mapping fra Discogs

| Discogs Style | Bandcamp Tags |
|--------------|---------------|
| Ambient | `ambient`, `dark-ambient`, `drone` |
| Krautrock | `krautrock`, `motorik`, `kosmische` |
| Post-Punk | `post-punk`, `coldwave`, `darkwave` |
| Synth-pop | `synthpop`, `synthwave` |
| Industrial | `industrial`, `power-electronics`, `noise` |
| Minimal | `minimal`, `minimal-wave` |
| Experimental | `experimental`, `avant-garde` |
| IDM | `idm`, `glitch`, `braindance` |
| Dub | `dub`, `dub-techno` |
| New Age | `new-age`, `fourth-world`, `healing` |

---

## Prioriteret Workflow

```
1. Brug Discogs styles → map til Bandcamp tags
2. bandcamp_browse_tag(tag, sort="pop") → Klassikere i genren
3. bandcamp_browse_tag(tag, sort="new") → Nyeste i genren
4. bandcamp_get_album(url) → Dyb research på interessante fund
5. bandcamp_get_artist(url) → Se diskografi, find mere
```

---

## Tips

- **Tags** er mere granulære end Discogs styles
- **Location** på artist page = geografisk scene-kontekst
- **About/credits** indeholder ofte kunstnerens inspirationer
- **"Supported by"** = peer validation fra andre kunstnere
- Kombiner flere tags med bindestreg: `lo-fi`, `post-rock`, `dark-ambient`
