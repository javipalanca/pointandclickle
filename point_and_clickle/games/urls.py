from django.urls import path

from point_and_clickle.games import stats
from point_and_clickle.games.views import (
    AboutView,
    ArchiveView,
    DateView,
    ImageFileView,
    RandomGameView,
    RootView,
    TitleAutocomplete,
    random_game,
)

app_name = "games"
urlpatterns = [
    path("", view=RootView.as_view(), name="home"),
    path("random/", view=random_game, name="random"),
    path("random/<int:game_id>/", view=RandomGameView.as_view(), name="random-game"),
    path("archive/", view=ArchiveView.as_view(), name="archive"),
    path("stats/", view=stats.dashboard, name="stats"),
    path("api/stats/", view=stats.collect, name="stats-collect"),
    path("how-to-play/", view=AboutView.as_view(), name="about"),
    path("<int:year>/<int:month>/<int:day>/", view=DateView.as_view(), name="date"),
    path("game-autocomplete/", TitleAutocomplete.as_view(), name="game-autocomplete"),
    path(
        "image/<int:year>/<int:month>/<int:day>/card.png",
        view=ImageFileView.as_view(),
        name="image",
    ),
]
