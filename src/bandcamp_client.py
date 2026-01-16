"""
Bandcamp Client for MCP Server
Uses web scraping since Bandcamp doesn't have a public API
"""
import re
import json
import logging
from typing import Optional
from urllib.parse import quote_plus, urljoin
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BANDCAMP_BASE = "https://bandcamp.com"


class BandcampClient:
    """Client for Bandcamp data extraction."""

    def __init__(self, user_agent: str = "BandcampMCP/1.0"):
        self.user_agent = user_agent
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def _fetch(self, url: str) -> str:
        """Fetch a URL and return the HTML content."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True,
            )
            response.raise_for_status()
            return response.text

    async def search(
        self,
        query: str,
        item_type: str = "all",  # all, album, artist, track, label, fan
        page: int = 1,
    ) -> dict:
        """Search Bandcamp for albums, artists, tracks, etc."""
        type_map = {
            "all": "",
            "album": "a",
            "artist": "b",
            "track": "t",
            "label": "b",
            "fan": "f",
        }

        search_type = type_map.get(item_type, "")
        url = f"{BANDCAMP_BASE}/search?q={quote_plus(query)}&page={page}"
        if search_type:
            url += f"&item_type={search_type}"

        html = await self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        results = []
        result_items = soup.select(".searchresult")

        for item in result_items:
            result = {}

            # Get type
            result_type = item.select_one(".itemtype")
            result["type"] = result_type.get_text(strip=True).lower() if result_type else "unknown"

            # Get heading (title)
            heading = item.select_one(".heading a")
            if heading:
                result["title"] = heading.get_text(strip=True)
                result["url"] = heading.get("href", "")

            # Get subhead (artist for albums/tracks)
            subhead = item.select_one(".subhead")
            if subhead:
                result["subhead"] = subhead.get_text(strip=True)

            # Get image
            img = item.select_one(".art img")
            if img:
                result["image"] = img.get("src", "")

            # Get tags
            tags = item.select(".tag")
            result["tags"] = [t.get_text(strip=True) for t in tags]

            # Get release date
            released = item.select_one(".released")
            if released:
                result["released"] = released.get_text(strip=True).replace("released ", "")

            # Get genre
            genre = item.select_one(".genre")
            if genre:
                result["genre"] = genre.get_text(strip=True).replace("genre: ", "")

            if result.get("title"):
                results.append(result)

        # Get pagination info
        pagination = {"page": page, "items": len(results)}

        return {"results": results, "pagination": pagination}

    async def get_album(self, url: str) -> dict:
        """Get album details from a Bandcamp album URL."""
        html = await self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        album = {"url": url}

        # Try to get JSON-LD data first (most reliable)
        json_ld = soup.select_one('script[type="application/ld+json"]')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    album["title"] = data.get("name", "")
                    album["artist"] = data.get("byArtist", {}).get("name", "")
                    album["description"] = data.get("description", "")
                    album["release_date"] = data.get("datePublished", "")
                    album["image"] = data.get("image", "")
                    album["num_tracks"] = data.get("numTracks", 0)

                    # Get tracks
                    tracks = data.get("track", {}).get("itemListElement", [])
                    album["tracks"] = []
                    for t in tracks:
                        track_item = t.get("item", {})
                        album["tracks"].append({
                            "position": t.get("position", 0),
                            "title": track_item.get("name", ""),
                            "duration": track_item.get("duration", ""),
                            "url": track_item.get("@id", ""),
                        })

                    # Get price from offers
                    offers = data.get("offers", {})
                    if offers:
                        album["price"] = offers.get("price", "")
                        album["currency"] = offers.get("priceCurrency", "")

                    # Get publisher (label)
                    publisher = data.get("publisher", {})
                    if publisher:
                        album["label"] = publisher.get("name", "")
                        album["label_url"] = publisher.get("@id", "")

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")

        # Fallback to HTML parsing if JSON-LD didn't work
        if not album.get("title"):
            title_elem = soup.select_one("#name-section .trackTitle")
            if title_elem:
                album["title"] = title_elem.get_text(strip=True)

        if not album.get("artist"):
            artist_elem = soup.select_one("#name-section a")
            if artist_elem:
                album["artist"] = artist_elem.get_text(strip=True)

        # Get tags
        tags = soup.select(".tralbum-tags a.tag")
        album["tags"] = [t.get_text(strip=True) for t in tags]

        # Get about/credits if available
        about = soup.select_one(".tralbum-about")
        if about:
            album["about"] = about.get_text(strip=True)

        credits = soup.select_one(".tralbum-credits")
        if credits:
            album["credits"] = credits.get_text(strip=True)

        return album

    async def get_artist(self, url: str) -> dict:
        """Get artist/label info from a Bandcamp artist page."""
        html = await self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        artist = {"url": url}

        # Get name
        name_elem = soup.select_one("#band-name-location .title")
        if name_elem:
            artist["name"] = name_elem.get_text(strip=True)

        # Get location
        location_elem = soup.select_one("#band-name-location .location")
        if location_elem:
            artist["location"] = location_elem.get_text(strip=True)

        # Get bio
        bio_elem = soup.select_one(".bio-text")
        if bio_elem:
            artist["bio"] = bio_elem.get_text(strip=True)

        # Get discography
        albums = []
        music_grid = soup.select(".music-grid-item")
        for item in music_grid:
            album = {}
            link = item.select_one("a")
            if link:
                album["url"] = urljoin(url, link.get("href", ""))

            title = item.select_one(".title")
            if title:
                album["title"] = title.get_text(strip=True)

            img = item.select_one("img")
            if img:
                album["image"] = img.get("src", "") or img.get("data-original", "")

            if album.get("title"):
                albums.append(album)

        artist["discography"] = albums

        # Get links
        links = []
        links_section = soup.select("#band-links li a")
        for link in links_section:
            links.append({
                "name": link.get_text(strip=True),
                "url": link.get("href", ""),
            })
        artist["links"] = links

        return artist

    async def get_track(self, url: str) -> dict:
        """Get track details from a Bandcamp track URL."""
        html = await self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        track = {"url": url}

        # Try JSON-LD first
        json_ld = soup.select_one('script[type="application/ld+json"]')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    track["title"] = data.get("name", "")
                    track["artist"] = data.get("byArtist", {}).get("name", "")
                    track["duration"] = data.get("duration", "")
                    track["description"] = data.get("description", "")
                    track["release_date"] = data.get("datePublished", "")
                    track["image"] = data.get("image", "")

                    # Get album info if part of one
                    in_album = data.get("inAlbum", {})
                    if in_album:
                        track["album"] = in_album.get("name", "")
                        track["album_url"] = in_album.get("@id", "")

                    # Get price
                    offers = data.get("offers", {})
                    if offers:
                        track["price"] = offers.get("price", "")
                        track["currency"] = offers.get("priceCurrency", "")

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")

        # Get tags
        tags = soup.select(".tralbum-tags a.tag")
        track["tags"] = [t.get_text(strip=True) for t in tags]

        # Get lyrics if available
        lyrics = soup.select_one(".lyricsText")
        if lyrics:
            track["lyrics"] = lyrics.get_text(strip=True)

        return track

    async def get_tag_page(
        self,
        tag: str,
        sort: str = "pop",  # pop, new, rec
        page: int = 1,
    ) -> dict:
        """Get albums from a tag/genre page."""
        url = f"{BANDCAMP_BASE}/tag/{quote_plus(tag)}?sort_field={sort}&page={page}"
        html = await self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        albums = []
        items = soup.select(".item_list .item")

        for item in items:
            album = {}

            link = item.select_one("a")
            if link:
                album["url"] = link.get("href", "")

            title = item.select_one(".itemtext")
            if title:
                album["title"] = title.get_text(strip=True)

            artist = item.select_one(".itemsubtext")
            if artist:
                album["artist"] = artist.get_text(strip=True)

            img = item.select_one("img")
            if img:
                album["image"] = img.get("src", "") or img.get("data-original", "")

            if album.get("title"):
                albums.append(album)

        return {
            "tag": tag,
            "sort": sort,
            "page": page,
            "albums": albums,
        }

    async def discover(
        self,
        genre: str = "",
        subgenre: str = "",
        sort: str = "top",  # top, new, rec
        format: str = "all",  # all, vinyl, cd, cassette
        location: int = 0,  # 0 = anywhere
    ) -> dict:
        """Discover new music on Bandcamp."""
        url = f"{BANDCAMP_BASE}/discover"
        params = []
        if genre:
            params.append(f"g={quote_plus(genre)}")
        if subgenre:
            params.append(f"s={quote_plus(subgenre)}")
        if sort:
            params.append(f"sort={sort}")
        if format != "all":
            params.append(f"f={format}")
        if location:
            params.append(f"l={location}")

        if params:
            url += "?" + "&".join(params)

        html = await self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        albums = []
        items = soup.select(".discover-item")

        for item in items:
            album = {}

            link = item.select_one("a")
            if link:
                album["url"] = link.get("href", "")

            title = item.select_one(".heading")
            if title:
                album["title"] = title.get_text(strip=True)

            artist = item.select_one(".subhead")
            if artist:
                album["artist"] = artist.get_text(strip=True)

            img = item.select_one("img")
            if img:
                album["image"] = img.get("src", "") or img.get("data-original", "")

            genre_elem = item.select_one(".genre")
            if genre_elem:
                album["genre"] = genre_elem.get_text(strip=True)

            if album.get("title"):
                albums.append(album)

        return {
            "genre": genre,
            "subgenre": subgenre,
            "sort": sort,
            "albums": albums,
        }
