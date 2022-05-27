import bs4
import requests
import json

BASE_URL = "https://adventuregamers.com"

with open("games.json", "r") as f:
    games_list = json.load(f)

for url in games_list.values():
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1", {"class": "page_title"}).text
    print(f"Scraping {title}")
    description = soup.find("div", {"id": "game_desc"})
    if description is None or description.text == "":
        print(f"Skipped game: {title}")
        continue

    game_info = {"title": title, "description": description.text}

    sidebox = soup.find("div", {"id": "sidebox"})
    for p in sidebox.find_all("p"):
        if "Developer:" in p.text:
            game_info["developer"] = p.text.replace("Developer:", "").strip()
            break

    game_info["cover"] = soup.find("div", {"class": "feat_image"}).find("img")["data-src"]

    screenshots = [img["data-src"] for img in soup.find_all("img", {"itemprop": "screenshot"})]
    game_info["screenshots"] = screenshots

    table = soup.find("table", {"class": "game_info_table"})
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        game_info[tds[0].text] = tds[1].text

    game_info["url"] = url

    with open(f"gamesdb.json", "r") as f:
        gamesdb = json.load(f)
    if title not in gamesdb:
        with open(f"gamesdb.json", "w") as f:
            gamesdb[title] = game_info
            json.dump(gamesdb, f, indent=4, ensure_ascii=False)
        # print(json.dumps(game_info, indent=4))

