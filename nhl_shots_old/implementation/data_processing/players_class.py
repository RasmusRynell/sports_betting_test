import Settings
import data_processing.api_class
import datetime
import json

class players:
    def __init__(self):
        self.api = Settings.api
        self.player_ids = self.get_player_ids()


    def get_player_ids(self):
        json_response = self.api.send_request("/teams?expand=team.roster&site=en_nhlNR&season=20202021", True)
        player_ids = {}

        for team in json_response["teams"]:
            for player in team['roster']['roster']:
                if (player["person"]["fullName"].lower() in player_ids):
                    player_ids[player["person"]["fullName"].lower()].append(player["person"]["id"])
                else:
                    player_ids[player["person"]["fullName"].lower()] = [player["person"]["id"]]

        return player_ids


    '''
    Converts a players name into its id, if there is more than one id for this player,
    i.e. the player has been transferred mid season an error will be thrown.
    '''
    def get_id(self, name):
        if (name.lower() in self.player_ids):
            if len(self.player_ids[name.lower()]) > 1:
                raise Exception("ERROR: The team \"{}\" has more than one id, the player has been transfered mid season! \n ".format(name) + str(self.player_ids[name.lower()]))
            return self.player_ids[name.lower()][0]
        else:
            if(name.lower() in Settings.player_nicknames):
                return self.get_id(Settings.player_nicknames[name.lower()])
            raise Exception("ERROR: Cannot convert player \"{}\" to an id, it's not in the database!".format(name))


    def get_games_in_season(self, id, season):
        res = []
        response_json = self.api.send_request("/people/{}/stats?stats=gameLog&season={}".format(id, season))
        split = response_json["stats"][0]["splits"]
        for game in split:
            res.append((game['game']['gamePk'], game['date']))
        return res

    
    def get_all_games_from_season_player(self, id, season):
        response_json = self.api.send_request("/people/{}/stats?stats=gameLog&season={}".format(id, season))
        return response_json["stats"][0]["splits"]


    '''
    Takes in two dicts and returns the first one now containing the
    added values for each key
    '''
    def add_stats_together(self, old, new, season):
        for key, value in new.items():
            if key in old:
                old[key] = (value + old[key])
            else:
                old[key] = new[key]
        return old


    def get_relevant_information_from_player_game(self, game, season, name_addition):
        stats = game["stat"]
        result = {}

        for key, stat in stats.items():
            if isinstance(stat, str):
                if (':' in stat):
                    result[str(season) + "-player-" + name_addition + str(key)] = int(stat.split(":")[0])*60 + int(stat.split(":")[1])
                else:
                    result[str(season) + "-player-" + name_addition + str(key)] = int(stat)
            else:
                result[str(season) + "-player-" + name_addition + str(key)] = int(stat)

        return result

    
    def get_player_season_stats(self, id, season, up_to_date="9999-01-01", total_matches=9999):
        last_matches_string = ""
        if total_matches != 9999:
            last_matches_string = "last" + str(total_matches) + "_matches-"

        #Convert date into datetime object if it isn't that already
        if isinstance(up_to_date, str):
            up_to_date = up_to_date.split('-')
            up_to_date = datetime.datetime(int(up_to_date[0]), int(up_to_date[1]), int(up_to_date[2]))

        all_games = self.get_all_games_from_season_player(id, season)

        total_stats = {}
        for game in all_games:
            game_date = game['date'].split('-')
            game_date = datetime.datetime(int(game_date[0]), int(game_date[1]), int(game_date[2]))
            if (game_date < up_to_date):
                total_stats = self.add_stats_together(total_stats, self.get_relevant_information_from_player_game(game, season, last_matches_string), season)

                if (str(season) + "-player-" + last_matches_string + 'totalGames') in total_stats:
                    total_stats[str(season) + "-player-" + last_matches_string + 'totalGames'] += 1
                else:
                    total_stats[str(season) + "-player-" + last_matches_string + 'totalGames'] = 1

                total_matches -= 1
                if (total_matches <= 0):
                    break
        return total_stats

    def calculate_answers(self, player_id, game_id):
        response_json = self.api.send_request("/game/{}/boxscore".format(game_id))
        for team in response_json["teams"]:
            for player in response_json["teams"][team]["players"]:
                if response_json["teams"][team]["players"][player]["person"]["id"] == player_id:
                    return {
                        "shots_this_game_O3.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] > 3.5),
                        "shots_this_game_O2.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] > 2.5),
                        "shots_this_game_O1.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] > 1.5),
                        "shots_this_game_U1.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] < 1.5),
                        "shots_this_game_U2.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] < 2.5),
                        "shots_this_game_U3.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] < 3.5),
                        "shots_this_game_total": response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"]
                    }


    def __str__(self):
        return self.name
