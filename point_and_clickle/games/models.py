from model_utils.models import TimeStampedModel
from django.db import models


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
        total = self.hits_at_1 + self.hits_at_2 + self.hits_at_3 + self.hits_at_4 + self.hits_at_5 + self.hits_at_6 + self.hits_failed
        return {
            '1': "{:.0f}".format(round(self.hits_at_1 * 100 / total if total > 0 else 0, 0)),
            '2': "{:.0f}".format(round(self.hits_at_2 * 100 / total if total > 0 else 0, 0)),
            '3': "{:.0f}".format(round(self.hits_at_3 * 100 / total if total > 0 else 0, 0)),
            '4': "{:.0f}".format(round(self.hits_at_4 * 100 / total if total > 0 else 0, 0)),
            '5': "{:.0f}".format(round(self.hits_at_5 * 100 / total if total > 0 else 0, 0)),
            '6': "{:.0f}".format(round(self.hits_at_6 * 100 / total if total > 0 else 0, 0)),
            '0': "{:.0f}".format(round(self.hits_failed * 100 / total if total > 0 else 0, 0)),
        }

    def __str__(self):
        return self.title


class DailyGame(TimeStampedModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateField(unique=True)

    def __str__(self):
        return self.game.title + ' ' + str(self.date)
