from dal import autocomplete

from django.views.generic import TemplateView

from point_and_clickle.games.forms import TitleForm
from point_and_clickle.games.models import Game


class RandomView(TemplateView):
    template_name = "pages/random.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = Game.objects.filter(is_valid=True, is_pointandclick=True).order_by('?').first()
        context["form"] = TitleForm()
        return context


class TitleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Game.objects.filter(is_pointandclick=True)

        if self.q:
            qs = qs.filter(title__istartswith=self.q)

        return qs
