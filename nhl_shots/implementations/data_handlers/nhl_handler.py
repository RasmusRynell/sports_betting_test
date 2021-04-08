import Settings
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import dateutil.parser
import pytz

from tqdm import tqdm


def populate_db():
    all_games = get_all_games_last_x_seasons(Settings.num_of_seasons_to_go_back)
    for season_index in all_games:
        all_games[season_index] = sorted(all_games[season_index], key=lambda date: Settings.string_to_standard_datetime(date["date"]))

    done = {}
    done["seasons"] = {}
    done["games_information"] = {}
    done["player_games"] = {}
    done["team_games"] = {}
    for season, stats in all_games.items():
        start = Settings.string_to_standard_datetime("1950-01-01T00:00:00Z")
        played_games_ids = []
        not_played_games_ids = []
        for game in stats:
            if game["status"] == "7" or game["status"] == "6":
                played_games_ids.append(str(game["gamePk"]))
            else:
                not_played_games_ids.append(str(game["gamePk"]))
            done["games_information"][str(game["gamePk"])] = game

            if str(game["teams"]["home"]) not in done["team_games"]:
                done["team_games"][str(game["teams"]["home"])] = {}
            if str(season) not in done["team_games"][str(game["teams"]["home"])]:
                done["team_games"][str(game["teams"]["home"])][str(season)] = []
            done["team_games"][str(game["teams"]["home"])][str(season)].append(game["gamePk"])

            if str(game["teams"]["away"]) not in done["team_games"]:
                done["team_games"][str(game["teams"]["away"])] = {}
            if str(season) not in done["team_games"][str(game["teams"]["away"])]:
                done["team_games"][str(game["teams"]["away"])][str(season)] = []
            done["team_games"][str(game["teams"]["away"])][str(season)].append(game["gamePk"])
        done["seasons"][str(season)] = {"played": played_games_ids, "not_played": not_played_games_ids}


    Settings.db.games = done
    Settings.db.team_ids = get_team_ids()
    Settings.db.player_ids = get_all_player_ids("20202021")




def get_team_ids():
    json_response = Settings.api.send_request("/teams", True)

    team_ids = {}
    for team in json_response['teams']:
        team_id = team["id"]
        if (team["name"].lower() in team_ids):
            team_ids[team["name"].lower()].append(team_id)
        else:
            team_ids[team["name"].lower()] = [team_id]
    return team_ids


def get_all_player_ids(season):
    json_response = Settings.api.send_request("/teams?expand=team.roster&site=en_nhlNR&season={}".format(season), True)
    player_ids = {}
    for team in json_response["teams"]:
        for player in team['roster']['roster']:
            if (player["person"]["fullName"].lower() in player_ids):
                player_ids[player["person"]["fullName"].lower()].append(player["person"]["id"])
            else:
                player_ids[player["person"]["fullName"].lower()] = [player["person"]["id"]]
    return player_ids



def player_in_team(player_id, team_id, gamePk):
    if str(Settings.db.games["games_information"][gamePk]["teams"]["home"]) == str(team_id):
        return int(player_id) in Settings.db.games["games_information"][gamePk]["data"]["teams"]["home"]["skaters"] or\
            str(player_id) in Settings.db.games["games_information"][gamePk]["data"]["teams"]["home"]["skaters"]
    elif str(Settings.db.games["games_information"][gamePk]["teams"]["away"]) == str(team_id):
        return int(player_id) in Settings.db.games["games_information"][gamePk]["data"]["teams"]["away"]["skaters"] or\
            str(player_id) in Settings.db.games["games_information"][gamePk]["data"]["teams"]["away"]["skaters"]
    raise("???")



def update_db():
    print("This is probably not working... will have to fix, problem is with \"team_games\"")
    Settings.db.games["player_games"] = {}
    for season_index in Settings.db.games["seasons"]:
        games = Settings.db.games["seasons"][season_index]
        new_not_played = []
        for game_pk in tqdm(games["not_played"], desc="Updating non-played games"):
            date = Settings.db.games["games_information"][game_pk]["nhl_database_date"]
            games_this_date = fetch_date_data(Settings.string_to_standard_datetime(date[:10]+"T00:00:00Z"), True)
            for g in games_this_date:
                if str(game_pk) == str(g["gamePk"]):

                    # Update list of games played and not played
                    if str(g["status"]) == "7" or str(g["status"]) == "6":
                        games["played"].append(str(g["gamePk"]))
                    else:
                        new_not_played.append(str(g["gamePk"]))



        print("Updated {} games in season {}.".format(len(games["not_played"]) - len(new_not_played), season_index))

        games["not_played"] = new_not_played
        games["played"] = sorted(games["played"], key=lambda gamePk: Settings.string_to_standard_datetime(\
            Settings.db.games["games_information"][str(gamePk)]["date"]))




def get_all_games_last_x_seasons(seasons_to_go_back):
    all_done = {}
    for i in tqdm(range(Settings.current_season - seasons_to_go_back, Settings.current_season), desc="Season"):
        date = dt(i, 8, 1)
        end_date = dt(date.year + 1, 7, 15)
        games = []
        while date != end_date:
            games += fetch_date_data(date)
            date += timedelta(days=1)
        all_done[str(i)] = games
    return all_done



def fetch_date_data(date, force_update=False):
    done = []
    res = Settings.api.send_request("/schedule?date={}".format(str(date.date())), force_update)
    if "message" not in res and res["totalGames"] > 0:
        for game in res["dates"][0]["games"]:
            if str(game["gamePk"])[4:6] == "02" or\
                str(game["gamePk"])[4:6] == "03":
                game_stats = Settings.api.send_request("/game/{}/boxscore".format(game["gamePk"]), force_update)
                done.append(get_stats_from_game(game, game_stats, date))
    return done

def get_stats_from_game(game, game_stats, date):
    return {"gamePk" : game["gamePk"],
            "status" : game["status"]["statusCode"],
            "date" : game["gameDate"],
            "nhl_database_date" : str(date),
            "game_type" : game["gameType"],
            "game_type_num" : str(game["gamePk"])[4:6],
            "teams" : {"home": game["teams"]["home"]["team"]["id"], "away": game["teams"]["away"]["team"]["id"]},
            "data" : {"players": get_all_player_info(game["gamePk"], game_stats),
                                    "teams": {"home": get_all_team_info(game, game_stats, "home"), "away": get_all_team_info(game, game_stats, "away")}}}


def get_all_player_info(gamepk, game_stats):
    done = {}
    for home_or_away in ("home", "away"):
        for player_id in game_stats["teams"][home_or_away]["players"]:
            try:
                done[player_id[2:]] = {
                    "id": player_id[2:],
                    "active": game_stats["teams"][home_or_away]["players"][player_id]["person"]["active"],
                    "rookie": game_stats["teams"][home_or_away]["players"][player_id]["person"]["rookie"],
                    "shootsCatches": game_stats["teams"][home_or_away]["players"][player_id]["person"]["shootsCatches"],
                    "rosterStatus": game_stats["teams"][home_or_away]["players"][player_id]["person"]["rosterStatus"],
                    "primaryPosition": game_stats["teams"][home_or_away]["players"][player_id]["person"]["primaryPosition"]["type"],
                    "primaryPositioncode": game_stats["teams"][home_or_away]["players"][player_id]["person"]["primaryPosition"]["code"],
                    "position": game_stats["teams"][home_or_away]["players"][player_id]["position"]["type"],
                    "code": game_stats["teams"][home_or_away]["players"][player_id]["position"]["code"],
                    "timeOnIce" : convert_string_to_sec(game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["timeOnIce"]),
                    "assists" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["assists"],
                    "goals" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["goals"],
                    "shots" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["shots"],
                    "hits" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["hits"],
                    "powerPlayGoals" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["powerPlayGoals"],
                    "powerPlayAssists" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["powerPlayAssists"],
                    "penaltyMinutes" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["penaltyMinutes"],
                    "faceOffWins" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["faceOffWins"],
                    "faceoffTaken" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["faceoffTaken"],
                    "takeaways" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["takeaways"],
                    "giveaways" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["giveaways"],
                    "shortHandedGoals" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["shortHandedGoals"],
                    "shortHandedAssists" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["shortHandedAssists"],
                    "blocked" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["blocked"],
                    "plusMinus" : game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["plusMinus"],
                    "evenTimeOnIce" : convert_string_to_sec(game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["evenTimeOnIce"]),
                    "powerPlayTimeOnIce" : convert_string_to_sec(game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["powerPlayTimeOnIce"]),
                    "shortHandedTimeOnIce" : convert_string_to_sec(game_stats["teams"][home_or_away]["players"][player_id]["stats"]["skaterStats"]["shortHandedTimeOnIce"])
                }
                if "currentTeam" in game_stats["teams"][home_or_away]["players"][player_id]["person"]:
                    done[player_id[2:]]["team"] = game_stats["teams"][home_or_away]["players"][player_id]["person"]["currentTeam"]["id"]
                else:
                    done[player_id[2:]]["team"] = None

                if "current_age" in game_stats["teams"][home_or_away]["players"][player_id]["person"]:
                    done[player_id[2:]]["current_age"] = game_stats["teams"][home_or_away]["players"][player_id]["person"]["currentAge"]
                else:
                    done[player_id[2:]]["current_age"] = None

            except Exception as e:
                pass
    return done


def get_all_team_info(game, game_stats, home_or_away):
    basic = {
        "id": game["teams"][home_or_away]["team"]["id"],
        "wins": game["teams"][home_or_away]["leagueRecord"]["wins"],
        "losses": game["teams"][home_or_away]["leagueRecord"]["losses"],
        "score": game["teams"][home_or_away]["score"],
        "skaters": game_stats["teams"][home_or_away]["skaters"],
        "scratches": game_stats["teams"][home_or_away]["scratches"]
    }

    if "teamStats" in game_stats["teams"][home_or_away]:
        basic["goals"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["goals"]
        basic["pim"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["pim"]
        basic["shots"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["shots"]
        basic["powerPlayPercentage"] = convert_string_percentage_to_float(game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["powerPlayPercentage"])
        basic["powerPlayGoals"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["powerPlayGoals"]
        basic["powerPlayOpportunities"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["powerPlayOpportunities"]
        basic["faceOffWinPercentage"] = convert_string_percentage_to_float(game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["faceOffWinPercentage"])
        basic["blocked"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["blocked"]
        basic["takeaways"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["takeaways"]
        basic["giveaways"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["giveaways"]
        basic["hits"] = game_stats["teams"][home_or_away]["teamStats"]["teamSkaterStats"]["hits"]

    if str(game["gamePk"])[4:6] != "03":
        basic["ot"] = game["teams"][home_or_away]["leagueRecord"]["ot"]
    else:
        basic["ot"] = 0

    return basic


'''
Converts a teams name into its id, if there is more than one id for this team,
i.e. something is terrably wrong and an error will bne trown.
'''
def get_team_id(name):
    if (name.lower() in Settings.db.team_ids):
        if len(Settings.db.team_ids[name.lower()]) > 1:
            raise Exception("ERROR: The team \"{}\" has more than one id! \n ".format(name) + str(Settings.db.team_ids[name.lower()]))
        return Settings.db.team_ids[name.lower()][0]
    elif (name.lower() in Settings.teams_translate):
        return get_team_id(Settings.teams_translate[name.lower()])
    else:
        raise Exception("ERROR: Cannot convert team \"{}\" to an id, it's not in the database!".format(name))


'''
Converts a players name into its id, if there is more than one id for this player,
i.e. the player has been transferred mid season an error will be thrown.
'''
def get_player_id(name):
    if (name.lower() in Settings.db.player_ids):
        if len(Settings.db.player_ids[name.lower()]) > 1:
            raise Exception("ERROR: The player \"{}\" has more than one id, the player has been transfered mid season! \n ".format(name) + str(Settings.db.player_ids[name.lower()]))
        return Settings.db.player_ids[name.lower()][0]
    else:
        if(name.lower() in Settings.player_nicknames):
            return get_player_id(Settings.player_nicknames[name.lower()])
        raise Exception("ERROR: Cannot convert player \"{}\" to an id, it's not in the database!".format(name))


def player_in_game(player_id, gamePk):
    return str(player_id) in Settings.db.games["games_information"][str(gamePk)]["data"]["players"] or\
        int(player_id) in Settings.db.games["games_information"][str(gamePk)]["data"]["players"]


def get_date_from_gamePk(gamePk):
    return Settings.db.games["games_information"][str(gamePk)]["data"]["date"]

def convert_string_to_sec(time_in_string):
    t = time_in_string.split(":")
    return (int(t[0])*60) + (int(t[1]))


def convert_string_percentage_to_float(per_in_string):
    p = per_in_string.split(".")
    return float((float(p[0])/100) + float(p[1]))
