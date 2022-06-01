from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from point_and_clickle.games.api.v1.viewsets import GameViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("v1/game", GameViewSet)

app_name = "api"
urlpatterns = router.urls
