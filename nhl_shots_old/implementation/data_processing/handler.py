import Settings
from tqdm import tqdm
from datetime import datetime as dt
from datetime import timedelta


def is_player_in_team(self, player_name, team_name):
    team_id = self.get_team_id(team_name)
    player_id = self.get_player_id(player_name)

    res = self.api.send_request("/teams/{}/roster".format(team_id))

    for player in res["roster"]:
        if str(player["person"]["id"]) == str(player_id):
            return True
    return False



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
def get_team_id(self, name):
    if (name.lower() in self.team_ids):
        if len(self.team_ids[name.lower()]) > 1:
            raise Exception("ERROR: The team \"{}\" has more than one id! \n ".format(name) + str(self.team_ids[name.lower()]))
        return self.team_ids[name.lower()][0]
    elif (name.lower() in Settings.teams_translate):
        return self.get_team_id(Settings.teams_translate[name.lower()])
    else:
        raise Exception("ERROR: Cannot convert team \"{}\" to an id, it's not in the database!".format(name))


def get_all_player_ids(self, season):
    json_response = self.api.send_request("/teams?expand=team.roster&site=en_nhlNR&season={}".format(season), True)
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
def get_player_id(self, name):
    if (name.lower() in self.player_ids):
        if len(self.player_ids[name.lower()]) > 1:
            raise Exception("ERROR: The player \"{}\" has more than one id, the player has been transfered mid season! \n ".format(name) + str(self.player_ids[name.lower()]))
        return self.player_ids[name.lower()][0]
    else:
        if(name.lower() in Settings.player_nicknames):
            return self.get_player_id(Settings.player_nicknames[name.lower()])
        raise Exception("ERROR: Cannot convert player \"{}\" to an id, it's not in the database!".format(name))


def create_database(season):
    date = dt(int(season[:4]), 8, 1)
    end_date = dt(date.year + 1, 7, 15)
    done = []


    while date != end_date:
        res = self.api.send_request("/schedule?date={}".format(str(date.date())))
        if "message" not in res and res["totalGames"] > 0:
            for game in res["dates"][0]["games"]:
                done.append({})
                done[-1]["gamePk"] = game["gamePk"]
                done[-1]["date"] = game["gameDate"]
                done[-1]["game_type"] = game["gameType"]
                done[-1]["teams"] = game["teams"]
        date += timedelta(days=1)

    done = sorted(done, key=lambda date: Settings.string_to_standard_datetime(date["date"]))

    for game in done:
        # Check if played
        # Add to database

    return done


def get_all_games(self, seasons_back):
    done = {}
    # Loop though num of seasons to get datapoints from
    for season_index in tqdm(range(0, seasons_back)):
        done[Settings.all_seasons[season_index]] = self.get_all_games_in_season(Settings.all_seasons[season_index])
    return done


def get_player_games_in_season(self, id, season):
    res = []
    response_json = self.api.send_request("/people/{}/stats?stats=gameLog&season={}".format(id, season))
    split = response_json["stats"][0]["splits"]
    for game in split:
        res.append((game['game']['gamePk'], game['date']))
    return res


def get_stats_from_x_games_ago(self, player_id, game_id, games_ago):
    stats = {}

    res = self.api.send_request("/game/{}/boxscore".format(game_id))
    for team in res["teams"]:
        for temp_player_id in res["teams"][team]["players"]:
            if str(temp_player_id)[2:] == str(player_id):
                stats["assists-{}-games_back".format(games_ago)] = res["teams"][team]["players"][temp_player_id]["stats"]["skaterStats"]["assists"]
                stats["goals-{}-games_back".format(games_ago)] = res["teams"][team]["players"][temp_player_id]["stats"]["skaterStats"]["goals"]
                stats["shots-{}-games_back".format(games_ago)] = res["teams"][team]["players"][temp_player_id]["stats"]["skaterStats"]["shots"]

                stats["penaltyMinutes-{}-games_back".format(games_ago)] = res["teams"][team]["players"][temp_player_id]["stats"]["skaterStats"]["penaltyMinutes"]

                stat = res["teams"][team]["players"][temp_player_id]["stats"]["skaterStats"]["evenTimeOnIce"]
                stats["evenTimeOnIce-{}-games_back".format(games_ago)] = int(stat.split(":")[0])*60 + int(stat.split(":")[1])

                stat = res["teams"][team]["players"][temp_player_id]["stats"]["skaterStats"]["powerPlayTimeOnIce"]
                stats["powerPlayTimeOnIce-{}-games_back".format(games_ago)] = int(stat.split(":")[0])*60 + int(stat.split(":")[1])
                
                stat = res["teams"][team]["players"][temp_player_id]["stats"]["skaterStats"]["timeOnIce"]
                stats["timeOnIce-{}-games_back".format(games_ago)] = int(stat.split(":")[0])*60 + int(stat.split(":")[1])

    return stats


def calculate_player_complex_stats(self, game, all_games, player_id):
    stats = {}
    for i in range (1, Settings.num_of_games_back_to_track + 1):
        stats["assists-{}-games_back".format(i)] = 0
        stats["evenTimeOnIce-{}-games_back".format(i)] = 0
        stats["goals-{}-games_back".format(i)] = 0
        stats["penaltyMinutes-{}-games_back".format(i)] = 0
        stats["powerPlayTimeOnIce-{}-games_back".format(i)] = 0
        stats["shots-{}-games_back".format(i)] = 0
        stats["timeOnIce-{}-games_back".format(i)] = 0
    

    date = dt.fromisoformat(str(game[1]))
    index = 0
    for i in range(0, len(all_games)):
        if str(date.date()) == all_games[i][1]:
            index = i
            break

    for i in range (1, Settings.num_of_games_back_to_track + 1):
        if (i+index >= len(all_games)):
            break
        stats.update(self.get_stats_from_x_games_ago(player_id, all_games[index + i][0], i))

    return stats


def convert_date_to_season_index(self, date):
    date = dt.fromisoformat(str(date))
    date_middle = dt.fromisoformat(str(date)[:4] + "-10-" + "01")

    if date < date_middle:
        return str(date.year-1) + str(date.year)
    return str(date.year) + str(date.year+1)


def get_stats_from_x_games_ago_team(self, team_id, game_id, games_ago, type_of_team):
    stats = {}

    res = self.api.send_request("/game/{}/boxscore".format(game_id))
    for team in res["teams"]:
        if res["teams"][team]["team"]["id"] == team_id:
            stats["home-{}-{}-games_back".format(type_of_team, games_ago)] = int(team == "home")
            #stats["goals-{}-{}-games_back".format(type_of_team, games_ago)] = res["teams"][team]["teamStats"]["teamSkaterStats"]["goals"]
            stats["pim-{}-{}-games_back".format(type_of_team, games_ago)] = res["teams"][team]["teamStats"]["teamSkaterStats"]["pim"]
            stats["takeaways-{}-{}-games_back".format(type_of_team, games_ago)] = res["teams"][team]["teamStats"]["teamSkaterStats"]["takeaways"]
            stats["giveaways-{}-{}-games_back".format(type_of_team, games_ago)] = res["teams"][team]["teamStats"]["teamSkaterStats"]["giveaways"]
            stats["hits-{}-{}-games_back".format(type_of_team, games_ago)] = res["teams"][team]["teamStats"]["teamSkaterStats"]["hits"]
            stats["game_type-{}-{}-games_back".format(type_of_team, games_ago)] = str(game_id)[4:6]
            
            if type_of_team == "ply":
                if "shots" in res["teams"][team]["teamStats"]["teamSkaterStats"]:
                    stats["shots-{}-{}-games_back".format(type_of_team, games_ago)] = res["teams"][team]["teamStats"]["teamSkaterStats"]["shots"]
            elif type_of_team == "opp":
                stats["blocked-{}-{}-games_back".format(type_of_team, games_ago)] = res["teams"][team]["teamStats"]["teamSkaterStats"]["blocked"]
    return stats


def calculate_teams_complex_stats(self, game, all_games, ids):
    stats = {}
    for i in range (1, Settings.num_of_games_back_to_track + 1):
        for v in ("ply", "opp"):
            stats["home-{}-{}-games_back".format(v, i)] = 0
            #stats["goals-{}-{}-games_back".format(v, i)] = 0
            stats["pim-{}-{}-games_back".format(v, i)] = 0
            stats["takeaways-{}-{}-games_back".format(v, i)] = 0
            stats["giveaways-{}-{}-games_back".format(v, i)] = 0
            stats["hits-{}-{}-games_back".format(v, i)] = 0
            stats["game_type-{}-{}-games_back".format(v, i)] = 0
            
            if v == "ply":
                stats["shots-{}-{}-games_back".format(v, i)] = 0
            elif v == "opp":
                stats["blocked-{}-{}-games_back".format(v, i)] = 0


    ### Get all games for team
    season_index = self.convert_date_to_season_index(game[1])

    all_games_ply_team = []
    all_games_opp_team = []



    for game_id in self.games[season_index]:
        if self.games[season_index][game_id]["teams"]["home"]["team"]["id"] == ids[1] or\
            self.games[season_index][game_id]["teams"]["away"]["team"]["id"] == ids[1]:
            all_games_ply_team.append(game_id)
        elif self.games[season_index][game_id]["teams"]["home"]["team"]["id"] == ids[2] or\
            self.games[season_index][game_id]["teams"]["away"]["team"]["id"] == ids[2]:
            all_games_opp_team.append(game_id)
    ###

    date = dt.fromisoformat(str(game[1]))
    index = 0
    for i in range(0, len(all_games)):
        if str(date.date()) == all_games[i][1]:
            index = i
            break

    for i in range (1, Settings.num_of_games_back_to_track + 1):
        if (i+index >= len(all_games_ply_team)):
            break
        # Get players teams stats
        stats.update(self.get_stats_from_x_games_ago_team(ids[1], all_games_ply_team[index + i], i, "ply"))



    for i in range (1, Settings.num_of_games_back_to_track + 1):
        if (i+index >= len(all_games_opp_team)):
            break
        # Get other teams stats
        stats.update(self.get_stats_from_x_games_ago_team(ids[2], all_games_opp_team[index + i], i, "opp"))

    return stats


def create_basic_stats(self, game, player_id):
    res = self.api.send_request("/people/{}".format(player_id))

    done = {"primary_position": res["people"][0]["primaryPosition"]["code"]}
    game_date = dt.strptime(game[1], "%Y-%m-%d")
    born = dt.strptime(res["people"][0]["birthDate"], "%Y-%m-%d")
    done["days_old"] = (game_date - born).days

    return done


def calculate_stats(self, game, all_games, ids):
    data = {}
    data.update(self.calculate_answers(game[0], ids))
    data.update(self.create_basic_stats(game, ids[0]))
    data.update(self.calculate_player_complex_stats(game, all_games, ids[0]))
    data.update(self.calculate_teams_complex_stats(game, all_games, ids))
    return data


def get_game_from_date(self, player_id, date, home_team_id, away_team_id):
    date = dt.fromisoformat(date)
    new_date_down = (date) - timedelta(days=1)
    new_date_up = (date) + timedelta(days=1)

    res = self.api.send_request("/schedule?date={}".format(str(date.date())))
    res_down = self.api.send_request("/schedule?date={}".format(str(new_date_down.date())))
    res_up = self.api.send_request("/schedule?date={}".format(str(new_date_up.date())))

    res_ans = ""
    for game in res["dates"][0]["games"]:
        if (str(game["teams"]["home"]["team"]["id"]) == str(home_team_id) and \
            str(game["teams"]["away"]["team"]["id"]) == str(away_team_id)):
            if str(game["gameDate"][:10]) == str(date.date()) or\
                str(game["gameDate"][:10]) == str(new_date_down.date()) or\
                str(game["gameDate"][:10]) == str(new_date_up.date()):
                    res_ans = (game["gamePk"], game["gameDate"][:10])

    res_ans_down = ""
    for game in res_down["dates"][0]["games"]:
        if (str(game["teams"]["home"]["team"]["id"]) == str(home_team_id) and \
            str(game["teams"]["away"]["team"]["id"]) == str(away_team_id)):
            if str(game["gameDate"][:10]) == str(date.date()) or\
                str(game["gameDate"][:10]) == str(new_date_down.date()) or\
                str(game["gameDate"][:10]) == str(new_date_up.date()):
                    res_ans_down = (game["gamePk"], game["gameDate"][:10])

    res_ans_up = ""
    for game in res_up["dates"][0]["games"]:
        if (str(game["teams"]["home"]["team"]["id"]) == str(home_team_id) and \
            str(game["teams"]["away"]["team"]["id"]) == str(away_team_id)):
            if str(game["gameDate"][:10]) == str(date.date()) or\
                str(game["gameDate"][:10]) == str(new_date_down.date()) or\
                str(game["gameDate"][:10]) == str(new_date_up.date()):
                    res_ans_up = (game["gamePk"], game["gameDate"][:10])

    if not res_ans and not res_ans_down and not res_ans_up:
        print("Player: " + str(player_id))
        print("Date: " + str(date.date()))
        print("home_team_id: " + str(home_team_id))
        print("away_team_id: " + str(away_team_id))
        raise("WRONG!!")
    
    return [x for x in [res_ans, res_ans_down, res_ans_up] if x != ""]


def get_stats_for_player(self, bet):
    all_matches_done = []
    player_id = self.get_player_id(bet["name"])
    ply_team_id = self.get_team_id(bet["ply_team_name"])
    opp_team_id = self.get_team_id(bet["opp_team_name"])
    ids = (player_id, ply_team_id, opp_team_id)
    print("player id: " + str(player_id))
    print("date: " + str(bet["date"]))

    (up_to_game, home_team, away_team) = self.get_game_from_date(player_id, bet["date"], ply_team_id, opp_team_id)

    for season_index in tqdm(range(0, Settings.num_of_seasons_to_go_back)):
        all_games = self.get_player_games_in_season(player_id, Settings.all_seasons[season_index])
        for game in all_games:
            info = {"game_id": game[0], "game_date": game[1]}
            info.update(self.calculate_stats(game, all_games, ids))
            all_matches_done.append(info)

    return (list(all_matches_done[0].keys()), all_matches_done)



def calculate_answers(self, game_id, ids):
    (player_id, ply_team_id, opp_team_id) = ids
    response_json = self.api.send_request("/game/{}/boxscore".format(game_id))
    for team in response_json["teams"]:
        for player in response_json["teams"][team]["players"]:
            if response_json["teams"][team]["players"][player]["person"]["id"] == player_id:
                return {
                    "is_home_game": int (team == "home"),
                    "shots_this_game_O3.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] > 3.5),
                    "shots_this_game_O2.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] > 2.5),
                    "shots_this_game_O1.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] > 1.5),
                    "shots_this_game_U1.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] < 1.5),
                    "shots_this_game_U2.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] < 2.5),
                    "shots_this_game_U3.5": int (response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"] < 3.5),
                    "shots_this_game_total": response_json["teams"][team]["players"][player]["stats"]["skaterStats"]["shots"]
                }
    return {}
