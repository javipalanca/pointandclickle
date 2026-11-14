from datetime import datetime, timedelta

from django.db import IntegrityError, models
from django.http import Http404
from model_utils.models import TimeStampedModel


class Game(TimeStampedModel):
    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField()
    cover = models.CharField(max_length=512)
    developer = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    perspective = models.CharField(max_length=255)
    control = models.CharField(max_length=255)
    gameplay = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    theme = models.CharField(max_length=255)
    graphic_style = models.CharField(max_length=255)
    presentation = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    red_flags = models.CharField(max_length=255)
    media = models.CharField(max_length=255)

    steam_id = models.CharField(max_length=20, blank=True, null=True)
    steam_num_reviews = models.IntegerField(default=0)
    steam_positive_reviews = models.IntegerField(default=0)
    steam_negative_reviews = models.IntegerField(default=0)
    steam_total_reviews = models.FloatField(default=0)
    steam_review_score = models.FloatField(default=0)

    screenshots = models.JSONField()

    is_valid = models.BooleanField(default=True)
    is_pointandclick = models.BooleanField(default=False)

    shown = models.BooleanField(default=False)
    date_shown = models.DateField(null=True, blank=True)

    hits_at_1 = models.IntegerField(default=0)
    hits_at_2 = models.IntegerField(default=0)
    hits_at_3 = models.IntegerField(default=0)
    hits_at_4 = models.IntegerField(default=0)
    hits_at_5 = models.IntegerField(default=0)
    hits_at_6 = models.IntegerField(default=0)
    hits_failed = models.IntegerField(default=0)

    featured = models.BooleanField(default=False)
    year = models.IntegerField(blank=True, null=True)

    total_played = property(
        lambda self: self.hits_at_1
        + self.hits_at_2
        + self.hits_at_3
        + self.hits_at_4
        + self.hits_at_5
        + self.hits_at_6
        + self.hits_failed
    )
    total_hits = property(
        lambda self: self.hits_at_1
        + self.hits_at_2
        + self.hits_at_3
        + self.hits_at_4
        + self.hits_at_5
        + self.hits_at_6
    )
    total_hits_failed = property(lambda self: self.hits_failed)

    def add_hit(self, guess):
        if guess == "1":
            self.hits_at_1 += 1
        elif guess == "2":
            self.hits_at_2 += 1
        elif guess == "3":
            self.hits_at_3 += 1
        elif guess == "4":
            self.hits_at_4 += 1
        elif guess == "5":
            self.hits_at_5 += 1
        elif guess == "6":
            self.hits_at_6 += 1
        elif guess == "0":
            self.hits_failed += 1
        self.save()

    def stats(self):
        total = (
            self.hits_at_1
            + self.hits_at_2
            + self.hits_at_3
            + self.hits_at_4
            + self.hits_at_5
            + self.hits_at_6
            + self.hits_failed
        )
        return {
            "1": f"{round(self.hits_at_1 * 100 / total if total > 0 else 0, 0):.0f}",
            "2": f"{round(self.hits_at_2 * 100 / total if total > 0 else 0, 0):.0f}",
            "3": f"{round(self.hits_at_3 * 100 / total if total > 0 else 0, 0):.0f}",
            "4": f"{round(self.hits_at_4 * 100 / total if total > 0 else 0, 0):.0f}",
            "5": f"{round(self.hits_at_5 * 100 / total if total > 0 else 0, 0):.0f}",
            "6": f"{round(self.hits_at_6 * 100 / total if total > 0 else 0, 0):.0f}",
            "0": f"{round(self.hits_failed * 100 / total if total > 0 else 0, 0):.0f}",
        }

    def __str__(self):
        return self.title


class DailyGame(TimeStampedModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateField(unique=True)

    total_played = property(lambda self: self.game.total_played)
    total_hits = property(lambda self: self.game.total_hits)
    total_hits_failed = property(lambda self: self.game.total_hits_failed)

    @classmethod
    def get_daily_game(cls, date=None, create=False):
        date = date if date else datetime.utcnow().date()

        daily = DailyGame.objects.filter(date=date)
        if len(daily) > 0:
            return daily[0]

        if create:
            yesterday = date - timedelta(days=1)
            daily = DailyGame.objects.filter(date=yesterday)
            if len(daily) > 0:
                daily = daily[0]
                success = (
                    daily.game.hits_at_1
                    + daily.game.hits_at_2
                    + daily.game.hits_at_3
                    + daily.game.hits_at_4
                    + daily.game.hits_at_5
                    + daily.game.hits_at_6
                )
                fails = daily.game.hits_failed
                if fails > success:
                    game = (
                        Game.objects.filter(
                            shown=False,
                            is_valid=True,
                            is_pointandclick=True,
                            featured=True,
                        )
                        .order_by("?")
                        .first()
                    )
                else:
                    game = (
                        Game.objects.filter(
                            shown=False, is_valid=True, is_pointandclick=True
                        )
                        .order_by("?")
                        .first()
                    )
            else:
                game = None
            if game is None:
                game = (
                    Game.objects.filter(is_valid=True, is_pointandclick=True)
                    .order_by("?")
                    .first()
                )
            try:
                daily = DailyGame.objects.create(
                    date=datetime.utcnow().date(), game=game
                )
                daily.save()
                game.shown = True
                game.date_shown = datetime.utcnow().date()
                game.save()
            except IntegrityError:
                daily = DailyGame.objects.get(date=datetime.utcnow().date())
            return daily
        else:
            raise Http404()

    def __str__(self):
        return self.game.title + " " + str(self.date)


class DailyStat(models.Model):
    """Anonymous daily counters (own statistics, see games/stats.py): one row per day, metric and label.
    No visitor identifiers, IPs or cookies are stored, only how many times something happened.
    """

    date = models.DateField(db_index=True)
    metric = models.CharField(max_length=32)
    label = models.CharField(max_length=64, blank=True, default="")
    count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date", "metric", "label"], name="unique_daily_stat"
            )
        ]
        ordering = ["-date", "metric", "-count"]

    def __str__(self):
        return f"{self.date} {self.metric}:{self.label} = {self.count}"
