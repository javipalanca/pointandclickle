import json
from datetime import timedelta

import pytest
from django.urls import reverse

from point_and_clickle.games.models import DailyGame, Game
from point_and_clickle.games.views import today

pytestmark = pytest.mark.django_db

SHOTS = [
    f"https://adventuregamers.com/images/screenshots/{i}__medium.jpg" for i in range(6)
]


def make_game(title):
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
    return Game.objects.create(
        title=title,
        url="https://adventuregamers.com/",
        screenshots=SHOTS,
        is_valid=True,
        is_pointandclick=True,
        **blank,
    )


@pytest.fixture
def days():
    """Three daily games: two days ago (#1), yesterday (#2) and today (#3)."""
    d = today()
    return {
        "before": DailyGame.objects.create(
            date=d - timedelta(days=2), game=make_game("Loom")
        ),
        "yesterday": DailyGame.objects.create(
            date=d - timedelta(days=1), game=make_game("Zak McKracken")
        ),
        "today": DailyGame.objects.create(date=d, game=make_game("The Dig")),
    }


def config(response):
    return response.context["game_config"]


def test_home_is_the_daily_game(client, days):
    r = client.get("/")
    assert r.status_code == 200
    assert config(r) == {
        "mode": "daily",
        "number": 3,
        "date": today().isoformat(),
        "autocompleteUrl": "/game-autocomplete/",
        "kind": "daily",
    }
    html = r.content.decode()
    assert '<link rel="canonical" href="https://pointandclickle.com/">' in html
    assert "index, follow" in html
    assert '"@type": "WebApplication"' in html
    assert 'id="searchbox"' in html


def test_canonical_ignores_query_strings(client, days):
    html = client.get("/?a1b2c3").content.decode()
    assert '<link rel="canonical" href="https://pointandclickle.com/">' in html


def test_random_redirects_to_a_stable_url_and_skips_todays_game(client, days):
    for _ in range(10):
        r = client.get(reverse("games:random"))
        assert r.status_code == 302
        assert r["Location"] != reverse(
            "games:random-game", kwargs={"game_id": days["today"].game_id}
        )
        assert "no-cache" in r["Cache-Control"] or "max-age=0" in r["Cache-Control"]


def test_random_game_is_playable_practice_and_noindex(client, days):
    game = days["before"].game
    r = client.get(reverse("games:random-game", kwargs={"game_id": game.id}))
    assert r.status_code == 200
    assert config(r)["mode"] == "practice" and config(r)["kind"] == "random"
    html = r.content.decode()
    assert 'id="searchbox"' in html  # the bug: practice games had no title box
    assert "noindex, follow" in html
    assert "Practice game" in html


def test_past_day_is_practice_with_number_and_neighbours(client, days):
    d = days["yesterday"].date
    r = client.get(
        reverse("games:date", kwargs={"year": d.year, "month": d.month, "day": d.day})
    )
    assert r.status_code == 200
    assert config(r) == {
        "mode": "practice",
        "number": 2,
        "date": d.isoformat(),
        "autocompleteUrl": "/game-autocomplete/",
        "kind": "archive",
    }
    assert r.context["previous_day"] == days["before"].date
    assert r.context["next_day"] is None  # today is not an archive day
    html = r.content.decode()
    assert "Point &amp; Clickle #2" in html
    assert '"@type": "BreadcrumbList"' in html
    assert "index, follow" in html


def test_today_by_date_redirects_home_and_future_is_404(client, days):
    d = today()
    assert (
        client.get(
            reverse(
                "games:date", kwargs={"year": d.year, "month": d.month, "day": d.day}
            )
        )["Location"]
        == "/"
    )
    f = d + timedelta(days=1)
    assert (
        client.get(
            reverse(
                "games:date", kwargs={"year": f.year, "month": f.month, "day": f.day}
            )
        ).status_code
        == 404
    )
    assert client.get("/2026/2/30/").status_code == 404


def test_archive_lists_past_days_without_answers(client, days):
    r = client.get(reverse("games:archive"))
    assert r.status_code == 200
    assert r.context["total"] == 2
    html = r.content.decode()
    assert "#1" in html and "#2" in html and "#3" not in html
    assert "Loom" not in html and "Zak McKracken" not in html


def test_about_has_faq_structured_data(client):
    r = client.get(reverse("games:about"))
    assert r.status_code == 200
    data = (
        r.content.decode()
        .split('<script type="application/ld+json">')[1]
        .split("</script>")[0]
    )
    graph = json.loads(data)["@graph"]
    faq = next(n for n in graph if n["@type"] == "FAQPage")
    assert len(faq["mainEntity"]) == 6


def test_sitemap_has_static_pages_and_past_days(client, days):
    xml = client.get("/sitemap.xml").content.decode()
    assert "/archive/</loc>" in xml and "/how-to-play/</loc>" in xml
    y = days["yesterday"].date
    assert f"/{y.year}/{y.month}/{y.day}/</loc>" in xml
    t = today()
    assert f"/{t.year}/{t.month}/{t.day}/</loc>" not in xml


def test_hits_only_count_for_todays_game(client, days):
    old = days["yesterday"].game
    client.post(f"/api/v1/game/{old.id}/hit/", {"hit": "2"})
    old.refresh_from_db()
    assert old.total_played == 0
    new = days["today"].game
    client.post(f"/api/v1/game/{new.id}/hit/", {"hit": "2"})
    new.refresh_from_db()
    assert new.hits_at_2 == 1


def test_www_redirects_to_the_canonical_host(client, settings, days):
    settings.CANONICAL_HOST_REDIRECT = True
    settings.ALLOWED_HOSTS = [".pointandclickle.com"]
    r = client.get("/archive/?x=1", HTTP_HOST="www.pointandclickle.com")
    assert r.status_code == 301
    assert r["Location"] == "https://pointandclickle.com/archive/?x=1"
    assert client.get("/archive/", HTTP_HOST="pointandclickle.com").status_code == 200
