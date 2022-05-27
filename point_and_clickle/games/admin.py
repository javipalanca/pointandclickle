from django.contrib import admin

from point_and_clickle.games.models import Game


class GameAdmin(admin.ModelAdmin):
    pass

admin.site.register(Game, GameAdmin)
