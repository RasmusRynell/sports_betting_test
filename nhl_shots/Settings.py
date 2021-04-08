import json
import dateutil.parser
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz
from functools import lru_cache


def print_json(j):
    print(json.dumps(j, indent=4, sort_keys=True))

@lru_cache(maxsize = 10000)
def string_to_standard_datetime(s):
    return dt.fromisoformat(str(dateutil.parser.parse(s))).astimezone(timezone.utc)

@lru_cache(maxsize = 1000)
def date_to_season(date):
    half_date = dt(int(date.year), 7, 20).replace(tzinfo=pytz.UTC)

    season = int(date.year)
    if date < half_date:
        season = int(date.year) - 1

    return season







current_season = 2021
num_of_seasons_to_go_back = 10 #10
num_of_seasons_to_go_back_for_data = 1 #1
num_of_games_back_to_track = 5 #10




all_seasons = [str(j)+str(i) for i, j in
            zip(reversed(range(1917, current_season + 1)),
                reversed(range(1917, current_season)))]





banned_players = []
old_banned_players = [
    "sebastian aho", "sebastian (1997) aho", "sebastian antero aho", "Sebastian Aho", "nikita gusev", "n. gusev", "shayne gostisbehere"]


# Go here get player name: https://statsapi.web.nhl.com/api/v1/teams?expand=team.roster&site=en_nhlNR&season=20202021
player_nicknames = {}
old_player_nicknames = {
                        "alexander ovechkin": "ALEX OVECHKIN",
                        "sebastian antero aho": "Sebastian Aho",
                        "Nicholas Suzuki": "Nick Suzuki",
                        "artemy panarin": "Artemi Panarin",
                        "n. hoglander":"Nils Hoglander",
                        "d. gurianov": "Denis Gurianov",
                        "j. hughes":"Jack Hughes",
                        "R. Johansen": "Ryan Johansen",
                        "M. Ekholm":"Mattias Ekholm",
                        "P. Hornqvist":"Patric Hornqvist",
                        "K. Kaprizov":"Kirill Kaprizov",
                        "K. Fiala":"kevin Fiala",
                        "A. Killorn":"alex Killorn",
                        "joel eriksson-ek": "joel eriksson ek",
                        "mitch marner": "Mitchell Marner",
                        "bowie horvat": "Bo Horvat",
                        "p. k. subban": "p.k. subban",
                        "j. bratt": "jesper bratt",
                        "n. gusev":"Nikita Gusev",
                        "N. Gusev":"Nikita Gusev",
                        "e. tolvanen": "Eeli Tolvanen",
                        "f. forsberg": "Filip Forsberg",
                        "t. j. oshie": "T.J. Oshie",
                        "m. wood": "Miles Wood",
                        "M. Dumba": "Matt Dumba",
                        "james van":"James van Riemsdyk",
                        "joel eriksson": "Joel Eriksson Ek",
                        "E. Haula": "Erik Haula",
                        "N. Schmaltz": "Nick Schmaltz",
                        "tim stuetzle": "Tim Stützle",
                        "T. Stutzle": "Tim Stützle",
                        "tim stutzle": "Tim Stützle",
                        "T. Stuetzle": "Tim Stützle",
                        "evgeny dadonov": "Evgenii Dadonov",
                        "V. Tarasenko": "Vladimir Tarasenko",
                        "K. Labanc": "Kevin Labanc",
                        "P. Dubois": "Pierre-Luc Dubois",
                        "nicholas paul" : "nick paul",
                        "C. Verhaeghe": "carter verhaeghe",
                        "K. Shattenkirk": "Kevin Shattenkirk",
                        "Maxime Comtois": "max Comtois"
                        }

teams_translate = {}
old_teams_translate = {"arz coyotes": "arizona coyotes",
                       "min wild": "minnesota wild",
                       "NAS predators": "Nashville Predators",
                       "TB Lightning": "Tampa Bay Lightning",
                       "BOS bruins": "Boston Bruins",
                       "PIT Penguins": "Pittsburgh Penguins",
                       "CHI blackhawks": "Chicago Blackhawks",
                       "FLA Panthers": "Florida Panthers",
                       "PHI Flyers": "Philadelphia Flyers",
                       "NY Rangers": "New York Rangers",
                       "VAN Canucks": "Vancouver Canucks",
                       "OTT Senators": "Ottawa Senators",
                       "WAS capitals": "Washington Capitals",
                       "EDM Oilers": "Edmonton Oilers",
                       "CAL Flames": "Calgary Flames",
                       "BUF Sabres": "Buffalo Sabres",
                       "MON Canadiens": "Montréal Canadiens",
                       "WIN Jets": "Winnipeg Jets",
                       "SJ Sharks": "San Jose Sharks",
                       "VGS Golden Knights": "VEGAS Golden Knights",
                       "STL Blues": "St. Louis Blues",
                       "LA Kings": "Los Angeles Kings",
                       "ANA Ducks": "Anaheim Ducks",
                       "NJ Devils": "New Jersey Devils",
                       "NY Islanders": "New York Islanders",
                       "CAR Hurricanes": "Carolina Hurricanes",
                       "Carolina Hurrican":"carolina hurricanes",
                       "det red wings": "Detroit Red Wings",
                       "DAL Stars": "Dallas Stars",
                       "COL Avalanche": "Colorado Avalanche",
                       "CLB Blue Jackets": "Columbus Blue Jackets",
                       "CBJ Blue Jackets": "Columbus Blue Jackets",
                       "TOR Maple Leafs": "Toronto Maple Leafs",
                       "St Louis Blues":"St. Louis Blues",
                       "Montreal Canadiens": "Montréal Canadiens",
                       "St.Louis Blues":"St. Louis Blues",
                       "Columbus Blue": "Columbus Blue Jackets"
                       }


name_translate = {}
old_name_translate = {"p. k. subban": "p.k. subban",
                        "Patric Hörnqvist": "patric hornqvist",
                        "patric hÒÂrnqvist": "patric hornqvist",
                        "patric h�rnqvist": "patric hornqvist"}



for v in old_banned_players:
    banned_players.append(v.lower())

for k, v in old_teams_translate.items():
    teams_translate[k.lower()] = v.lower()

for k, v in old_player_nicknames.items():
    player_nicknames[k.lower()] = v.lower()

for k, v in old_name_translate.items():
    name_translate[k.lower()] = v.lower()



from implementations.api.handler import api as api_class
api = None

from implementations.database.handler import database as database_class
db = None

def init(api_b=True, db_b=True):
    global api
    global db
    if api_b and api==None:
        api = api_class("https://statsapi.web.nhl.com/api/v1", True, True)
    if db_b and db==None:
        db = database_class(api, "./data/db_games.json", "./data/db_old_odds.json", "./data/db_team_ids.json", "./data/db_player_ids.json")
