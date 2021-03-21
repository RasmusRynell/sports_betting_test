import Settings
from tqdm import tqdm
from datetime import datetime as dt
from datetime import timedelta

class games:
    def __init__(self):
        self.api = Settings.api
        self.games = self.get_all_games(Settings.num_of_seasons_to_go_back)
        self.player_ids = self.get_all_player_ids(Settings.all_seasons[0]) # This current season
        self.team_ids = self.get_team_ids()


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
                raise Exception("ERROR: The team \"{}\" has more than one id, the player has been transfered mid season! \n ".format(name) + str(self.player_ids[name.lower()]))
            return self.player_ids[name.lower()][0]
        else:
            if(name.lower() in Settings.player_nicknames):
                return self.get_player_id(Settings.player_nicknames[name.lower()])
            raise Exception("ERROR: Cannot convert player \"{}\" to an id, it's not in the database!".format(name))


    def get_all_games_in_season(self, season):
        date = dt(int(season[:4]), 8, 1)
        end_date = dt(date.year + 1, 7, 15)
        done = {}
        while date != end_date:
            res = self.api.send_request("/schedule?date={}".format(str(date.date())))
            if "message" not in res and res["totalGames"] > 0:
                for game in res["dates"][0]["games"]:
                    done[game["gamePk"]] = {}
                    done[game["gamePk"]]["date"] = res["dates"][0]["date"]
                    done[game["gamePk"]]["game_type"] = game["gameType"]
                    done[game["gamePk"]]["teams"] = game["teams"]
            date += timedelta(days=1)
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


    def get_game_from_date(self, player_id, date, ply_team_id, opp_team_id, back_one=False):
        res = self.api.send_request("/schedule?date={}".format(date))

        for game in res["dates"][0]["games"]:
            if (str(game["teams"]["home"]["team"]["id"]) == str(ply_team_id) and \
                str(game["teams"]["away"]["team"]["id"]) == str(opp_team_id)):
                return (game["gamePk"], str(ply_team_id), str(opp_team_id))
                
            if (str(game["teams"]["home"]["team"]["id"]) == str(opp_team_id) and \
            str(game["teams"]["away"]["team"]["id"]) == str(ply_team_id)):
                return (game["gamePk"], str(opp_team_id),str(ply_team_id))

        if not back_one:
            new_date = dt.fromisoformat(date) - timedelta(days=1)
            return self.get_game_from_date(player_id, str(new_date.date()), ply_team_id, opp_team_id, True)
            
        print("Player: " + str(player_id))
        print("Date: " + str(date))
        print("Ply team id: " + str(ply_team_id))
        print("Opp team_id: " + str(opp_team_id))
        print("WE MIGHT NEED TO GO BACK 1 MORE DAY!!")
        raise("WRONG!!")


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


'''
[[['brock boeser', 'van canucks', 'ott senators', 'away'], 
    ['2.5', '1.83', '1.83', 'Brock Boeser', 'VAN Canucks', 'OTT Senators', 'Away', 'Tor 18 mar 00:08']], 
    [['bo horvat', 'van canucks', 'ott senators', 'away'], ['2.5', '2.00', '1.71', 'Bo Horvat', 'VAN Canucks', 'OTT Senators', 'Away', 'Tor 18 mar 00:08']], [['j.t. miller', 'van canucks', 'ott senators', 'away'], ['1.5', '1.52', '2.40', 'J.T. Miller', 'VAN Canucks', 'OTT Senators', 'Away', 'Tor 18 mar 00:08']], [['tanner pearson', 'van canucks', 'ott senators', 'away'], ['2.5', '2.00', '1.71', 'Tanner Pearson', 'VAN Canucks', 'OTT Senators', 'Away', 'Tor 18 mar 00:08']], [['thomas chabot', 'ott senators', 'van canucks', 'home'], ['2.5', '2.00', '1.71', 'Thomas Chabot', 'OTT Senators', 'VAN Canucks', 'Home', 'Tor 18 mar 00:08']], [['evgenii dadonov', 'ott senators', 'van canucks', 'home'], ['2.5', '2.30', '1.55', 'Evgenii Dadonov', 'OTT Senators', 'VAN Canucks', 'Home', 'Tor 18 mar 00:08']], [['brady tkachuk', 'ott senators', 'van canucks', 'home'], ['3.5', '1.71', '2.00', 'Brady Tkachuk', 'OTT Senators', 'VAN Canucks', 'Home', 'Tor 18 mar 00:08']], [['sean couturier', 'phi flyers', 'ny rangers', 'away'], ['2.5', '2.00', '1.71', 'Sean Couturier', 'PHI Flyers', 'NY Rangers', 'Away', 'Tor 18 mar 00:38']], [['joel farabee', 'phi flyers', 'ny rangers', 'away'], ['2.5', '2.20', '1.62', 'Joel Farabee', 'PHI Flyers', 'NY Rangers', 'Away', 'Tor 18 mar 00:38']], [['claude giroux', 'phi flyers', 'ny rangers', 'away'], ['2.5', '2.10', '1.66', 'Claude Giroux', 'PHI Flyers', 'NY Rangers', 'Away', 'Tor 18 mar 00:38']], [['kevin hayes', 'phi flyers', 'ny rangers', 'away'], ['2.5', '2.20', '1.62', 'Kevin Hayes', 'PHI Flyers', 'NY Rangers', 'Away', 'Tor 18 mar 00:38']], [['james van riemsdyk', 'phi flyers', 'ny rangers', 'away'], ['2.5', '2.10', '1.66', 'James van Riemsdyk', 'PHI Flyers', 'NY Rangers', 'Away', 'Tor 18 mar 00:38']], [['jakub voracek', 'phi flyers', 'ny rangers', 'away'], ['1.5', '1.52', '2.40', 'Jakub Voracek', 'PHI Flyers', 'NY Rangers', 'Away', 'Tor 18 mar 00:38']], [['artemi panarin', 'ny rangers', 'phi flyers', 'home'], ['2.5', '1.76', '1.90', 'Artemi Panarin', 'NY Rangers', 'PHI Flyers', 'Home', 'Tor 18 mar 00:38']], [['mika zibanejad', 'ny rangers', 'phi flyers', 'home'], ['2.5', '1.57', '2.25', 'Mika Zibanejad', 'NY Rangers', 'PHI Flyers', 'Home', 'Tor 18 mar 00:38']], [['josh anderson', 'mon canadiens', 'win jets', 'away'], ['2.5', '1.86', '1.80', 'Josh Anderson', 'MON Canadiens', 'WIN Jets', 'Away', 'Tor 18 mar 02:08']], [['brendan gallagher', 'mon canadiens', 'win jets', 'away'], ['3.5', '2.20', '1.62', 'Brendan Gallagher', 'MON Canadiens', 'WIN Jets', 'Away', 'Tor 18 mar 02:08']], [['jeff petry', 'mon canadiens', 'win jets', 'away'], ['2.5', '2.25', '1.57', 'Jeff Petry', 'MON Canadiens', 'WIN Jets', 'Away', 'Tor 18 mar 02:08']], [['nicholas suzuki', 'mon canadiens', 'win jets', 'away'], ['1.5', '1.62', '2.20', 'Nicholas Suzuki', 'MON Canadiens', 'WIN Jets', 'Away', 'Tor 18 mar 02:08']], [['tyler toffoli', 'mon canadiens', 'win jets', 'away'], ['2.5', '1.71', '2.00', 'Tyler Toffoli', 'MON Canadiens', 'WIN Jets', 'Away', 'Tor 18 mar 02:08']], [['shea weber', 'mon canadiens', 'win jets', 'away'], ['2.5', '2.40', '1.52', 'Shea Weber', 'MON Canadiens', 'WIN Jets', 'Away', 'Tor 18 mar 02:08']], [['kyle connor', 'win jets', 'mon canadiens', 'home'], ['2.5', '1.71', '2.00', 'Kyle Connor', 'WIN Jets', 'MON Canadiens', 'Home', 'Tor 18 mar 02:08']], [['pierre-luc dubois', 'win jets', 'mon canadiens', 'home'], ['1.5', '1.62', '2.20', 'Pierre-Luc Dubois', 'WIN Jets', 'MON Canadiens', 'Home', 'Tor 18 mar 02:08']], [['nikolaj ehlers', 'win jets', 'mon canadiens', 'home'], ['2.5', '1.76', '1.90', 'Nikolaj Ehlers', 'WIN Jets', 'MON Canadiens', 'Home', 'Tor 18 mar 02:08']], [['neal pionk', 'win jets', 'mon canadiens', 'home'], ['1.5', '1.66', '2.10', 'Neal Pionk', 'WIN Jets', 'MON Canadiens', 'Home', 'Tor 18 mar 02:08']], [['mark scheifele', 'win jets', 'mon canadiens', 'home'], ['2.5', '2.30', '1.55', 'Mark Scheifele', 'WIN Jets', 'MON Canadiens', 'Home', 'Tor 18 mar 02:08']], [['blake wheeler', 'win jets', 'mon canadiens', 'home'], ['2.5', '2.30', '1.55', 'Blake Wheeler', 'WIN Jets', 'MON Canadiens', 'Home', 'Tor 18 mar 02:08']], [['leon draisaitl', 'edm oilers', 'cal flames', 'away'], ['2.5', '1.66', '2.10', 'Leon Draisaitl', 'EDM Oilers', 'CAL Flames', 'Away', 'Tor 18 mar 03:08']], [['connor mcdavid', 'edm oilers', 'cal flames', 'away'], ['3.5', '1.86', '1.80', 'Connor McDavid', 'EDM Oilers', 'CAL Flames', 'Away', 'Tor 18 mar 03:08']], [['ryan nugent-hopkins', 'edm oilers', 'cal flames', 'away'], ['2.5', '1.76', '1.90', 'Ryan Nugent-Hopkins', 'EDM Oilers', 'CAL Flames', 'Away', 'Tor 18 mar 03:08']], [['mikael backlund', 'cal flames', 'edm oilers', 'home'], ['2.5', '2.50', '1.50', 'Mikael Backlund', 'CAL Flames', 'EDM Oilers', 'Home', 'Tor 18 mar 03:08']], [['dillon dube', 'cal flames', 'edm oilers', 'home'], ['1.5', '1.62', '2.20', 'Dillon Dube', 'CAL Flames', 'EDM Oilers', 'Home', 'Tor 18 mar 03:08']], [['johnny gaudreau', 'cal flames', 'edm oilers', 'home'], ['2.5', '2.10', '1.66', 'Johnny Gaudreau', 'CAL Flames', 'EDM Oilers', 'Home', 'Tor 18 mar 03:08']], [['mark giordano', 'cal flames', 'edm oilers', 'home'], ['1.5', '1.50', '2.50', 'Mark Giordano', 'CAL Flames', 'EDM Oilers', 'Home', 'Tor 18 mar 03:08']], [['elias lindholm', 'cal flames', 'edm oilers', 'home'], ['2.5', '2.40', '1.52', 'Elias Lindholm', 'CAL Flames', 'EDM Oilers', 'Home', 'Tor 18 mar 03:08']], [['sean monahan', 'cal flames', 'edm oilers', 'home'], ['2.5', '2.20', '1.62', 'Sean Monahan', 'CAL Flames', 'EDM Oilers', 'Home', 'Tor 18 mar 03:08']], [['brent burns', 'sj sharks', 'vgs golden knights', 'away'], ['2.5', '1.66', '2.10', 'Brent Burns', 'SJ Sharks', 'VGS Golden Knights', 'Away', 'Tor 18 mar 03:08']], [['logan couture', 'sj sharks', 'vgs golden knights', 'away'], ['2.5', '2.20', '1.62', 'Logan Couture', 'SJ Sharks', 'VGS Golden Knights', 'Away', 'Tor 18 mar 03:08']], [['tomas hertl', 'sj sharks', 'vgs golden knights', 'away'], ['1.5', '1.52', '2.40', 'Tomas Hertl', 'SJ Sharks', 'VGS Golden Knights', 'Away', 'Tor 18 mar 03:08']], [['evander kane', 'sj sharks', 'vgs golden knights', 'away'], ['2.5', '1.55', '2.30', 'Evander Kane', 'SJ Sharks', 'VGS Golden Knights', 'Away', 'Tor 18 mar 03:08']], [['erik karlsson', 'sj sharks', 'vgs golden knights', 'away'], ['1.5', '1.62', '2.20', 'Erik Karlsson', 'SJ Sharks', 'VGS Golden Knights', 'Away', 'Tor 18 mar 03:08']], [['kevin labanc', 'sj sharks', 'vgs golden knights', 'away'], ['2.5', '2.40', '1.52', 'Kevin Labanc', 'SJ Sharks', 'VGS Golden Knights', 'Away', 'Tor 18 mar 03:08']], [['timo meier', 'sj sharks', 'vgs golden knights', 'away'], ['2.5', '1.71', '2.00', 'Timo Meier', 'SJ Sharks', 'VGS Golden Knights', 'Away', 'Tor 18 mar 03:08']], [['william karlsson', 'vgs golden knights', 'sj sharks', 'home'], ['1.5', '1.66', '2.10', 'William Karlsson', 'VGS Golden Knights', 'SJ Sharks', 'Home', 'Tor 18 mar 03:08']], [['jonathan marchessault', 'vgs golden knights', 'sj sharks', 'home'], ['2.5', '1.71', '2.00', 'Jonathan Marchessault', 'VGS Golden Knights', 'SJ Sharks', 'Home', 'Tor 18 mar 03:08']], [['max pacioretty', 'vgs golden knights', 'sj sharks', 'home'], ['3.5', '1.71', '2.00', 'Max Pacioretty', 'VGS Golden Knights', 'SJ Sharks', 'Home', 'Tor 18 mar 03:08']], [['mark stone', 'vgs golden knights', 'sj sharks', 'home'], ['2.5', '2.40', '1.52', 'Mark Stone', 'VGS Golden Knights', 'SJ Sharks', 'Home', 'Tor 18 mar 03:08']], [['justin faulk', 'stl blues', 'la kings', 'away'], ['1.5', '1.62', '2.20', 'Justin Faulk', 'STL Blues', 'LA Kings', 'Away', 'Tor 18 mar 03:08']], [['torey krug', 'stl blues', 'la kings', 'away'], ['2.5', '2.20', '1.62', 'Torey Krug', 'STL Blues', 'LA Kings', 'Away', 'Tor 18 mar 03:08']], [['david perron', 'stl blues', 'la kings', 'away'], ['2.5', '2.00', '1.71', 'David Perron', 'STL Blues', 'LA Kings', 'Away', 'Tor 18 mar 03:08']], [['brayden schenn', 'stl blues', 'la kings', 'away'], ['2.5', '2.20', '1.62', 'Brayden Schenn', 'STL Blues', 'LA Kings', 'Away', 'Tor 18 mar 03:08']], [['vladimir tarasenko', 'stl blues']]]
'''