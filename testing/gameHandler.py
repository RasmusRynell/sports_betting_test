import traceback
import gevent.monkey
gevent.monkey.patch_all(thread=False, select=False)
from models import *
import requests
import grequests
import datetime
import json

def convert_string_to_time(timeS):
    arr = timeS.split(":")
    h = 0
    m = int(arr[0])
    s = int(arr[1])
    while m > 59:
        h += 1
        m -= 60
    return datetime.time(h, m, s)


def add_game_to_db(session, game):
    try:
        newGame = Game()

        newGame.gamePk = game["gamePk"]
        newGame.gameType = game["gameType"] if "gameType" in game else None
        newGame.season = game["season"] if "season" in game else None
        newGame.gameDate = datetime.datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ") if "gameDate" in game else None
        newGame.abstractGameState = game["status"]["abstractGameState"] if "status" in game and "abstractGameState" in game["status"] else None
        newGame.codedGameState = game["status"]["codedGameState"] if "status" in game and "codedGameState" in game["status"] else None
        newGame.detailedState = game["status"]["detailedState"] if "status" in game and "detailedState" in game["status"] else None
        newGame.statusCode = game["status"]["statusCode"] if "status" in game and "statusCode" in game["status"] else None
        newGame.startTimeTBD = game["status"]["startTimeTBD"] if "status" in game and "startTimeTBD" in game["status"] else None
        newGame.homeTeamId = game["teams"]["home"]["team"]["id"]
        newGame.awayTeamId = game["teams"]["away"]["team"]["id"]

        session.add(newGame)
    except Exception as e:
        print(e)
        traceback.print_exc()


def fill_all_games_from_season(session, season):
    def hook_factory(*factory_args, **factory_kwargs):
        def add_game_stats_to_db(res, *args, **kwargs):
            try:
                info = factory_kwargs["info"]
                session = info["session"]

                res = res.json()

                for home_or_away in ("home", "away"):
                    # Add team stats
                    teamInfo = res["teams"][home_or_away]
                    resTeamStats = teamInfo["teamStats"]["teamSkaterStats"]

                    newTeamStats = teamStats()

                    newTeamStats.gamePk = info["gamePk"]
                    newTeamStats.teamId = teamInfo["team"]["id"]
                    newTeamStats.goals = resTeamStats["goals"]
                    newTeamStats.pim = resTeamStats["pim"]
                    newTeamStats.shots = resTeamStats["shots"]
                    newTeamStats.powerPlayPercentage = resTeamStats["powerPlayPercentage"]
                    newTeamStats.powerPlayGoals = resTeamStats["powerPlayGoals"]
                    newTeamStats.powerPlayOpportunities = resTeamStats["powerPlayOpportunities"]
                    newTeamStats.faceOffWinPercentage = resTeamStats["faceOffWinPercentage"]
                    newTeamStats.blocked = resTeamStats["blocked"]
                    newTeamStats.takeaways = resTeamStats["takeaways"]
                    newTeamStats.giveaways = resTeamStats["giveaways"]
                    newTeamStats.hits = resTeamStats["hits"]

                    newTeamStats.wins = info["stats"][teamInfo["team"]["id"]]["wins"]
                    newTeamStats.losses = info["stats"][teamInfo["team"]["id"]]["losses"]
                    newTeamStats.ot = info["stats"][teamInfo["team"]["id"]]["ot"]
                    newTeamStats.leagueRecordType = info["stats"][teamInfo["team"]["id"]]["type"]
                    newTeamStats.score = info["stats"][teamInfo["team"]["id"]]["score"]

                    session.add(newTeamStats)

                    # Add all players stats
                    for playerId in teamInfo["players"]:
                        playerInfo = teamInfo["players"][playerId]

                        if playerInfo["position"]["code"] == "G":
                            if "goalieStats" in playerInfo["stats"]:
                                resGoalieStats = playerInfo["stats"]["goalieStats"]

                                newGoalieStats = goalieStats()

                                newGoalieStats.playerId = playerInfo["person"]["id"]
                                newGoalieStats.gamePk = info["gamePk"]
                                newGoalieStats.currentTeamId = playerInfo["person"]["currentTeam"]["id"]
                                newGoalieStats.position = playerInfo["position"]["code"]

                                newGoalieStats.timeOnIce = convert_string_to_time(resGoalieStats["timeOnIce"])
                                newGoalieStats.assists = resGoalieStats["assists"]
                                newGoalieStats.goals = resGoalieStats["goals"]
                                newGoalieStats.pim = resGoalieStats["pim"]
                                newGoalieStats.shots = resGoalieStats["shots"]
                                newGoalieStats.saves = resGoalieStats["saves"]
                                newGoalieStats.powerPlaySaves = resGoalieStats["powerPlaySaves"]
                                newGoalieStats.shortHandedSaves = resGoalieStats["shortHandedSaves"]
                                newGoalieStats.evenSaves = resGoalieStats["evenSaves"]
                                newGoalieStats.shortHandedShotsAgainst = resGoalieStats["shortHandedShotsAgainst"]
                                newGoalieStats.evenShotsAgainst = resGoalieStats["evenShotsAgainst"]
                                newGoalieStats.powerPlayShotsAgainst = resGoalieStats["powerPlayShotsAgainst"]
                                newGoalieStats.decision = resGoalieStats["decision"]
                                newGoalieStats.savePercentage = resGoalieStats["savePercentage"] if "savePercentage" in resGoalieStats else None
                                newGoalieStats.powerPlaySavePercentage = resGoalieStats["powerPlaySavePercentage"] if "powerPlaySavePercentage" in resGoalieStats else None
                                newGoalieStats.evenStrengthSavePercentage = resGoalieStats["evenStrengthSavePercentage"] if "evenStrengthSavePercentage" in resGoalieStats else None

                                session.add(newGoalieStats)

                        else:
                            if "skaterStats" in playerInfo["stats"]:
                                resSkaterStats = playerInfo["stats"]["skaterStats"]

                                newSkaterStats = skaterStats()
                                
                                newSkaterStats.playerId = playerInfo["person"]["id"]
                                newSkaterStats.gamePk = info["gamePk"]
                                newSkaterStats.currentTeamId = playerInfo["person"]["currentTeam"]["id"]
                                newSkaterStats.position = playerInfo["position"]["code"]

                                newSkaterStats.timeOnIce = convert_string_to_time(resSkaterStats["timeOnIce"])
                                newSkaterStats.assists = resSkaterStats["assists"]
                                newSkaterStats.goals = resSkaterStats["goals"]
                                newSkaterStats.shots = resSkaterStats["shots"]
                                newSkaterStats.hits = resSkaterStats["hits"]
                                newSkaterStats.powerPlayGoals = resSkaterStats["powerPlayGoals"]
                                newSkaterStats.powerPlayAssists = resSkaterStats["powerPlayAssists"]
                                newSkaterStats.penaltyMinutes = resSkaterStats["penaltyMinutes"]
                                newSkaterStats.faceOffWins = resSkaterStats["faceOffWins"]
                                newSkaterStats.faceoffTaken = resSkaterStats["faceoffTaken"]
                                newSkaterStats.takeaways = resSkaterStats["takeaways"]
                                newSkaterStats.giveaways = resSkaterStats["giveaways"]
                                newSkaterStats.shortHandedGoals = resSkaterStats["shortHandedGoals"]
                                newSkaterStats.shortHandedAssists = resSkaterStats["shortHandedAssists"]
                                newSkaterStats.blocked = resSkaterStats["blocked"]
                                newSkaterStats.plusMinus = resSkaterStats["plusMinus"]
                                newSkaterStats.evenTimeOnIce = convert_string_to_time(resSkaterStats["evenTimeOnIce"])
                                newSkaterStats.powerPlayTimeOnIce = convert_string_to_time(resSkaterStats["powerPlayTimeOnIce"])
                                newSkaterStats.shortHandedTimeOnIce = convert_string_to_time(resSkaterStats["shortHandedTimeOnIce"])

                                session.add(newSkaterStats)

            except Exception as e:
                print(e)
                print(info["gamePk"])
                print("----")
                traceback.print_exc()

        return add_game_stats_to_db



    res = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?season={}'.format(season))
    res = res.json()

    base = "https://statsapi.web.nhl.com/api/v1/game/"
    urls = []

    if "dates" in res:
        for date in res["dates"]:
            for game in date["games"]:
                add_game_to_db(session, game)
                gamePk = game["gamePk"]
                urls.append((base + str(gamePk) + "/boxscore", { "session": session, "gamePk": str(gamePk), "stats" : {game["teams"]["home"]["team"]["id"]: {"wins": game["teams"]["home"]["leagueRecord"]["wins"],
                                                                                                                "losses": game["teams"]["home"]["leagueRecord"]["losses"],
                                                                                                                "ot": game["teams"]["home"]["leagueRecord"]["ot"] if "ot" in game["teams"]["home"]["leagueRecord"] else "",
                                                                                                                "type": game["teams"]["home"]["leagueRecord"]["type"],
                                                                                                                "score": game["teams"]["home"]["score"]},
                                                                            game["teams"]["away"]["team"]["id"]: {"wins": game["teams"]["away"]["leagueRecord"]["wins"],
                                                                                                                "losses": game["teams"]["away"]["leagueRecord"]["losses"],
                                                                                                                "ot": game["teams"]["away"]["leagueRecord"]["ot"] if "ot" in game["teams"]["away"]["leagueRecord"] else "",
                                                                                                                "type": game["teams"]["away"]["leagueRecord"]["type"],
                                                                                                                "score": game["teams"]["away"]["score"]}}}))

    #rs = (grequests.get(u[0], hooks={'response': [hook_factory(info=u[1])]}) for u in urls[:2])
    rs = (grequests.get(u[0], hooks={'response': [hook_factory(info=u[1])]}) for u in urls)
    responses = grequests.map(rs)


def fill_teams():
    pass

def fill_persons():
    pass

def print_test(session):
    games = session.query(skaterStats).all()
    for game in games:
        print(game)
