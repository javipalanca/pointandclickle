from django.contrib import admin

from point_and_clickle.games.models import Game, DailyGame


class GameAdmin(admin.ModelAdmin):
    pass

admin.site.register(Game, GameAdmin)

class DailyGameAdmin(admin.ModelAdmin):
    pass

admin.site.register(DailyGame, DailyGameAdmin)
