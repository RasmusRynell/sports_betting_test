import Settings
import data_processing.api_class
import datetime
import json
from tqdm import tqdm

class teams:
    def __init__(self):
        self.api = Settings.api
        self.team_ids = self.get_team_ids()

    def get_team_ids(self):
        json_response = self.api.send_request("/teams", True)

        team_ids = {}
        for team in json_response['teams']:
            team_id = team["id"]
            if (team["name"].lower() in team_ids):
                team_ids[team["name"].lower()].append(team_id)
            else:
                team_ids[team["name"].lower()] = [team_id]
        return team_ids


    '''
    Converts a teams name into its id, if there is more than one id for this team,
    i.e. something is terrably wrong and an error will bne trown.
    '''
    def get_id(self, name):
        if (name.lower() in self.team_ids):
            if len(self.team_ids[name.lower()]) > 1:
                raise Exception("ERROR: The team \"{}\" has more than one id! \n ".format(name) + str(self.team_ids[name.lower()]))
            return self.team_ids[name.lower()][0]
        elif (name.lower() in Settings.teams_translate):
            return self.get_id(Settings.teams_translate[name.lower()])
        else:
            raise Exception("ERROR: Cannot convert team \"{}\" to an id, it's not in the database!".format(name))



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


    def calculate_more_stats_from_already_existing_data(self, data, season, key_addition, last_matches_string):
        #own
        if data:
            data [str(season) + key_addition + "-team-own-" + last_matches_string + 'faceOffWinPercentage'] = \
                data[str(season) + key_addition + "-team-own-" + last_matches_string + 'faceOffWinPercentage'] \
                    / data[str(season) + key_addition + "-team-own-" + last_matches_string + 'totalGames']

            data[str(season) + key_addition + "-team-own-" + last_matches_string + 'shotspergame'] = \
                data[str(season) + key_addition + "-team-own-" + last_matches_string + 'shots'] \
                    / data[str(season) + key_addition + "-team-own-" + last_matches_string + 'totalGames']

            data[str(season) + key_addition + "-team-own-" + last_matches_string + 'shotsAllowed'] = \
                data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'shots'] \
                    / data[str(season) + key_addition + "-team-own-" + last_matches_string + 'totalGames']

            #opp
            data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'faceOffWinPercentage'] = \
                data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'faceOffWinPercentage'] \
                    / data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'totalGames']

            data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'shotspergame'] = \
                data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'shots'] \
                    / data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'totalGames']

            data[str(season) + key_addition + "-team-opp-" + last_matches_string + 'shotsAllowed'] = \
                data[str(season) + key_addition + "-team-own-" + last_matches_string + 'shots'] \
                    / data[str(season) + key_addition + "-team-own-" + last_matches_string + 'totalGames']
        return data


    def get_relevant_information_from_team_game(self, game, season, team_id, key_addition, name_addition):
        response_json = game
        teams = response_json['teams']
        away_team = teams['away']
        home_team = teams['home']
        relevant_team = {}
        irrelevant_team = {}
        if away_team['team']['id'] == team_id:
            relevant_team = away_team
            irrelevant_team = home_team
        elif home_team['team']['id'] == team_id:
            relevant_team = home_team
            irrelevant_team = away_team
        else:
            raise("Something has gone horribly wrong when trying to get match data!")

        stats_rel = relevant_team['teamStats']['teamSkaterStats']
        stats_irrel = irrelevant_team['teamStats']['teamSkaterStats']

        result = {}

        for key, value in stats_rel.items():
            if isinstance(value, str):
                result[str(season) + key_addition + "-team-own-" + name_addition + str(key)] = float(value)/100
            else:
                result[str(season) + key_addition + "-team-own-" + name_addition + str(key)] = value

        for key, value in stats_irrel.items():
            if isinstance(value, str):
                result[str(season) + key_addition + "-team-opp-" + name_addition + str(key)] = float(value)/100
            else:
                result[str(season) + key_addition + "-team-opp-" + name_addition + str(key)] = value
                
        return result


    def get_all_games(self, season, up_to_game_id):
        games = {}
        prefix = str(season)[0 : 4]
        up_to_game_id_new = str(9999).zfill(4)
        if up_to_game_id:
            prefix = str(up_to_game_id)[0 : 4]
            up_to_game_id_new = str(up_to_game_id)[-4:]
            
        curr = 1
        while (curr < int(up_to_game_id_new)):
            response_json = self.api.send_request("/game/{}/boxscore".format(prefix + "02" + str(curr).zfill(4)))

            if (up_to_game_id_new == "9999" and "message" in response_json):
                break
            home_team_id = response_json['teams']['home']['team']['id']
            away_team_id = response_json['teams']['away']['team']['id']

            if home_team_id not in games:
                games[home_team_id] = [response_json]
            else:
                games[home_team_id].insert(0, response_json)

            if away_team_id not in games:
                games[away_team_id] = [response_json]
            else:
                games[away_team_id].insert(0, response_json)
            curr += 1

        return games


    def get_team_stats_from_season(self, team_id, season, up_to_game_id, key_addition="", total_matches=9999):
        last_matches_string = ""
        if total_matches != 9999:
            last_matches_string = "last" + str(total_matches) + "_matches-"

        total_stats = {}
        all_games = self.get_all_games(season, up_to_game_id)
        if team_id in all_games:
            for game in all_games[team_id]:
                total_stats = self.add_stats_together(total_stats, self.get_relevant_information_from_team_game(
                    game, season, team_id, key_addition, last_matches_string), season)

                if (str(season) + key_addition + "-team-own-" + last_matches_string + 'totalGames') in total_stats:
                        total_stats[str(season) + key_addition + "-team-own-" + last_matches_string + 'totalGames'] += 1
                        total_stats[str(season) + key_addition + "-team-opp-" + last_matches_string + 'totalGames'] += 1
                else:
                    total_stats[str(season) + key_addition + "-team-own-" + last_matches_string + 'totalGames'] = 1
                    total_stats[str(season) + key_addition + "-team-opp-" + last_matches_string + 'totalGames'] = 1

                total_matches -= 1
                if (total_matches == 0):
                    break
        return self.calculate_more_stats_from_already_existing_data(total_stats, season, key_addition, last_matches_string)



    def __str__(self):
        return self.name
