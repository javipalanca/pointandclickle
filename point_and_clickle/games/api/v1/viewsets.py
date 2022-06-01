from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from point_and_clickle.games.api.v1.serializers import GameSerializer
from point_and_clickle.games.models import Game


class GameViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = GameSerializer
    queryset = Game.objects.all()
    lookup_field = "id"


    @action(detail=True, methods=['post'])
    def hit(self, request, id):
        game = Game.objects.get(id=id)
        guess = request.data.get('hit')
        if guess == "1":
            game.hits_at_1 += 1
        elif guess == "2":
            game.hits_at_2 += 1
        elif guess == "3":
            game.hits_at_3 += 1
        elif guess == "4":
            game.hits_at_4 += 1
        elif guess == "5":
            game.hits_at_5 += 1
        elif guess == "6":
            game.hits_at_6 += 1
        elif guess == "0":
            game.hits_failed += 1
        game.save()
        return Response(status=status.HTTP_200_OK)
