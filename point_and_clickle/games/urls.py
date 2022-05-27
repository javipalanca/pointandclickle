from django.urls import path

from point_and_clickle.games.views import RandomView

app_name = "games"
urlpatterns = [
    path("random/", view=RandomView.as_view(), name="random"),

]
