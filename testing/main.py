import sqlite3
import grequests
import json

con = sqlite3.connect('./database.db')

def add_games_from_date_hook(res, *args, **kwargs):
    if (res):
        res = res.json()
        cur = con.cursor()
        for game in res["dates"][0]["games"]:
            gamePk = game["gamePk"]
            gameType = game["gameType"]
            season = game["season"]
            gameDate = game["gameDate"]
            statusCode = game["status"]["statusCode"]
            homeTeam = game["teams"]["home"]["team"]["id"]
            awayTeam = game["teams"]["away"]["team"]["id"]
            cur.execute("INSERT INTO game VALUES ({},{},{},{},{},{},{})".format(gamePk, gameType, season, gameDate, statusCode, homeTeam, awayTeam))
        con.commit()
        con.close()


df.to_sql("team", cur, if_exists='replace')
#print(json.dumps(keep, indent=4))





urls = [
    'https://statsapi.web.nhl.com/api/v1/schedule?date=2021-03-18'
]

rs = (grequests.get(
    u, hooks={'response': add_games_from_date_hook}) for u in urls)
responses = grequests.map(rs)
