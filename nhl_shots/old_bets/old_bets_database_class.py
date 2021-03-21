import json
from datetime import datetime as dt
from datetime import timedelta
import Settings


''' 
STRUCTURE

old_bets:
{"bets":[GAME1, GAME2, GAME3, ...]}

GAME:
{
    "game_id":(INT),
    "date":(STRING yyyy-mm-dd),
    "home_team_name":(STRING)
    "away_team_name":(STRING)
    "home_team_id":(INT),
    "away_team_id":(INT),
    "players": [PLAYER1, PLAYER2, PLAYER3, ...]
}

PLAYER:
{
    "name":(STRING)
    "team_name":(STRING)
    "id":(INT)
    "team_id":(INT)
    "known_over_under":(FLOAT)
    "bets": {   
                "bet365": {"over": (FLOAT), "under": (FLOAT), "over-under": (FLOAT)},
                "unibet": {"over": (FLOAT), "under": (FLOAT), "over-under": (FLOAT)},
                ...
            },
    "known_stats": {"shots":(int)}
}
'''



class old_bets_database:
    def __init__(self, api, data_handling, path=""):
        self.api = api
        self.data_handling = data_handling
        self.games = data_handling.get_all_games(Settings.num_of_seasons_to_go_back)
        self.old_bets = {"bets":[]}
        self.path = path

        if path:
            self.old_bets.update(self.load_json_file(path))

    def load_json_file(self, path):
        try:
            with open(path) as json_file:
                return json.load(json_file)
        except:
            print("Could not find file {}".format(path))
            return {}

    def save_to_json_file(self, path=""):
        try:
            if not path:
                path = self.path
            with open(path, "w") as f:
                f.write(json.dumps(self.old_bets))
        except:
            print("Something went wrong when saving database...")


    def add_bet(self, date, player_name, home_team_name, away_team_name, site, over, under, over_under = ""):
        player_id = self.data_handling.get_player_id(player_name)
        home_team_id = self.data_handling.get_team_id(home_team_name)
        away_team_id = self.data_handling.get_team_id(away_team_name)
        
        try:
            game_id = self.data_handling.get_game_from_date(player_id, date, home_team_id, away_team_id)
            if len(game_id) > 1:
                while True:
                    print(game_id)
                    number_to_save = input("would you like to store (1) or (2) or (3), answer with that number: ")
                    number_to_save = (int)(number_to_save)-1
                    if 0 <= number_to_save <= len(game_id):
                        try:
                            print("Number to save: " + str(number_to_save))
                            print(game_id)
                            game_id = game_id[number_to_save][0]
                        except:
                            print("thats not in the list...")
                    if type(game_id) == int:
                        break
            else:
                game_id = game_id[0][0]
        except:
            print("Date: " + date)
            raise("Could not find game on this date...")
        print(game_id)

        game_found = False
        for game in self.old_bets["bets"]:
            if str(game["game_id"]) == str(game_id):
                game_found = True
                print("Found the game!")
                player_found = False
                for p in game["players"]:
                    if str(p["id"]) == str(player_id):
                        player_found = True
                        if site in p["bets"]:
                            print("We already have this in the database... PLAYER = \"{}\", TEAMS = (\"{}\", \"{}\")". format(player_name, home_team_name, away_team_name))
                            print("[ALREADY IN THE DATABSE]")
                            Settings.print_json(p["bets"][site])
                            print("\n[YOU'RE NEW ADDITION]")
                            Settings.print_json({"over": over, "under": under, "over_under": over_under})

                            number_to_save = ""
                            while True:
                                number_to_save = input("would you like to store (1) or (2), answer with that number: ")
                                if "1" == number_to_save or "2" == number_to_save:
                                    if number_to_save == "2":
                                        if not over_under:
                                            over_under = p["known_over_under"]
                                            p["bets"][site] = {"over": over, "under": under, "over_under": over_under}
                                    break
                            return True
                        else:
                            if not over_under:
                                over_under = p["known_over_under"]
                            p["bets"][site] = {"over": over, "under": under, "over_under": over_under}
                            return True

                if not player_found:
                    game["players"].append(self.create_player(player_name, home_team_name, away_team_name, over_under))
                    if not over_under:
                        over_under = input("Could not find existing over_under for player {}, what should it be? (EXAMPLE: 2.5): ".format(player_name))
                    game["players"][-1]["bets"][site] = {"over": over, "under": under, "over_under": over_under}
                    return True

        if not game_found:
            self.old_bets["bets"].append(self.create_game(date, game_id, home_team_name, away_team_name, home_team_id, away_team_id))
            self.old_bets["bets"][-1]["players"].append(self.create_player(player_name, home_team_name, away_team_name, over_under))
            if not over_under:
                over_under = input("Could not find existing over_under for player {}, what should it be? (EXAMPLE: 2.5): ".format(player_name))
            self.old_bets["bets"][-1]["players"][-1]["bets"][site] = {"over": over, "under": under, "over_under": over_under}
            return True

    def remove_bet(self, data):
        pass

    def update_bet(self, data):
        pass

    def create_game(self, date, game_id, home_team, away_team, home_team_id, away_team_id):
        return {
            "game_id": game_id,                     #(INT),
            "date": date,                           #(STRING yyyy-mm-dd),
            "home_team_name":home_team,             #(STRING)
            "away_team_name":away_team,             #(STRING)
            "home_team_id":home_team_id,            #(INT),
            "away_team_id":away_team_id,            #(INT),
            "players": []                           #[PLAYER1, PLAYER2, PLAYER3, ...]
        }


    def create_player(self, player_name, team_one, team_two, known_over_under = ""):
        player_id = self.data_handling.get_player_id(player_name)

        player_team_name = ""
        if self.data_handling.is_player_in_team(player_name, team_one):
            player_team_name = team_one
        elif self.data_handling.is_player_in_team(player_name, team_two):
            player_team_name = team_two
        else:
            raise("FEL player cannot be found in any team!")

        ply_team_id = self.data_handling.get_team_id(player_team_name)

        return {
            "name": player_name,                    #(STRING)
            "team_name":player_team_name,           #(STRING)
            "id":player_id,                         #(INT)
            "team_id":ply_team_id,                  #(INT)
            "known_over_under":known_over_under,    #(FLOAT)
            "bets": {},                             #(STRUCT)
            "known_stats": {}                       #(STRUCT)
        }