import sqlite3
import grequests
import json
import time

con1 = sqlite3.connect('./database.db')

def add_current_teams_to_db(con):
    def add_teams(res, *args, **kwargs):
        try:
            if (res):
                res = res.json()
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


add_current_teams_to_db(con1)
