import base64
from datetime import date

from dal import autocomplete
from django import http
from django.db import IntegrityError
from django.db.models import Q

from django.views.generic import TemplateView

from point_and_clickle.games.models import Game, DailyGame


class RootView(TemplateView):
    template_name = 'pages/random.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            daily = DailyGame.objects.get(date=date.today())
        except DailyGame.DoesNotExist:
            game = Game.objects.filter(shown=False, is_valid=True, is_pointandclick=True).order_by('?').first()
            try:
                daily = DailyGame.objects.create(date=date.today(), game=game)
                daily.save()
                game.shown = True
                game.date_shown = date.today()
                game.save()
            except IntegrityError:
                daily = DailyGame.objects.get(date=date.today())

        context['game'] = daily.game
        context['result'] = base64.b64encode(daily.game.title.encode('utf-8')).decode('utf-8')
        return context

class RandomView(TemplateView):
    template_name = "pages/random.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = Game.objects.filter(is_valid=True, is_pointandclick=True).order_by('?').first()
        context['game'] = game
        context['result'] = base64.b64encode(game.title.encode('utf-8')).decode('utf-8')
        return context


class TitleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Game.objects.all()

        if self.q:
            query = Q()
            for word in self.q.split(" "):
                query &= Q(title__icontains=word.strip())
            qs = qs.filter(query)

        return qs

    def get_results(self, context):
        return [self.get_result_label(result) for result in context['object_list']]

    def render_to_response(self, context):
        return http.JsonResponse(self.get_results(context), safe=False)
