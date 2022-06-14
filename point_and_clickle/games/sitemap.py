from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return ['games:home']

    def location(self, item):
        return reverse(item)


SITEMAPS = {
    'static': StaticViewSitemap,
}