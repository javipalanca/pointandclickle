# Generated by Django 3.2.13 on 2022-05-27 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='is_pointandclick',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
    ]
