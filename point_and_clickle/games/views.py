import base64
from datetime import datetime

import requests
from dal import autocomplete
from django import http
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views import View

from django.views.generic import TemplateView

from point_and_clickle.games.models import Game, DailyGame


class RootView(TemplateView):
    template_name = 'pages/random.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        daily = DailyGame.get_daily_game(create=True)

        context['game'] = daily.game
        context['result'] = base64.b64encode(daily.game.title.encode('utf-8')).decode('utf-8')
        context['playable'] = True
        return context


class RandomView(TemplateView):
    template_name = "pages/random.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = Game.objects.filter(is_valid=True, is_pointandclick=True).order_by('?').first()
        context['game'] = game
        context['result'] = base64.b64encode(game.title.encode('utf-8')).decode('utf-8')
        context['playable'] = False
        return context


class DateView(TemplateView):
    template_name = "pages/random.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        date = datetime(year=context['year'], month=context['month'], day=context['day'])
        daily = get_object_or_404(DailyGame, date=date)
        context['game'] = daily.game
        context['result'] = base64.b64encode(daily.game.title.encode('utf-8')).decode('utf-8')
        context['playable'] = now.year == context['year'] and now.month == context['month'] and now.day == context['day']
        return context


class ImageFileView(View):
    def get(self, request, year, month, day):
        date = datetime(year=year, month=month, day=day)
        daily = get_object_or_404(DailyGame, date=date)
        url = daily.game.screenshots[5]
        response = requests.get(url)
        return http.HttpResponse(response, content_type='image/png')


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
