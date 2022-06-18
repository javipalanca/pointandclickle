import re
import bs4
import requests
from dateutil.parser import parse
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm
from django.contrib.postgres.search import TrigramSimilarity
from django.core.management.base import BaseCommand
from point_and_clickle.games.models import Game


class Command(BaseCommand):
    help = "Select featured games based on wikipedia data"

    def handle(self, *args, **options):
        BASE_URL = "https://en.wikipedia.org/wiki/List_of_graphic_adventure_games"
        page = requests.get(BASE_URL)
        soup = bs4.BeautifulSoup(page.text, "html.parser")

        table = soup.find("table", {"class": "wikitable"})

        # Obtain every title of columns with tag <th>
        headers = []
        for th in table.find_all("th"):
            headers.append(th.text.strip())

        # Create a for loop to fill the data in the table to a pandas dataframe
        data = []
        for tr in table.find_all("tr"):
            row = []
            for td in tr.find_all("td"):
                row.append(td.text.strip())
            data.append(row)
        df = pd.DataFrame(data, columns=headers)

        self.stdout.write(tabulate(df.head(2), headers="keys", tablefmt="psql"))

        # Obtain  games
        for index, row in tqdm(df.iterrows()):
            game_title = row["Game"]
            if game_title:
                # remove text that matches [<int>]
                game_title = re.sub(r"\[\d+\]", "", game_title)
                year = row["Date released"]
                if year != "TBA":
                    # parse date from string with any format to datetime
                    year = parse(year, fuzzy=True).year
                else:
                    year = None

                try:
                    game = Game.objects.get(title=game_title)
                    game.featured = True
                    game.year = year
                    game.save()
                except Game.DoesNotExist:
                    alternative = Game.objects.annotate(similarity=TrigramSimilarity('title', game_title))\
                        .filter(similarity__gt=0.5).order_by('-similarity')
                    if len(alternative) > 0:
                        game = alternative[0]
                        game.featured = True
                        game.year = year
                        game.save()
                    else:
                        pass
                        #self.stdout.write(str(game) + "NOT FOUND")

