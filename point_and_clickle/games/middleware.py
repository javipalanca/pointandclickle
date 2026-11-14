from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """301 from any other host name (e.g. www.) to the host of SITE_URL, keeping path and query.

    Only active when CANONICAL_HOST_REDIRECT is True (production), so local and test hosts are left alone.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        target = urlsplit(settings.SITE_URL)
        self.scheme, self.host = target.scheme, target.netloc

    def __call__(self, request):
        if getattr(settings, "CANONICAL_HOST_REDIRECT", False):
            host = request.get_host().split(":")[0]
            if host != self.host and host.endswith("." + self.host):
                return HttpResponsePermanentRedirect(
                    f"{self.scheme}://{self.host}{request.get_full_path()}"
                )
        return self.get_response(request)
