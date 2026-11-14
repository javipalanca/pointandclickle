from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from point_and_clickle.games.models import DailyGame
from point_and_clickle.games.views import today


class StaticViewSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return ["games:home", "games:archive", "games:about"]

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        return {"games:home": "daily", "games:archive": "daily"}.get(item, "monthly")

    def priority(self, item):
        return {"games:home": 1.0, "games:archive": 0.8}.get(item, 0.6)

    def lastmod(self, item):
        if item in ("games:home", "games:archive"):
            return today()
        return None


class PastGamesSitemap(Sitemap):
    """Every past daily game, playable as practice at /YYYY/M/D/."""

    protocol = "https"
    changefreq = "yearly"
    priority = 0.5
    limit = 5000

    def items(self):
        return DailyGame.objects.filter(date__lt=today()).order_by("-date")

    def location(self, item):
        d = item.date
        return reverse(
            "games:date", kwargs={"year": d.year, "month": d.month, "day": d.day}
        )

    def lastmod(self, item):
        return item.date


SITEMAPS = {
    "static": StaticViewSitemap,
    "days": PastGamesSitemap,
}
