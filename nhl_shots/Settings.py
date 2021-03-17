from data_processing.api_class import api
import json

api = api("https://statsapi.web.nhl.com/api/v1", True, True)



current_season = 2021
num_of_seasons_to_go_back = 10 #3
num_of_seasons_to_go_back_for_data = 1 #3
num_of_games_back_to_track = 10 #5
global_csv = False

all_seasons = [str(j)+str(i) for i, j in
            zip(reversed(range(1917, current_season + 1)),
                reversed(range(1917, current_season)))]



#   ram usage: Show ram usage when creating CSV
#   print_api_cache: Print whole api cache

#
Debug = {   "ram usage": True,
            "print_api_cache": False}




def print_json(j):
    print(json.dumps(j, indent=4, sort_keys=True))


# Go here get player najme: https://statsapi.web.nhl.com/api/v1/teams?expand=team.roster&site=en_nhlNR&season=20202021
player_nicknames = {}
old_player_nicknames = {
                        "alexander ovechkin": "ALEX OVECHKIN",
                        "sebastian antero aho": "Sebastian Aho"
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
                       "det red wings": "Detroit Red Wings",
                       "DAL Stars": "Dallas Stars",
                       "COL Avalanche": "Colorado Avalanche"
                       }






for k, v in old_teams_translate.items():
    teams_translate[k.lower()] = v.lower()




for k, v in old_player_nicknames.items():
    player_nicknames[k.lower()] = v.lower()