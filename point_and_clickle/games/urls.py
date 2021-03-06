from django.urls import path

from point_and_clickle.games.views import RandomView, TitleAutocomplete, RootView, DateView, ImageFileView

app_name = "games"
urlpatterns = [
    path("", view=RootView.as_view(), name="home"),
    path("random/", view=RandomView.as_view(), name="random"),
    path("<int:year>/<int:month>/<int:day>/", view=DateView.as_view(), name="date"),
    path('game-autocomplete/', TitleAutocomplete.as_view(), name='game-autocomplete'),
    path("image/<int:year>/<int:month>/<int:day>/card.png", view=ImageFileView.as_view(), name="image"),
]
