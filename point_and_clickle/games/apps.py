from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GamesConfig(AppConfig):
    name = "point_and_clickle.games"
    verbose_name = _("Games")
