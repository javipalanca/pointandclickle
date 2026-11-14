import json

import pytest

from point_and_clickle.games.models import DailyStat
from point_and_clickle.games.views import today

pytestmark = pytest.mark.django_db
UA = "Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15 Safari/605.1.15"


def post(client, events, ua=UA, raw=None):
    body = raw if raw is not None else json.dumps({"e": events})
    return client.post(
        "/api/stats/", body, content_type="text/plain", HTTP_USER_AGENT=ua
    )


def counts():
    return {
        (s.metric, s.label): s.count for s in DailyStat.objects.filter(date=today())
    }


def test_counts_valid_events_without_cookies_or_csrf(client):
    client.handler.enforce_csrf_checks = True
    r = post(
        client,
        [
            ["view", "daily"],
            ["view", "daily"],
            ["device", "mobile"],
            ["referrer", "reddit.com"],
            ["game_win", "daily"],
            ["daily_attempts", "3"],
        ],
    )
    assert r.status_code == 204
    assert not r.cookies
    post(client, [["view", "daily"]])
    assert counts() == {
        ("view", "daily"): 3,
        ("device", "mobile"): 1,
        ("referrer", "reddit.com"): 1,
        ("game_win", "daily"): 1,
        ("daily_attempts", "3"): 1,
    }


def test_ignores_unknown_metrics_labels_and_garbage(client):
    post(
        client,
        [
            ["view", "nope"],
            ["evil", "x"],
            ["referrer", "<script>"],
            ["share", "x", "extra"],
            "view",
        ],
    )
    post(client, None, raw="not json")
    post(client, None, raw=json.dumps({"e": [["view", "daily"]] * 50}))  # capped at 20
    assert counts() == {("view", "daily"): 20}


def test_ignores_bots_and_large_bodies(client):
    post(
        client,
        [["view", "daily"]],
        ua="Googlebot/2.1 (+http://www.google.com/bot.html)",
    )
    post(client, None, raw=json.dumps({"e": [["view", "daily"]], "pad": "x" * 5000}))
    assert counts() == {}


def test_only_post(client):
    assert client.get("/api/stats/").status_code == 405


def test_dashboard_is_staff_only(client, admin_client):
    post(client, [["view", "daily"], ["game_start", "daily"], ["referrer", "direct"]])
    assert client.get("/stats/").status_code == 302  # to the admin login
    r = admin_client.get("/stats/?days=7")
    assert r.status_code == 200
    assert r.context["totals"][0] == 1 and r.context["totals"][1] == 1
    assert ("direct", 1) in dict(r.context["breakdowns"])["Where visitors come from"]
