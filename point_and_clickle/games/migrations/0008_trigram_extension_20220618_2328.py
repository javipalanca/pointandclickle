from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_auto_20220618_1903'),
    ]

    operations = [
        TrigramExtension(),
    ]
