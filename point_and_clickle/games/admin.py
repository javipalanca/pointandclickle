from django.contrib import admin

from point_and_clickle.games.models import DailyGame, DailyStat, Game


class GameAdmin(admin.ModelAdmin):
    search_fields = ["title", "year"]
    ordering = ("year", "title")
    list_filter = ("is_pointandclick", "is_valid", "featured")
    list_display = (
        "title",
        "control",
        "year",
        "total_played",
        "total_hits",
        "total_hits_failed",
        "is_pointandclick",
        "is_valid",
        "featured",
    )


admin.site.register(Game, GameAdmin)


class DailyGameAdmin(admin.ModelAdmin):
    list_display = ("game", "date", "total_played", "total_hits", "total_hits_failed")


admin.site.register(DailyGame, DailyGameAdmin)


@admin.register(DailyStat)
class DailyStatAdmin(admin.ModelAdmin):
    """Own statistics (anonymous daily counters). The summary is at /stats/."""

    list_display = ("date", "metric", "label", "count")
    list_filter = ("metric", "date")
    search_fields = ("label",)
    date_hierarchy = "date"
