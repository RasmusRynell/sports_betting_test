import gevent.monkey
gevent.monkey.patch_all(thread=False, select=False)
from models import *
import requests
import grequests
import datetime

def add_game_to_db(session, game):
    newGame = Game()

    newGame.gamePk = game["gamePk"]
    newGame.gameType = game["gameType"] if "gameType" in game else None
    newGame.season = game["season"] if "season" in game else None
    newGame.gameDate = datetime.datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ") if "gameDate" in game else None
    newGame.abstractGameState = game["status"]["abstractGameState"] if "status" in "game" and "abstractGameState" in game["status"] else None
    newGame.codedGameState = game["status"]["codedGameState"] if "status" in "game" and "codedGameState" in game["status"] else None
    newGame.detailedState = game["status"]["detailedState"] if "status" in "game" and "detailedState" in game["status"] else None
    newGame.statusCode = game["status"]["statusCode"] if "status" in "game" and "statusCode" in game["status"] else None
    newGame.startTimeTBD = game["status"]["startTimeTBD"] if "status" in "game" and "startTimeTBD" in game["status"] else None
    newGame.homeTeamId = game["teams"]["home"]["team"]["id"] \
        if "teams" in "game" and "home" in game["status"] and "team" in game["teams"]["home"] and \
        "id" in game["teams"]["home"]["team"] else None
    newGame.awayTeamId = game["teams"]["away"]["team"]["id"] \
        if "teams" in "game" and "away" in game["status"] and "team" in game["teams"]["away"] and \
        "id" in game["teams"]["away"]["team"] else None

    session.add(newGame)


def fill_all_games_from_season(session, season):

    def add_game_stats_to_db(res, *args, **kwargs):
        print(res["gamePk"])



    res = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?season={}'.format(season))
    res = res.json()

    base = "https://statsapi.web.nhl.com/api/v1/game/"
    urls = []

    if "dates" in res:
        for date in res["dates"]:
            for game in date["games"]:
                #add_game_to_db(session, game)
                gamePk = game["gamePk"]
                urls.append((base + str(gamePk) + "/boxscore", str(gamePk), {game["teams"]["home"]["team"]["id"]: {"wins": game["teams"]["home"]["leagueRecord"]["wins"],
                                                                                                                "losses": game["teams"]["home"]["leagueRecord"]["losses"],
                                                                                                                "ot": game["teams"]["home"]["leagueRecord"]["ot"] if "ot" in game["teams"]["home"]["leagueRecord"] else "",
                                                                                                                "type": game["teams"]["home"]["leagueRecord"]["type"],
                                                                                                                "score": game["teams"]["home"]["score"]},
                                                                            game["teams"]["away"]["team"]["id"]: {"wins": game["teams"]["away"]["leagueRecord"]["wins"],
                                                                                                                "losses": game["teams"]["away"]["leagueRecord"]["losses"],
                                                                                                                "ot": game["teams"]["away"]["leagueRecord"]["ot"] if "ot" in game["teams"]["away"]["leagueRecord"] else "",
                                                                                                                "type": game["teams"]["away"]["leagueRecord"]["type"],
                                                                                                                "score": game["teams"]["away"]["score"]}}))
    print(urls[0][0])
    rs = (grequests.get(u[0], hooks={
          'response': add_game_stats_to_db}) for u in urls)
    responses = grequests.map(rs)
    print(responses)


def print_test(session):
    games = session.query(Game).all()
    for game in games:
        print(game.gameDate)
