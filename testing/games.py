import sqlite3
import grequests
import json
import time
import dateutil.parser
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz



con = sqlite3.connect('./database.db')



def add_all_games_x_seasons_back(season, seasons_back):
    def add_date(res, *args, **kwargs):
        try:
            res = res.json()
            if res['dates'] != []:
                def hook_factory(*factory_args, **factory_kwargs):
                    def add_game(res, *args, **kwargs):
                        try:
                            res = res.json()
                            cur = con.cursor()
                            for team in ("home", "away"):
                                try:
                                    team_id = res["teams"][team]["team"]["id"]
                                    pk = factory_kwargs["arguments"][1]
                                    score = factory_kwargs["arguments"][2][team_id]["score"]
                                    wins = factory_kwargs["arguments"][2][team_id]["wins"]
                                    losses = factory_kwargs["arguments"][2][team_id]["losses"]
                                    ots = factory_kwargs["arguments"][2][team_id]["ot"]
                                    goals = res["teams"][team]["teamStats"]["teamSkaterStats"]["goals"]
                                    pim = res["teams"][team]["teamStats"]["teamSkaterStats"]["pim"]
                                    shots = res["teams"][team]["teamStats"]["teamSkaterStats"]["shots"]
                                    powerPlayPercentage = res["teams"][team]["teamStats"]["teamSkaterStats"]["powerPlayPercentage"]
                                    powerPlayGoals = res["teams"][team]["teamStats"]["teamSkaterStats"]["powerPlayGoals"]
                                    powerPlayOpportunuties = res["teams"][team]["teamStats"]["teamSkaterStats"]["powerPlayOpportunities"]
                                    faceOffWinPercentage = res["teams"][team]["teamStats"]["teamSkaterStats"]["faceOffWinPercentage"]
                                    blocked = res["teams"][team]["teamStats"]["teamSkaterStats"]["blocked"]
                                    takeaways = res["teams"][team]["teamStats"]["teamSkaterStats"]["takeaways"]
                                    giveaways = res["teams"][team]["teamStats"]["teamSkaterStats"]["giveaways"]
                                    hits = res["teams"][team]["teamStats"]["teamSkaterStats"]["hits"]
                                    cur.execute("INSERT INTO teamStatsGame VALUES ({},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})".format(pk, team_id, score,
                                            wins, losses, ots, goals, pim, shots, powerPlayPercentage, powerPlayGoals, powerPlayOpportunuties, faceOffWinPercentage,\
                                                                                                                        blocked, takeaways, giveaways, hits))
                                except Exception as e:
                                    print("5")
                                    print(e)
                                    pk = factory_kwargs["arguments"][1]
                                    print(pk)
                                    print("-")
                            con.commit()
                        except Exception as e:
                            print("4")
                            print(e)
                    return add_game


                base = "https://statsapi.web.nhl.com/api/v1/game/"
                urls = []
                cur = con.cursor()
                for game in res['dates'][0]['games']:
                    try:
                        gamePk = game["gamePk"]
                        gameType = game["gameType"]
                        season = game["season"]
                        gameDate = game["gameDate"]
                        statusCode = game["status"]["statusCode"]
                        homeTeam = game["teams"]["home"]["team"]["id"]
                        awayTeam = game["teams"]["away"]["team"]["id"]
                        try:
                            cur.execute("INSERT INTO game VALUES ({},\"{}\",\"{}\",\"{}\",{},{},{})".format(gamePk, gameType, season, gameDate, statusCode, homeTeam, awayTeam))
                        except Exception as e:
                            print("3")
                            print(e)
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
                    except Exception as e:
                        print("2")
                        print(e)
                con.commit()

                rs = (grequests.get(u[0], hooks={'response': [hook_factory(arguments=u)]}) for u in urls)
                responses = grequests.map(rs)

        except Exception as e:
            print("1")
            print(e)




    for i in range(int(season), int(season)-int(seasons_back), -1):
        base = "https://statsapi.web.nhl.com/api/v1/schedule?date="
        urls = []
        current_date = dt(i - 1, 8, 1)
        end_date = dt(i + 1, 7, 15)
        while (current_date != end_date):
            urls.append(base + str(current_date.date()))
            current_date += timedelta(days=1)
        
    rs = (grequests.get(u, hooks={'response': add_date}) for u in urls)
    responses = grequests.map(rs)



add_all_games_x_seasons_back(2021, 10)
con.close()
