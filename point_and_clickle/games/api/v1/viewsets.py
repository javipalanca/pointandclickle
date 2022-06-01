from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from point_and_clickle.games.api.v1.serializers import GameSerializer
from point_and_clickle.games.models import Game


class GameViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = GameSerializer
    queryset = Game.objects.all()
    lookup_field = "id"

