import Settings
import implementations.data_handlers.nhl_handler as nhl_handler
import traceback
import sys



def generate_training_data(gamePk, player_id, team_id, opp_team_id):
    done = []
    for season in Settings.db.games.values():
        for p_o_np in ("played", "not_played"):
            for game in season[p_o_np]:
                if nhl_handler.player_in_game(player_id, game["gamePk"]):
                    p_team_id = game["teams"]["home"]
                    o_team_id = game["teams"]["away"]
                    if not nhl_handler.player_in_team(player_id, o_team_id) and\
                        not nhl_handler.player_in_team(player_id, p_team_id):
                        continue
                    if nhl_handler.player_in_team(player_id, o_team_id):
                        p_team_id = game["teams"]["away"]
                        o_team_id = game["teams"]["home"]
                    done.append(generate_data(game["gamePk"], player_id, p_team_id, o_team_id))
    return (list(done[0].keys()), done)


def generate_data(game_id, player_id, player_team_id, opp_team_id):
    all_data = generate_deafult()
    old = list(all_data.keys())
    old_len = len(all_data)

    all_games = nhl_handler.get_games_up_to_date(nhl_handler.get_date_from_gameid(game_id))

    all_data.update(generate_player_data(all_games, game_id, player_id, player_team_id, opp_team_id))
    all_data.update(generate_team_data(all_games, game_id, player_team_id, opp_team_id))
    all_data.update(generate_general_data_this_game(game_id, player_id, player_team_id, opp_team_id))

    if old_len != len(all_data):
        print(old_len)
        print(len(all_data))
        s = set(old)
        print([x for x in list(all_data.keys()) if x not in s])
        print("We added some new data field without initalizing it.")
    return all_data


def generate_general_data_this_game(game_id, player_id, player_team_id, opp_team_id):
    for played_not_played in ("played", "not_played"):
        for game in Settings.db.games[str(game_id)[:4]][played_not_played]:
            if game["gamePk"] == game_id:
                return {
                        "gamePk": game_id,
                        "date": game["date"],
                        "game_type": int(game["game_type_num"]),
                        "isHome": int(player_team_id == game["teams"]["home"]),
                        "opp": int(opp_team_id),
                        "shots_this_game_O3.5": int (int(game["data"]["players"][str(player_id)]["shots"]) > 3.5),
                        "shots_this_game_O2.5": int (int(game["data"]["players"][str(player_id)]["shots"]) > 2.5),
                        "shots_this_game_O1.5": int (int(game["data"]["players"][str(player_id)]["shots"]) > 1.5),
                        "shots_this_game_U1.5": int (int(game["data"]["players"][str(player_id)]["shots"]) < 1.5),
                        "shots_this_game_U2.5": int (int(game["data"]["players"][str(player_id)]["shots"]) < 2.5),
                        "shots_this_game_U3.5": int (int(game["data"]["players"][str(player_id)]["shots"]) < 3.5),
                        "shots_this_game_total": int(game["data"]["players"][str(player_id)]["shots"])
                        }
    raise("FEL!")




def generate_player_data(all_games, game_id, player_id, player_team_id, opp_team_id):
    all_stats = {}

    games_player_is_in = []
    last_home_game_same_teams = []
    last_away_game_same_teams = []
    for game in all_games:
        for player_index in game["data"]["players"]:
            if str(player_index) == str(player_id):
                games_player_is_in.append(game)
                if str(game["teams"]["home"]) == str(player_team_id)\
                    and str(game["teams"]["away"]) == str(opp_team_id):
                    last_home_game_same_teams.append(game)

                if str(game["teams"]["home"]) == str(opp_team_id)\
                    and str(game["teams"]["away"]) == str(player_team_id):
                    last_away_game_same_teams.append(game)


    for i in range(Settings.num_of_games_back_to_track):
        if len(games_player_is_in) > i:
            all_stats.update(get_relevant_player_data(games_player_is_in[(-1)-i], player_id, player_team_id, "player-stat-{}-games-back-{}".format("TEMP",i+1)))

    if len(last_home_game_same_teams) > 0:
        all_stats.update(get_relevant_player_data(last_home_game_same_teams[-1], player_id, player_team_id, "player-stat-{}-last-{}-game".format("TEMP", "home")))
    if len(last_away_game_same_teams) > 0:
        all_stats.update(get_relevant_player_data(last_away_game_same_teams[-1], player_id, player_team_id, "player-stat-{}-last-{}-game".format("TEMP", "away")))


    all_stats.update(get_relevant_player_data_average(last_home_game_same_teams+last_away_game_same_teams,\
                                                        player_id, player_team_id, "player-stat-{}-last-{}-game".format("TEMP", "avr")))

    return all_stats





def get_relevant_player_data_average(games, player_id, player_team_id, key):
    total_done = 0
    total = {}
    for game in games:
        game_stats = get_relevant_player_data(game, player_id, player_team_id, key)
        if total == {}:
            total = game_stats
        else:
            for index, value in game_stats.items():
                total[index] = ((total[index]*(total_done)) + value) / (total_done + 1)
        total_done += 1

    return total


def get_relevant_player_data(game, player_id, player_team_id, key):
    for player_index in game["data"]["players"]:
        if str(player_index) == str(player_id):
            return {
                key.replace("TEMP", "current_age"): 0,
                key.replace("TEMP", "rosterStatus"): 0,
                key.replace("TEMP", "primaryPositioncode"): 0,
                key.replace("TEMP", "code"): 0,
                key.replace("TEMP", "timeOnIce"): game["data"]["players"][player_index]["timeOnIce"],
                key.replace("TEMP", "assists"): game["data"]["players"][player_index]["assists"],
                key.replace("TEMP", "goals"): game["data"]["players"][player_index]["goals"],
                key.replace("TEMP", "shots"): game["data"]["players"][player_index]["shots"],
                key.replace("TEMP", "hits"): game["data"]["players"][player_index]["hits"],
                key.replace("TEMP", "powerPlayGoals"): game["data"]["players"][player_index]["powerPlayGoals"],
                key.replace("TEMP", "powerPlayAssists"): game["data"]["players"][player_index]["powerPlayAssists"],
                key.replace("TEMP", "penaltyMinutes"): game["data"]["players"][player_index]["penaltyMinutes"],
                key.replace("TEMP", "faceOffWins"): game["data"]["players"][player_index]["faceOffWins"],
                key.replace("TEMP", "faceoffTaken"): game["data"]["players"][player_index]["faceoffTaken"],
                key.replace("TEMP", "takeaways"): game["data"]["players"][player_index]["takeaways"],
                key.replace("TEMP", "giveaways"): game["data"]["players"][player_index]["giveaways"],
                key.replace("TEMP", "shortHandedGoals"): game["data"]["players"][player_index]["shortHandedGoals"],
                key.replace("TEMP", "shortHandedAssists"): game["data"]["players"][player_index]["shortHandedAssists"],
                key.replace("TEMP", "blocked"): game["data"]["players"][player_index]["blocked"],
                key.replace("TEMP", "plusMinus"): game["data"]["players"][player_index]["plusMinus"],
                key.replace("TEMP", "evenTimeOnIce"): game["data"]["players"][player_index]["evenTimeOnIce"],
                key.replace("TEMP", "powerPlayTimeOnIce"): game["data"]["players"][player_index]["powerPlayTimeOnIce"],
                key.replace("TEMP", "shortHandedTimeOnIce"): game["data"]["players"][player_index]["shortHandedTimeOnIce"],
                key.replace("TEMP", "isHome"): int(str(game["teams"]["home"]) == str(player_team_id)),
                key.replace("TEMP", "gameType"): int(game["game_type_num"])
            }
    raise("Something it terrably wrong djuds")








def generate_team_data(all_games, game_id, player_team_id, opp_team_id):
    all_stats = {}

    all_games = add_stat_in_games(all_games)
    for team in ("player_team", "opp_team"):
        t = opp_team_id
        t_inv = player_team_id
        if team == "player_team":
            t = player_team_id
            t_inv = opp_team_id

        games_team_in = []
        last_home_game_same_teams = []
        last_away_game_same_teams = []
        for game in all_games:
            if str(game["teams"]["home"]) == str(t) or\
                str(game["teams"]["away"]) == str(t):
                    games_team_in.append(game)
                    if str(game["teams"]["home"]) == str(t)\
                        and str(game["teams"]["away"]) == str(t_inv):
                        last_home_game_same_teams.append(game)

                    if str(game["teams"]["home"]) == str(t_inv)\
                        and str(game["teams"]["away"]) == str(t):
                        last_away_game_same_teams.append(game)

        for i in range(Settings.num_of_games_back_to_track):
            if len(games_team_in) > i:
                all_stats.update(get_relevant_team_data(games_team_in[(-1)-i], t, "{}-stat-{}-games-back-{}".format(team, "TEMP",i+1)))

        if len(last_home_game_same_teams) > 0:
            all_stats.update(get_relevant_team_data(last_home_game_same_teams[-1], t, "{}-stat-{}-last-{}-game".format(team, "TEMP", "home")))
        if len(last_away_game_same_teams) > 0:
            all_stats.update(get_relevant_team_data(last_away_game_same_teams[-1], t, "{}-stat-{}-last-{}-game".format(team, "TEMP", "away")))


        all_stats.update(get_relevant_team_data_average(last_home_game_same_teams+last_away_game_same_teams,\
                                                            t, "{}-stat-{}-last-{}-game".format(team, "TEMP", "avr")))

    return all_stats


def get_relevant_team_data_average(games, team_id, key):
    total_done = 0
    total = {}
    for game in games:
        game_stats = get_relevant_team_data(game, team_id, key)
        if total == {}:
            total = game_stats
        else:
            for index, value in game_stats.items():
                total[index] = ((total[index]*(total_done)) + value) / (total_done + 1)
        total_done += 1

    return total


def get_relevant_team_data(game, team_id, key):
    for team_index in ("home", "away"):
        if game["data"]["teams"][str(team_index)] != {}:
            if str(game["data"]["teams"][str(team_index)]["id"]) == str(team_id):
                return {
                    key.replace("TEMP", "wins"): game["data"]["teams"][team_index]["wins"],
                    key.replace("TEMP", "losses"): game["data"]["teams"][team_index]["losses"],
                    key.replace("TEMP", "ot"): game["data"]["teams"][team_index]["ot"],

                    key.replace("TEMP", "score"): game["data"]["teams"][team_index]["score"],
                    key.replace("TEMP", "goals"): game["data"]["teams"][team_index]["goals"],
                    key.replace("TEMP", "pim"): game["data"]["teams"][team_index]["pim"],
                    key.replace("TEMP", "shots"): game["data"]["teams"][team_index]["shots"],
                    key.replace("TEMP", "powerPlayPercentage"): game["data"]["teams"][team_index]["powerPlayPercentage"],
                    key.replace("TEMP", "powerPlayGoals"): game["data"]["teams"][team_index]["powerPlayGoals"],
                    key.replace("TEMP", "powerPlayOpportunities"): game["data"]["teams"][team_index]["powerPlayOpportunities"],
                    key.replace("TEMP", "faceOffWinPercentage"): game["data"]["teams"][team_index]["faceOffWinPercentage"],
                    key.replace("TEMP", "blocked"): game["data"]["teams"][team_index]["blocked"],
                    key.replace("TEMP", "takeaways"): game["data"]["teams"][team_index]["takeaways"],
                    key.replace("TEMP", "giveaways"): game["data"]["teams"][team_index]["giveaways"],
                    key.replace("TEMP", "hits"): game["data"]["teams"][team_index]["hits"],
                    key.replace("TEMP", "isHome"): int(str(game["teams"]["home"]) == str(team_id)),
                    key.replace("TEMP", "gameType"): int(game["game_type_num"]),

                    key.replace("TEMP", "GoalsPerGame"): game["data"]["teams"][team_index]["GoalsPerGame"],
                    key.replace("TEMP", "goalsAgainstPerGame"): game["data"]["teams"][team_index]["goalsAgainstPerGame"],
                    key.replace("TEMP", "shotsPerGame"): game["data"]["teams"][team_index]["shotsPerGame"],
                    key.replace("TEMP", "shotsAgainstPerGame"): game["data"]["teams"][team_index]["shotsAgainstPerGame"],
                }

    print(team_id)
    print(game["gamePk"])
    print(game["data"]["teams"])
    print(key)
    print(game)
    raise("???")


def add_stat_in_games(all_games):
    for i in range(len(all_games)):
        for team_index in all_games[i]["data"]["teams"]:
            other_team_index = list(all_games[i]["data"]["teams"].keys())[0] if \
                list(all_games[i]["data"]["teams"].keys())[0] != team_index else list(all_games[i]["data"]["teams"].keys())[1]
            if i == 0:
                all_games[i]["data"]["teams"][team_index]["GoalsPerGame"] = all_games[i]["data"]["teams"][team_index]["goals"]
                all_games[i]["data"]["teams"][team_index]["goalsAgainstPerGame"] = all_games[i]["data"]["teams"][other_team_index]["goals"]
                all_games[i]["data"]["teams"][team_index]["shotsPerGame"] = all_games[i]["data"]["teams"][team_index]["shots"]
                all_games[i]["data"]["teams"][team_index]["shotsAgainstPerGame"] = all_games[i]["data"]["teams"][other_team_index]["shots"]
            else:
                if "goals" in all_games[i]["data"]["teams"][team_index]:
                    all_games[i]["data"]["teams"][team_index]["GoalsPerGame"] = (all_games[i-1]["data"]["teams"][team_index]["GoalsPerGame"]*i + all_games[i]["data"]["teams"][team_index]["goals"]) / (i + 1)
                    all_games[i]["data"]["teams"][team_index]["goalsAgainstPerGame"] = (all_games[i-1]["data"]["teams"][team_index]["goalsAgainstPerGame"]*i + all_games[i]["data"]["teams"][other_team_index]["goals"]) / (i + 1)
                    all_games[i]["data"]["teams"][team_index]["shotsPerGame"] = (all_games[i-1]["data"]["teams"][team_index]["shotsPerGame"]*i + all_games[i]["data"]["teams"][team_index]["shots"]) / (i + 1)
                    all_games[i]["data"]["teams"][team_index]["shotsAgainstPerGame"] = (all_games[i-1]["data"]["teams"][team_index]["shotsAgainstPerGame"]*i + all_games[i]["data"]["teams"][other_team_index]["shots"]) / (i + 1)

    return all_games



def generate_deafult():
    default_data = {
        "gamePk": None,
        "date": None,
        "game_type": None,
        "isHome": None,
        "opp": None,
        "shots_this_game_O3.5": None,
        "shots_this_game_O2.5": None,
        "shots_this_game_O1.5": None,
        "shots_this_game_U1.5": None,
        "shots_this_game_U2.5": None,
        "shots_this_game_U3.5": None,
        "shots_this_game_total": None,
    }



    for i in range(1, Settings.num_of_games_back_to_track + 1):
        default_data["player-stat-{}-games-back-{}".format("current_age", i)] = None
        default_data["player-stat-{}-games-back-{}".format("rosterStatus", i)] = None
        default_data["player-stat-{}-games-back-{}".format("primaryPositioncode", i)] = None
        default_data["player-stat-{}-games-back-{}".format("code", i)] = None
        default_data["player-stat-{}-games-back-{}".format("timeOnIce", i)] = None
        default_data["player-stat-{}-games-back-{}".format("assists", i)] = None
        default_data["player-stat-{}-games-back-{}".format("goals", i)] = None
        default_data["player-stat-{}-games-back-{}".format("shots", i)] = None
        default_data["player-stat-{}-games-back-{}".format("hits", i)] = None
        default_data["player-stat-{}-games-back-{}".format("powerPlayGoals", i)] = None
        default_data["player-stat-{}-games-back-{}".format("powerPlayAssists", i)] = None
        default_data["player-stat-{}-games-back-{}".format("penaltyMinutes", i)] = None
        default_data["player-stat-{}-games-back-{}".format("faceOffWins", i)] = None
        default_data["player-stat-{}-games-back-{}".format("faceoffTaken", i)] = None
        default_data["player-stat-{}-games-back-{}".format("takeaways", i)] = None
        default_data["player-stat-{}-games-back-{}".format("giveaways", i)] = None
        default_data["player-stat-{}-games-back-{}".format("shortHandedGoals", i)] = None
        default_data["player-stat-{}-games-back-{}".format("shortHandedAssists", i)] = None
        default_data["player-stat-{}-games-back-{}".format("blocked", i)] = None
        default_data["player-stat-{}-games-back-{}".format("plusMinus", i)] = None
        default_data["player-stat-{}-games-back-{}".format("evenTimeOnIce", i)] = None
        default_data["player-stat-{}-games-back-{}".format("powerPlayTimeOnIce", i)] = None
        default_data["player-stat-{}-games-back-{}".format("shortHandedTimeOnIce", i)] = None
        default_data["player-stat-{}-games-back-{}".format("isHome", i)] = None
        default_data["player-stat-{}-games-back-{}".format("gameType", i)] = None



    for team in ("player_team", "opp_team"):
        for i in range(1, Settings.num_of_games_back_to_track + 1):
            default_data["{}-stat-{}-games-back-{}".format(team, "player_played", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "wins", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "losses", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "ot", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "score", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "goals", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "pim", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "shots", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "powerPlayPercentage", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "powerPlayGoals", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "powerPlayOpportunities", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "faceOffWinPercentage", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "blocked", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "takeaways", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "giveaways", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "hits", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "isHome", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "gameType", i)] = None

            default_data["{}-stat-{}-games-back-{}".format(team, "GoalsPerGame", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "goalsAgainstPerGame", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "shotsPerGame", i)] = None
            default_data["{}-stat-{}-games-back-{}".format(team, "shotsAgainstPerGame", i)] = None



    for taa in ("home", "away", "avr"):
        default_data["player-stat-{}-last-{}-game".format("current_age", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("rosterStatus", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("primaryPositioncode", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("code", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("timeOnIce", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("assists", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("goals", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("shots", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("hits", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("powerPlayGoals", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("powerPlayAssists", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("penaltyMinutes", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("faceOffWins", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("faceoffTaken", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("takeaways", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("giveaways", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("shortHandedGoals", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("shortHandedAssists", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("blocked", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("plusMinus", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("evenTimeOnIce", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("powerPlayTimeOnIce", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("shortHandedTimeOnIce", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("isHome", taa)] = None
        default_data["player-stat-{}-last-{}-game".format("gameType", taa)] = None

        for team in ("player_team", "opp_team"):
            default_data["{}-stat-{}-last-{}-game".format(team, "player_played", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "wins", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "losses", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "ot", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "score", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "goals", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "pim", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "shots", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "powerPlayPercentage", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "powerPlayGoals", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "powerPlayOpportunities", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "faceOffWinPercentage", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "blocked", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "takeaways", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "giveaways", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "hits", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "isHome", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "gameType", taa)] = None

            default_data["{}-stat-{}-last-{}-game".format(team, "GoalsPerGame", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "goalsAgainstPerGame", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "shotsPerGame", taa)] = None
            default_data["{}-stat-{}-last-{}-game".format(team, "shotsAgainstPerGame", taa)] = None


    return default_data