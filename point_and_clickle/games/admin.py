from django.contrib import admin

from point_and_clickle.games.models import Game, DailyGame


class GameAdmin(admin.ModelAdmin):
    search_fields = ['title']
    ordering = ('title',)
    list_filter = ('is_pointandclick', 'is_valid')
    list_display = ('title', 'control', 'is_pointandclick', 'is_valid')

admin.site.register(Game, GameAdmin)

class DailyGameAdmin(admin.ModelAdmin):
    pass

admin.site.register(DailyGame, DailyGameAdmin)
