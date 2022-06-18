from django.contrib import admin

from point_and_clickle.games.models import Game, DailyGame


class GameAdmin(admin.ModelAdmin):
    search_fields = ['title', 'year']
    ordering = ('year', 'title',)
    list_filter = ('is_pointandclick', 'is_valid', 'featured')
    list_display = (
        'title', 'control', 'year', 'is_pointandclick', 'is_valid')


admin.site.register(Game, GameAdmin)


class DailyGameAdmin(admin.ModelAdmin):
    pass


admin.site.register(DailyGame, DailyGameAdmin)
