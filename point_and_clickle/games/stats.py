"""Own statistics: anonymous daily counters, counted for every visitor without cookies or consent.

The browser (static/js/analytics.js) sends batches of [metric, label] pairs to POST /api/stats/ with
navigator.sendBeacon. Nothing that identifies a visitor is stored: no cookies, no IP addresses, no user agents,
only per-day counts. Bots and unknown metrics are ignored, labels are normalised and limited, and a request
carries at most 20 events, so the table stays small.
"""

import json
import re
from collections import Counter
from datetime import timedelta

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from point_and_clickle.games.models import DailyStat

MAX_EVENTS = 20
MAX_BODY = 4096
LABEL = re.compile(r"^[a-z0-9._-]{0,64}$")
BOTS = re.compile(
    r"bot|crawl|spider|slurp|preview|headless|lighthouse|pagespeed|monitor|curl|wget|python",
    re.I,
)
# metric → allowed labels (None: any label that matches LABEL, e.g. referrer domains)
METRICS = {
    "view": {"daily", "random", "archive-day", "archive", "about", "page"},
    "device": {"mobile", "tablet", "desktop"},
    "referrer": None,
    "game_start": {"daily", "random", "archive"},
    "game_win": {"daily", "random", "archive"},
    "game_loss": {"daily", "random", "archive"},
    "daily_attempts": {"1", "2", "3", "4", "5", "6", "x"},
    "share": {"x", "whatsapp", "telegram", "clipboard"},
    "museum_click": {"header", "banner", "result", "howto", "footer", "faq"},
    "random_game": {"daily", "random", "archive-day", "archive", "about", "page"},
    "archive_day": {""},
    "donate_click": {""},
}


def today():
    from point_and_clickle.games.views import today as utc_today

    return utc_today()


def clean(events):
    """Valid (metric, label) pairs of a request, at most MAX_EVENTS."""
    out = []
    for item in events[:MAX_EVENTS] if isinstance(events, list) else []:
        if not (isinstance(item, list) and len(item) == 2):
            continue
        metric, label = str(item[0]), str(item[1]).lower()[:64]
        allowed = METRICS.get(metric, ())
        if allowed == () or not LABEL.match(label):
            continue
        if allowed is not None and label not in allowed:
            continue
        out.append((metric, label))
    return out


def add(day, counts: Counter):
    for (metric, label), n in counts.items():
        updated = DailyStat.objects.filter(date=day, metric=metric, label=label).update(
            count=F("count") + n
        )
        if not updated:
            try:
                with transaction.atomic():
                    DailyStat.objects.create(
                        date=day, metric=metric, label=label, count=n
                    )
            except IntegrityError:  # created by a concurrent request
                DailyStat.objects.filter(date=day, metric=metric, label=label).update(
                    count=F("count") + n
                )


@csrf_exempt
def collect(request):
    """POST /api/stats/ with {"e": [[metric, label], ...]}. Always answers 204: the page never waits on it."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if len(request.body) <= MAX_BODY and not BOTS.search(
        request.META.get("HTTP_USER_AGENT", "")
    ):
        try:
            events = json.loads(request.body.decode("utf-8")).get("e")
        except (ValueError, AttributeError):
            events = None
        pairs = clean(events)
        if pairs:
            add(today(), Counter(pairs))
    return HttpResponse(status=204)


def visitor_count() -> int:
    """For the retro counter: HIT_COUNTER_START plus every page view counted so far (cached for a minute)."""

    def count():
        views = DailyStat.objects.filter(metric="view").aggregate(n=Sum("count"))["n"]
        return settings.HIT_COUNTER_START + (views or 0)

    return cache.get_or_set("hit_counter", count, 60)


def summary(days=30):
    """Totals per day for the main metrics, plus breakdowns for the whole period."""
    start = today() - timedelta(days=days - 1)
    rows = DailyStat.objects.filter(date__gte=start)
    per_day = {}
    for date, metric, label, count in rows.values_list(
        "date", "metric", "label", "count"
    ):
        d = per_day.setdefault(date, Counter())
        d[metric] += count
        d[f"{metric}:{label}"] += count
    columns = [
        ("Views", "view"),
        ("Daily games", "game_start:daily"),
        ("Daily wins", "game_win:daily"),
        ("Random games", "game_start:random"),
        ("Archive games", "game_start:archive"),
        ("Shares", "share"),
        ("Museum clicks", "museum_click"),
    ]
    table = [
        (date, [per_day[date][key] for _, key in columns])
        for date in sorted(per_day, reverse=True)
    ]
    totals = [sum(r[1][i] for r in table) for i in range(len(columns))]

    def breakdown(metric, limit=15):
        return list(
            rows.filter(metric=metric)
            .values_list("label")
            .annotate(n=Sum("count"))
            .order_by("-n")[:limit]
        )

    return {
        "days": days,
        "columns": [c[0] for c in columns],
        "table": table,
        "totals": totals,
        "breakdowns": [
            ("Pages viewed", breakdown("view")),
            ("Where visitors come from", breakdown("referrer", 25)),
            ("Devices", breakdown("device")),
            ("Daily game: guesses needed", sorted(breakdown("daily_attempts"))),
            ("Shares", breakdown("share")),
            ("Museum links", breakdown("museum_click")),
        ],
    }


@staff_member_required
def dashboard(request):
    try:
        days = max(1, min(365, int(request.GET.get("days", 30))))
    except ValueError:
        days = 30
    return render(request, "pages/stats.html", summary(days))
