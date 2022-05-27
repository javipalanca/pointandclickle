import json

import tqdm as tqdm
from django.core.management.base import BaseCommand, CommandError
from point_and_clickle.games.models import Game


class Command(BaseCommand):
    help = "Import games from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        file_path = options['file']
        try:
            with open(file_path) as f:
                gamesdb = json.load(f)
        except FileNotFoundError:
            raise CommandError('File not found')

        for game in tqdm.tqdm(gamesdb.values()):
            if not Game.objects.filter(title=game['title']).exists():
                game_register = Game.objects.create(title=game['title'],
                                                    description=game['description'],
                                                    url=game['url'],
                                                    cover=game['cover'],
                                                    developer=game['developer'],
                                                    platform=game['Platform'],
                                                    perspective=game['Perspective'],
                                                    control=game['Control'],
                                                    gameplay=game['Gameplay'],
                                                    genre=game['Genre'],
                                                    theme=game['Theme'],
                                                    graphic_style=game['Graphic Style'],
                                                    presentation=game['Presentation'],
                                                    action=game['Action (Compulsory)'],
                                                    red_flags=game['Red Flags'],
                                                    media=game['Media'],
                                                    screenshots=game['screenshots'])
                game_register.save()

        self.stdout.write(self.style.SUCCESS('Games imported'))
