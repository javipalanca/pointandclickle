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

    def __str__(self):
        return self.title
