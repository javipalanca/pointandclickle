from rest_framework.mixins import GenericViewSet, RetrieveModelMixin

from point_and_clickle.games.api.v1.serializers import GameSerializer
from point_and_clickle.games.models import Game


class GameViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = GameSerializer
    queryset = Game.objects.all()
    lookup_field = "title"

