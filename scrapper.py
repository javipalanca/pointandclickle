import bs4
import requests
import json

BASE_URL = "https://adventuregamers.com"
games = {}

links = ["/games/adventure/all"]

while len(links) > 0:
    link = links.pop()
    print("Scraping " + link)
    page = requests.get(BASE_URL + link)
    soup = bs4.BeautifulSoup(page.text, "html.parser")

    item_holders = soup.find_all("div", {"class": "item_holder"})
    for item_holder in item_holders:
        items = item_holder.find_all("div", {"class": "item"})
        for item in items:
            game_name = item.find("h2", {"class": "game_title"})
            game_name = game_name.text.strip()
            game_link = item.find("a")["href"]
            games[game_name] = BASE_URL + game_link

    next_page = soup.find("span", {"class": "next"})
    if next_page is not None:
        links.append(next_page.find("a")["href"])

with open("games.json", "w") as f:
    json.dump(games, f)
