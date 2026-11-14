from django.conf import settings


def museum(request):
    """Expose the Point and Click Museum URL to every template."""
    return {"MUSEUM_URL": settings.MUSEUM_URL}
