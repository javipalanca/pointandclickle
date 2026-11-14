import json

import pytest

from point_and_clickle.games import museum

pytestmark = pytest.mark.django_db

TIMELINE = {
    "timeline": {
        "games": [
            {
                "id": "monkey-island",
                "title": "The Secret of Monkey Island",
                "year": 1990,
            },
            {"id": "sam-max", "title": "Sam & Max Hit the Road", "year": 1993},
            {"id": "kings-quest", "title": "King's Quest", "year": 1984},
        ]
    }
}
ARCADE = {
    "arcade": {
        "games": [
            {
                "id": "monkey-island",
                "title": "The Secret of Monkey Island",
                "year": 1990,
                "status": "playable",
            },
            {
                "id": "bass",
                "title": "Beneath a Steel Sky",
                "year": 1994,
                "status": "playable",
                "timeline": "beneath-a-steel-sky",
            },
            {"id": "soon", "title": "Loom", "year": 1990, "status": "record"},
        ]
    }
}


class FakeResponse:
    def __init__(self, data):
        self.text = (
            '<html><script id="pcm-data" type="application/json">'
            + json.dumps(data)
            + "</script></html>"
        )

    def raise_for_status(self):
        pass


@pytest.fixture
def museum_site(monkeypatch, settings):
    from django.core.cache import cache

    cache.clear()
    settings.MUSEUM_URL = "https://museum.example/"
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return FakeResponse(TIMELINE if "timeline" in url else ARCADE)

    monkeypatch.setattr(museum.requests, "get", fake_get)
    return calls


def test_normalise():
    assert museum.normalise("The Secret of Monkey Island") == "secret of monkey island"
    assert museum.normalise("Sam & Max Hit the Road") == museum.normalise(
        "Sam and Max: Hit the Road".replace(":", "")
    )
    assert museum.normalise("Café Noir") == "cafe noir"


def test_links_exact_edition_and_none(museum_site):
    links = museum.links_for("The Secret of Monkey Island")
    assert [link["kind"] for link in links] == ["timeline", "arcade"]
    assert (
        links[0]["url"]
        == "https://museum.example/en/timeline/?utm_source=pointandclickle&utm_medium=result_game#monkey-island"
    )
    assert links[1]["url"].endswith(
        "/en/arcade/?utm_source=pointandclickle&utm_medium=result_game#play=monkey-island"
    )
    assert [
        link["kind"]
        for link in museum.links_for("The Secret of Monkey Island: Special Edition")
    ] == ["timeline", "arcade"]
    assert [link["kind"] for link in museum.links_for("Sam and Max Hit the Road")] == [
        "timeline"
    ]
    bass = museum.links_for("Beneath a Steel Sky")
    assert [link["kind"] for link in bass] == ["timeline", "arcade"] and bass[0][
        "url"
    ].endswith("#beneath-a-steel-sky")
    assert museum.links_for("Loom") == []  # in the catalogue but not playable
    assert (
        museum.links_for("Half-Life") == []
    )  # a hyphen inside a word is not an edition suffix
    assert len(museum_site) == 2  # the index is cached


def test_museum_down_gives_no_links(monkeypatch, settings):
    import requests
    from django.core.cache import cache

    cache.clear()

    def boom(url, **kwargs):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(museum.requests, "get", boom)
    assert museum.links_for("The Secret of Monkey Island") == []


def test_api_museum_and_stats_played(client, museum_site):
    from point_and_clickle.games.models import Game

    blank = {
        f: ""
        for f in (
            "description",
            "cover",
            "developer",
            "platform",
            "perspective",
            "control",
            "gameplay",
            "genre",
            "theme",
            "graphic_style",
            "presentation",
            "action",
            "red_flags",
            "media",
        )
    }
    game = Game.objects.create(
        title="The Secret of Monkey Island",
        url="https://adventuregamers.com/",
        screenshots=["x"] * 6,
        is_valid=True,
        is_pointandclick=True,
        hits_at_2=3,
        hits_failed=1,
        **blank,
    )
    r = client.get(f"/api/v1/game/{game.id}/museum/")
    assert [link["kind"] for link in r.json()["links"]] == ["timeline", "arcade"]
    st = client.get(f"/api/v1/game/{game.id}/stats/").json()
    assert st["played"] == 4 and st["2"] == "75" and st["0"] == "25"
