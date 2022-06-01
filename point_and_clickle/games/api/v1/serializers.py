from rest_framework import serializers

from point_and_clickle.games.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        exclude = ('screenshots', 'is_valid', 'is_pointandclick', 'shown', 'date_shown', 'created', 'modified',
                   'hits_at_1', 'hits_at_2', 'hits_at_3', 'hits_at_4', 'hits_at_5', 'hits_at_6', 'hits_failed')

