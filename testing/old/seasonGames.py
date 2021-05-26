import sqlite3
import grequests
import requests
import json
import time


def add_game_to_db(cur, game):
    values = ""
    values += str(game["gamePk"]) + ","
    values += "\"" + str(game["gameType"]) + "\", "
    values += "\"" + str(game["season"]) + "\", "
    values += "\"" + str(game["gameDate"]) + "\", "
    values += "\"" + str(game["status"]["statusCode"]) + "\", "
    values += str(game["teams"]["home"]["team"]["id"]) + ", "
    values += str(game["teams"]["away"]["team"]["id"])

    cur.execute("INSERT INTO game(pk, gameType, season, gameDate, statusCode, homeTeamId, awayTeamId) VALUES({})".format(values))



def fill_all_games_from_season(season):
    res = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?season={}'.format(season))
    res = res.json()

    con = sqlite3.connect('./database.db')
    cur = con.cursor()

    if "dates" in res:
        for date in res["dates"]:
            for game in date["games"]:
                add_game_to_db(cur, game)

    con.commit()
    con.close()








def add_current_teams_to_db(con):
    def add_teams(res, *args, **kwargs):
        try:
            if (res):
                
                cur = con.cursor()
                start = time.time()
                for team in res["teams"]:
                    try:
                        thing = "INSERT INTO team(id,name,link,teamName,locationName,firstYearOfPlay,franchise,shortName,active) VALUES({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",{},\"{}\",{});".format(
                            team["id"],
                            team["name"] if "name" in team else "",
                            team["link"] if "link" in team else "",
                            team["teamName"] if "teamName" in team else "",
                            team["locationName"] if "locationName" in team else "",
                            team["firstYearOfPlay"] if "firstYearOfPlay" in team else "",
                            team["franchise"]["franchiseId"] if "franchise" in team else "",
                            team["shortName"] if "shortName" in team else "",
                            team["active"] if "active" in team else False)
                        cur.execute(thing)
                    except Exception as e:
                        print(e)
                end = time.time()
                print("Time consumed in working: ", end - start)
                con.commit()
                con.close()
        except Exception as e:
            print(e)

    urls = [
        'https://statsapi.web.nhl.com/api/v1/teams'
    ]

    rs = (grequests.get(u, hooks={'response': add_teams}) for u in urls)
    responses = grequests.map(rs)


fill_all_games_from_season("20202021")
