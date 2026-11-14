import base64
from collections import OrderedDict
from datetime import date as date_cls
from datetime import datetime, timezone

import requests
from dal import autocomplete
from django import http
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from point_and_clickle.games.models import DailyGame, Game


def today():
    """The daily game changes at 00:00 UTC (see DailyGame.get_daily_game)."""
    return datetime.now(timezone.utc).date()


def puzzle_number(day: date_cls) -> int:
    """Point & Clickle #1 is the first daily game; numbers grow by one each day."""
    return DailyGame.objects.filter(date__lte=day).count()


def encode_title(game: Game) -> str:
    return base64.b64encode(game.title.encode("utf-8")).decode("utf-8")


class GameView(TemplateView):
    """One game page. mode "daily" is today's game: it counts in the player's stats and in the game's
    guess distribution. mode "practice" (random games and past days) keeps its own guesses and touches
    neither the daily game nor the stats."""

    template_name = "pages/game.html"
    mode = "daily"

    def game_context(self, game: Game, mode: str, day: date_cls = None) -> dict:
        number = puzzle_number(day) if day else None
        return {
            "game": game,
            "result": encode_title(game),
            "mode": mode,
            "playable": True,
            "day": day,
            "number": number,
            # read by static/js/project.js (init_wordle)
            "game_config": {
                "mode": mode,
                "number": number,
                "date": day.isoformat() if day else None,
                "kind": (
                    "daily" if mode == "daily" else ("archive" if day else "random")
                ),
            },
        }


class RootView(GameView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        daily = DailyGame.get_daily_game(create=True)
        context.update(self.game_context(daily.game, "daily", daily.date))
        return context


@never_cache
def random_game(request):
    """/random/ picks a game and sends the player to its own URL, so a reload keeps the same game."""
    games = Game.objects.filter(is_valid=True, is_pointandclick=True)
    todays = DailyGame.objects.filter(date=today()).values_list("game_id", flat=True)
    game = games.exclude(id__in=list(todays)).order_by("?").first() or games.first()
    if game is None:
        raise http.Http404("No games yet")
    return redirect("games:random-game", game_id=game.id)


class RandomGameView(GameView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = get_object_or_404(
            Game, id=kwargs["game_id"], is_valid=True, is_pointandclick=True
        )
        context.update(self.game_context(game, "practice"))
        context["noindex"] = True
        return context


class DateView(GameView):
    """A past daily game, playable as practice. Today's goes to the home page; future days do not exist."""

    def get(self, request, *args, **kwargs):
        try:
            self.day = date_cls(kwargs["year"], kwargs["month"], kwargs["day"])
        except ValueError:
            raise http.Http404("No such day")
        if self.day == today():
            return redirect("games:home")
        if self.day > today():
            raise http.Http404("Not played yet")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        daily = get_object_or_404(DailyGame, date=self.day)
        context.update(self.game_context(daily.game, "practice", daily.date))
        previous = DailyGame.objects.filter(date__lt=self.day).order_by("-date").first()
        following = (
            DailyGame.objects.filter(date__gt=self.day, date__lt=today())
            .order_by("date")
            .first()
        )
        context["previous_day"] = previous.date if previous else None
        context["next_day"] = following.date if following else None
        return context


class ArchiveView(TemplateView):
    """Every past daily game, by month, without the answers."""

    template_name = "pages/archive.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = list(
            DailyGame.objects.filter(date__lt=today())
            .order_by("date")
            .values_list("date", flat=True)
        )
        months = OrderedDict()
        for n, day in enumerate(days, start=1):
            months.setdefault(day.replace(day=1), []).append((n, day))
        context["months"] = [
            (m, entries[::-1]) for m, entries in reversed(months.items())
        ]
        context["total"] = len(days)
        return context


class AboutView(TemplateView):
    template_name = "pages/about.html"


class ImageFileView(View):
    def get(self, request, year, month, day):
        date = datetime(year=year, month=month, day=day)
        daily = get_object_or_404(DailyGame, date=date)
        url = daily.game.screenshots[5]
        response = requests.get(url)
        return http.HttpResponse(response, content_type="image/png")


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
        return [self.get_result_label(result) for result in context["object_list"]]

    def render_to_response(self, context):
        return http.JsonResponse(self.get_results(context), safe=False)
