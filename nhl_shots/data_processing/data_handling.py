import Settings
from data_processing.players_class import players
from data_processing.teams_class import teams
from data_processing.api_class import api

import csv
import requests, json, sys
import datetime
from tqdm import tqdm
from datetime import datetime as dt
from datetime import timedelta
import pytz



api = Settings.api
players = players()
teams = teams()



def check_if_player_in_team_from_match(player_id, game_id, force = False):
    game = api.send_request("/game/{}/boxscore".format(game_id), force)
    if "ID" + str(player_id) in game['teams']['home']['players']:
        return (game['teams']['home']['team']['id'], game['teams']['away']['team']['id'], 1)
    elif "ID" + str(player_id) in game['teams']['away']['players']:
        return (game['teams']['away']['team']['id'], game['teams']['home']['team']['id'], 0)
    if force:
        Settings.print_json(game)
        print(str(player_id) + " : " + str(game_id))
        raise ("Player is not in the game xd")
    else:
        return check_if_player_in_team_from_match(player_id, game_id, True)
    


def calculate_data(player_id, team_id, opp_team_id, home_away, game, season, season_index, total_stats_default):
    (game_id, game_date) = game

    total_stats = total_stats_default
    team_id_this_match = team_id
    opponent_team_id_this_match = opp_team_id
    total_stats["is_home_game"] = 1 if home_away == "home" else 0

    if game_id != "2020029999":
        (team_id_this_match, opponent_team_id_this_match, total_stats["is_home_game"]) = check_if_player_in_team_from_match(player_id, game_id)

        # Calculate stats
        total_stats.update(players.calculate_answers(player_id, game[0]))
        

    #Player stats
    #Player stats season_index seasons ago
    for current_season_index in range(1, Settings.num_of_seasons_to_go_back_for_data):
        total_stats.update(players.get_player_season_stats(player_id, Settings.all_seasons[current_season_index + season_index]))
        total_stats.update(teams.get_team_stats_from_season(team_id_this_match, Settings.all_seasons[current_season_index + season_index], "", "-team_player"))
        total_stats.update(teams.get_team_stats_from_season(opponent_team_id_this_match, Settings.all_seasons[current_season_index + season_index], "", "-team_opponent"))

    #Player stats current season
    total_stats.update(players.get_player_season_stats(player_id, season))

    #All player stats this season last 1...5 games
    for i in range(1, Settings.num_of_games_back_to_track + 1):
        total_stats.update(players.get_player_season_stats(player_id, season, game[1], i))

    #TODO: #Procent of teams shots (total)

    #TODO: #Player procent of teams shots (last two games)


    #Team stats

    #Player team
    #Team stats current season
    total_stats.update(teams.get_team_stats_from_season(team_id_this_match, season, game_id, "-team_player"))

    #Team stats last 2 games
    total_stats.update(teams.get_team_stats_from_season(team_id_this_match, season, game_id, "-team_player", 2))

    #Opponent team
    #Opponent stats current season
    total_stats.update(teams.get_team_stats_from_season(opponent_team_id_this_match, season, game_id, "-team_opponent"))

    #Opponent stats last 2 games
    total_stats.update(teams.get_team_stats_from_season(opponent_team_id_this_match, season, game_id, "-team_opponent", 2))


    #TODO: #Player team Last two matches against that team

    #TODO: #Player teams shots against opp two last matches



    #TODO: #Form last 5 games (???)
    return total_stats







def generate_and_save_data(player_id, team_id, opp_team_id, home_away, path):
    # Open and write to csv-file
    with open(str(path), 'w+', newline='\n') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        most = 0
        most_dict = {}


        res = generate_default_keys(Settings.num_of_games_back_to_track, Settings.all_seasons[0], 0)
        res.update(calculate_data(player_id, team_id, opp_team_id, home_away, ("2020029999", "9999-01-01"), Settings.all_seasons[0], 0, res))
        writer.writerow(res.keys())
        writer.writerow(res.values())


        # Loop though num of seasons to get datapoints from
        for season_index in tqdm(range(0, Settings.num_of_seasons_to_go_back)):

            index_current_season = 0
            for i in range(len(Settings.all_seasons)):
                if Settings.all_seasons[i] == Settings.all_seasons[season_index]:
                    index_current_season = i

            # Loop trough all games the player has played that season
            for game in tqdm(players.get_games_in_season(player_id, Settings.all_seasons[season_index])):
                # Get and write the relevant stats for this game
                res = generate_default_keys(Settings.num_of_games_back_to_track, Settings.all_seasons[season_index], index_current_season)
                res.update(calculate_data(player_id, team_id, opp_team_id, False, game, Settings.all_seasons[season_index], index_current_season, res))
                if (len(res) != 448):
                    print("FEL:")
                    print(len(res))
                    print(json.dumps(res, indent=4, sort_keys=True))
                if len(res) > most:
                    most = len(res)
                    most_dict = res.copy()
                writer.writerow(res.values())

        # Debug and for now to change "generate_default_keys()"
        #print(json.dumps(most_dict, indent=4, sort_keys=True))
        #print("Total number of fields: " + str(most))


def get_game_pk(new_timezone_timestamp, data, tries = 3):
    schedule = Settings.api.send_request("/schedule?date={}".format(str(new_timezone_timestamp.date())))

    for d in schedule["dates"]:
        if d["date"] == str(new_timezone_timestamp.date()):
            for game in d["games"]:
                if (Settings.teams_translate[data[4].lower()] == str(game["teams"]["away"]["team"]["name"]).lower()\
                    and Settings.teams_translate[data[5].lower()] == str(game["teams"]["home"]["team"]["name"]).lower()) or\
                    (Settings.teams_translate[data[5].lower()] == str(game["teams"]["away"]["team"]["name"]).lower()\
                    and Settings.teams_translate[data[4].lower()] == str(game["teams"]["home"]["team"]["name"]).lower()):

                    print("Home: " + str(game["teams"]["home"]["team"]["name"]).lower())
                    print("Away: " + str(game["teams"]["away"]["team"]["name"]).lower())
                    print(game["gamePk"])
                    return game["gamePk"]
    
    if tries == 0:
        print("Should be: " + str(data[4]) + " and " + str(data[5]))
        print(new_timezone_timestamp)
        print(schedule)
        raise("Could not find a game this date...")
    else:
        new_timezone_timestamp = new_timezone_timestamp - timedelta(days=1)
        return get_game_pk(new_timezone_timestamp, data, tries - 1)

def get_current_game(data):
    date = str(data[-1][4:])
    print(date)
    (date_day, date_month, date_time) = date.split(" ")

    if date_month == "maj":
        date_month = "may"
    elif date_month == "okt":
        date_month = "oct"
    
    date = str(date_day) + " "
    date += str(date_month) + " "
    date += str(date_time) + ":"
    date += str(Settings.current_season)

    date = dt.strptime(date, "%d %b %H:%M:%Y")

    # create both timezone objects
    old_timezone = pytz.timezone("Europe/Stockholm")
    new_timezone = pytz.timezone("Europe/London")
    new_timezone_timestamp = old_timezone.localize(date).astimezone(new_timezone)
    new_timezone_timestamp = new_timezone_timestamp + timedelta(days=1)

    return get_game_pk(new_timezone_timestamp, data)



def save_data_player(bet, current_game_data, path=""):
    (name, player_team_name, opp_team_name, home_away) = bet
    if not path:
        path = "pp_" + str(name) + ".csv"
    path = path.lower().replace(' ', '_')
    path = "./temp/"+ path

    current_game = get_current_game(current_game_data)
    '''
    generate_and_save_data(players.get_id(name), 
                            teams.get_id(player_team_name), 
                            teams.get_id(opp_team_name),
                            home_away,
                            path)

    if Settings.Debug["print_api_cache"]:
        api.print_cache()
    '''
    return path



def generate_default_keys(last_games, season, index_current_season):
    done = {
        "is_home_game": 0,
        "shots_this_game_O1.5": 0,
        "shots_this_game_O2.5": 0,
        "shots_this_game_O3.5": 0,
        "shots_this_game_U1.5": 0,
        "shots_this_game_U2.5": 0,
        "shots_this_game_U3.5": 0,
        "shots_this_game_total": 0
    }

    player_data = {
        "assists": 5,
        "blocked": 4,
        "evenTimeOnIce": 5804,
        "faceOffPct": 0,
        "gameWinningGoals": 1,
        "games": 6,
        "goals": 2,
        "hits": 18,
        "overTimeGoals": 1,
        "penaltyMinutes": 2,
        "pim": 2,
        "plusMinus": -1,
        "points": 7,
        "powerPlayGoals": 0,
        "powerPlayPoints": 3,
        "powerPlayTimeOnIce": 1040,
        "shifts": 131,
        "shortHandedGoals": 0,
        "shortHandedPoints": 0,
        "shortHandedTimeOnIce": 0,
        "shotPct": 49,
        "shots": 21,
        "timeOnIce": 6844,
        "totalGames": 6,
    }

    player_data_lastX_matches = {
        "assists": 0,
        "blocked": 0,
        "evenTimeOnIce": 986,
        "faceOffPct": 0,
        "gameWinningGoals": 0,
        "games": 1,
        "goals": 0,
        "hits": 0,
        "overTimeGoals": 0,
        "penaltyMinutes": 2,
        "pim": 2,
        "plusMinus": -2,
        "points": 0,
        "powerPlayGoals": 0,
        "powerPlayPoints": 0,
        "powerPlayTimeOnIce": 397,
        "shifts": 21,
        "shortHandedGoals": 0,
        "shortHandedPoints": 0,
        "shortHandedTimeOnIce": 0,
        "shotPct": 0,
        "shots": 5,
        "timeOnIce": 1383,
        "totalGames": 1
    }

    teams_data = {
        "assists": 2,
        "evenTimeOnIce": 4418,
        "faceOffPct": 267,
        "gameWinningGoals": 0,
        "games": 5,
        "overTimeGoals": 0,
        "penaltyMinutes": 0,
        "plusMinus": 3,
        "points": 3,
        "powerPlayPoints": 0,
        "powerPlayTimeOnIce": 728,
        "shifts": 112,
        "shortHandedGoals": 0,
        "shortHandedPoints": 0,
        "shortHandedTimeOnIce": 49,
        "shotPct": 100,
        "blocked": 105,
        "faceOffWinPercentage": 0.415375,
        "giveaways": 92,
        "goals": 17,
        "hits": 218,
        "pim": 61,
        "powerPlayGoals": 3.0,
        "powerPlayOpportunities": 30.0,
        "powerPlayPercentage": 1.4,
        "shots": 183,
        "shotsAllowed": 32.5,
        "shotspergame": 22.875,
        "takeaways": 66,
        "totalGames": 8,
    }

    teams_data_last_2_games = {
        "last2_matches-blocked": 23,
        "last2_matches-faceOffWinPercentage": 0.5735,
        "last2_matches-giveaways": 6,
        "last2_matches-goals": 7,
        "last2_matches-hits": 74,
        "last2_matches-pim": 14,
        "last2_matches-powerPlayGoals": 2.0,
        "last2_matches-powerPlayOpportunities": 6.0,
        "last2_matches-powerPlayPercentage": 0.75,
        "last2_matches-shots": 57,
        "last2_matches-shotsAllowed": 28.0,
        "last2_matches-shotspergame": 28.5,
        "last2_matches-takeaways": 12,
        "last2_matches-totalGames": 2,
    }

    for season_index in range(0, Settings.num_of_seasons_to_go_back_for_data):
        for key in player_data.keys():
            done[str(Settings.all_seasons[season_index + index_current_season]) + "-player-" + str(key)] = 0

        for team in ("-team_opponent-", "-team_player-"):
            for stats_team in ("team-opp-", "team-own-"):
                for key in teams_data.keys():
                    done[str(Settings.all_seasons[season_index + index_current_season]) + str(team) + str(stats_team) + str(key)] = 0


    for team in ("-team_opponent-", "-team_player-"):
        for stats_team in ("team-opp-", "team-own-"):
            for key in teams_data_last_2_games.keys():
                done[str(Settings.all_seasons[index_current_season]) + str(team) + str(stats_team) + str(key)] = 0

    for last_game in range(1, last_games + 1):
        for key in player_data_lastX_matches.keys():
            done[str(season) + "-player-" + "last" + str(last_game) + "_matches-" + str(key)] = 0
    
    return done
