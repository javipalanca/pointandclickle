from datetime import date

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from point_and_clickle.games.api.v1.serializers import GameSerializer
from point_and_clickle.games.models import Game, DailyGame


class GameViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = GameSerializer
    queryset = Game.objects.all()
    lookup_field = "id"


    @action(detail=True, methods=['post'])
    def hit(self, request, id):
        game = Game.objects.get(id=id)
        guess = request.data.get('hit')
        todays_game = DailyGame.objects.get(date=date.today())
        if todays_game.game.id == game.id:
            game.add_hit(guess)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def stats(self, request, id):
        game = Game.objects.get(id=id)
        return JsonResponse(game.stats())