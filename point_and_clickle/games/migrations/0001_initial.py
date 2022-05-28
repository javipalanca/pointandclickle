# Generated by Django 3.2.13 on 2022-05-27 20:02

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('description', models.TextField()),
                ('cover', models.CharField(max_length=512)),
                ('developer', models.CharField(max_length=255)),
                ('platform', models.CharField(max_length=255)),
                ('perspective', models.CharField(max_length=255)),
                ('control', models.CharField(max_length=255)),
                ('gameplay', models.CharField(max_length=255)),
                ('genre', models.CharField(max_length=255)),
                ('theme', models.CharField(max_length=255)),
                ('graphic_style', models.CharField(max_length=255)),
                ('presentation', models.CharField(max_length=255)),
                ('action', models.CharField(max_length=255)),
                ('red_flags', models.CharField(max_length=255)),
                ('media', models.CharField(max_length=255)),
                ('screenshots', models.JSONField()),
                ('shown', models.BooleanField(default=False)),
                ('date_shown', models.DateField(blank=True, null=True)),
                ('hits_at_1', models.IntegerField(default=0)),
                ('hits_at_2', models.IntegerField(default=0)),
                ('hits_at_3', models.IntegerField(default=0)),
                ('hits_at_4', models.IntegerField(default=0)),
                ('hits_at_5', models.IntegerField(default=0)),
                ('hits_at_6', models.IntegerField(default=0)),
                ('hits_failed', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]