from django.urls import path

from point_and_clickle.games.views import RandomView, TitleAutocomplete, RootView

app_name = "games"
urlpatterns = [
    path("", view=RootView.as_view(), name="home"),
    path("random/", view=RandomView.as_view(), name="random"),
    path('game-autocomplete/', TitleAutocomplete.as_view(), name='game-autocomplete'),
]
