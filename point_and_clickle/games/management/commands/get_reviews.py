import requests
import tqdm as tqdm
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from point_and_clickle.games.models import Game


def get_steam_app_id(game_name):
    response = requests.get(url=f'https://store.steampowered.com/search/?term={game_name}&category1=998',
                            headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        app_id = soup.find(class_='search_result_row')['data-ds-appid']
    except TypeError:
        raise ValueError(f'Could not find app_id for {game_name}')


    return app_id


def get_reviews(app_id):
    return requests.get(url=f'https://store.steampowered.com/appreviews/{app_id}?json=1').json()



class Command(BaseCommand):
    help = "Get reviews from Steam"

    def handle(self, *args, **options):
        for game in tqdm.tqdm(Game.objects.all()):
            try:
                app_id = get_steam_app_id(game.title)
                reviews = get_reviews(app_id)
                game.steam_num_reviews = reviews['query_summary']['num_reviews']
                game.steam_positive_reviews = reviews['query_summary']['total_positive']
                game.steam_negative_reviews = reviews['query_summary']['total_negative']
                game.steam_total_reviews = reviews['query_summary']['total_reviews']
                game.steam_review_score = reviews['query_summary']['review_score']
                game.save()
            except ValueError as e:
                print(e)