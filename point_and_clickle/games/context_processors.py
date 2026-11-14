from django.conf import settings


def museum(request):
    """Site-wide values every template needs: the museum link, the canonical origin and analytics."""
    return {
        "MUSEUM_URL": settings.MUSEUM_URL,
        "SITE_URL": settings.SITE_URL.rstrip("/"),
        "GA_MEASUREMENT_ID": settings.GA_MEASUREMENT_ID,
    }
