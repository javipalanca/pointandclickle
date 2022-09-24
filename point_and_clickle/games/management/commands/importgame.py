from django.core.management.base import BaseCommand

from scrap_games import scrap_game
from .importdb import insert_game_in_db


class Command(BaseCommand):
    help = "Import games from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        url = options['url']

        game = scrap_game(url)
        insert_game_in_db(game)

        self.stdout.write(self.style.SUCCESS(f'Game {game["title"]} imported'))
