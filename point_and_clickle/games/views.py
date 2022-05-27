from django.views.generic import TemplateView

from point_and_clickle.games.models import Game


class RandomView(TemplateView):

    template_name = "pages/random.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = Game.objects.filter(is_valid=True, is_pointandclick=True).order_by('?').first()
        return context

