import base64
from datetime import datetime, timedelta

from dal import autocomplete
from django import http
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404

from django.views.generic import TemplateView

from point_and_clickle.games.models import Game, DailyGame


class RootView(TemplateView):
    template_name = 'pages/random.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            daily = DailyGame.objects.get(date=datetime.utcnow().date())
        except DailyGame.DoesNotExist:

            yesterday = datetime.utcnow().date() - timedelta(days=1)
            daily = DailyGame.objects.get(date=yesterday)
            success = daily.game.hits_at_1 + daily.game.hits_at_2 + daily.game.hits_at_3 + daily.game.hits_at_4 + daily.game.hits_at_5 + daily.game.hits_at_6
            fails = daily.game.hits_failed

            if fails > success:
                game = Game.objects.filter(shown=False, is_valid=True, is_pointandclick=True, featured=True).order_by('?').first()
            else:
                game = Game.objects.filter(shown=False, is_valid=True, is_pointandclick=True).order_by('?').first()
            if game is None:
                game = Game.objects.filter(is_valid=True, is_pointandclick=True).order_by('?').first()
            try:
                daily = DailyGame.objects.create(date=datetime.utcnow().date(), game=game)
                daily.save()
                game.shown = True
                game.date_shown = datetime.utcnow().date()
                game.save()
            except IntegrityError:
                daily = DailyGame.objects.get(date=datetime.utcnow().date())

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


class DateView(TemplateView):
    template_name = "pages/random.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = datetime(year=context['year'], month=context['month'], day=context['day'])
        daily = get_object_or_404(DailyGame, date=date)
        context['game'] = daily.game
        context['result'] = base64.b64encode(daily.game.title.encode('utf-8')).decode('utf-8')
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
