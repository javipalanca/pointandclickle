"""Links from a game to its pages in the Point and Click Museum (museum.pointandclickle.com).

The museum is a static site: each page embeds its data as JSON in <script id="pcm-data">. The timeline page
lists the curated games (record at /<lang>/timeline/#<id>) and the DOSBox room the ones that can be played in
the browser (/<lang>/arcade/#play=<id>). We read both pages, index the games by a normalised title and keep
the index in the cache for 12 hours (10 minutes if the museum could not be reached), so a result never waits
on the museum more than once.
"""

import json
import logging
import re
import unicodedata

import requests
from django.conf import settings
from django.core.cache import cache

log = logging.getLogger(__name__)

CACHE_KEY = "museum_index_v1"
TTL, TTL_FAILED = 12 * 3600, 600
PAGES = {"timeline": "en/timeline/", "arcade": "en/arcade/"}
DATA = re.compile(r'<script id="pcm-data" type="application/json">(.*?)</script>', re.S)
# "Title: Special Edition", "Title (Remastered)", "Title - Episode 1" (not the hyphen inside a word)
EDITION = re.compile(r"\s*(?::|\(|\[|\s[–—-]\s).*$")


def normalise(title: str) -> str:
    """Lower case, no accents, no punctuation, "&" as "and", without a leading "The"."""
    t = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode()
    t = t.lower().replace("&", " and ")
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return re.sub(r"^the ", "", t)


def _page_data(path: str) -> dict:
    url = settings.MUSEUM_URL.rstrip("/") + "/" + path
    r = requests.get(url, timeout=6, headers={"User-Agent": "PointAndClickle/1.0"})
    r.raise_for_status()
    m = DATA.search(r.text)
    return json.loads(m.group(1)) if m else {}


def build_index() -> dict:
    """{normalised title: {"timeline": id, "arcade": id, "year": int}} from the museum's pages."""
    index: dict = {}
    timeline = _page_data(PAGES["timeline"]).get("timeline") or {}
    for g in timeline.get("games", []) if isinstance(timeline, dict) else []:
        if g.get("id") and g.get("title"):
            index.setdefault(normalise(g["title"]), {})
            index[normalise(g["title"])].update(timeline=g["id"], year=g.get("year"))
    arcade = _page_data(PAGES["arcade"]).get("arcade") or {}
    for g in arcade.get("games", []):
        if g.get("id") and g.get("title") and g.get("status", "playable") == "playable":
            entry = index.setdefault(normalise(g["title"]), {})
            entry["arcade"] = g["id"]
            entry.setdefault("year", g.get("year"))
            if g.get("timeline"):
                entry.setdefault("timeline", g["timeline"])
    return index


def index() -> dict:
    data = cache.get(CACHE_KEY)
    if data is None:
        try:
            data = build_index()
            cache.set(CACHE_KEY, data, TTL)
        except (requests.RequestException, ValueError) as e:
            log.warning("museum index not available: %s", e)
            data = {}
            cache.set(CACHE_KEY, data, TTL_FAILED)
    return data


def links_for(title: str, year: int = None) -> list:
    """Museum pages about this game: its record in the timeline and/or the DOSBox room, best match first.

    Exact title first; then the title without an edition suffix ("…: Special Edition"), which links remakes
    to the original's story.
    """
    idx = index()
    entry = idx.get(normalise(title))
    if entry is None:
        base = normalise(EDITION.sub("", title or ""))
        entry = idx.get(base) if base else None
    if not entry:
        return []
    root = settings.MUSEUM_URL.rstrip("/")
    utm = "utm_source=pointandclickle&utm_medium=result_game"
    links = []
    if entry.get("timeline"):
        links.append(
            {
                "kind": "timeline",
                "url": f"{root}/en/timeline/?{utm}#{entry['timeline']}",
                "label": "Read its story in the museum's timeline",
            }
        )
    if entry.get("arcade"):
        links.append(
            {
                "kind": "arcade",
                "url": f"{root}/en/arcade/?{utm}#play={entry['arcade']}",
                "label": "Play it in the museum's DOSBox room",
            }
        )
    return links
