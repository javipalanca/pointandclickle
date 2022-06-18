import tqdm as tqdm
from django.core.management.base import BaseCommand
from point_and_clickle.games.models import Game


class Command(BaseCommand):
    help = "Filter games based on number of screenshots and genre"

    def handle(self, *args, **options):
        for game in tqdm.tqdm(Game.objects.all()):
            if len(game.screenshots) < 6:
                game.is_valid = False
            if "Point-and-click" in game.control or "Click-and-drag" in game.control or "Text parser" in game.control:
                game.is_pointandclick = True

            game.save()

        self.stdout.write(self.style.SUCCESS('Games filtered'))
        self.stdout.write(self.style.SUCCESS(f'Games invalid: {Game.objects.filter(is_valid=False).count()}'))
        self.stdout.write(self.style.SUCCESS(f'Games point and click: {Game.objects.filter(is_pointandclick=True).count()}'))
