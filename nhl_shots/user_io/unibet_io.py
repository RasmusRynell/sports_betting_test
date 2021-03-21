import json
from datetime import datetime as dt
from datetime import timedelta
import Settings
import pytz

def print_json(j):
    print(json.dumps(j, indent=4, sort_keys=True))

def update_match(content, old, date):
    if " - " in content[0]:
        team_one, team_two = content[0].lower().split(" - ")

    old_keys = list(old.keys())
    
    date_new = dt.fromisoformat(date)

    game = ""
    if str(team_one + " @ " + team_two+"-"+str(date_new.date())).lower() in old:
        game = str(team_one + " @ " + team_two+"-"+str(date_new.date())).lower()
    elif str(team_two + " @ " + team_one+"-"+str(date_new.date())).lower() in old:
        game = str(team_two + " @ " + team_one+"-"+str(date_new.date())).lower()
    else:
        date_new += timedelta(days=1)
        if str(team_one + " @ " + team_two+"-"+str(date_new.date())).lower() in old:
            game = str(team_one + " @ " + team_two+"-"+str(date_new.date())).lower()
        elif str(team_two + " @ " + team_one+"-"+str(date_new.date())).lower() in old:
            game = str(team_two + " @ " + team_one+"-"+str(date_new.date())).lower()
        else:
            date_new += timedelta(days=1)
            game = str(team_one + " @ " + team_two+"-"+str(date_new.date())).lower()
            old[game] = {}


    for index in range(1, len(content), 5):
        if " - " in str(content[index]):
            update_match(content[index:], old, date)
            break
        
        l_name, f_name = (str(content[index + 0]).lower()).split(", ")
        name = f_name +" "+ l_name
        if name not in old[game]:
            if name in Settings.name_translate:
                name = Settings.name_translate[name]
            else:
                old[game][name] = {}
                while True:
                    old[game][name]["date_time"] = " a"#input("date_time for game with \"{}\", (\"{}\" VS \"{}\") (EXAMPLE: 2021-03-20) (Enter for todays date): ".format(name, team_one, team_two))
                    break #REMOVE
                    if old[game][name]["date_time"] == "":
                        old[game][name]["date_time"] = str(dt.today().date())
                        #if input("Are you sure you want \"{}\" for this match? (Enter for YES anythings else for NO): ".format(old[game][name]["date_time"])) == "":
                        break # MOVE UP ONE
                old[game][name]["name"] = name
                old[game][name]["ply_team"] = " b"#team_one if input("Does \"{}\" play for \"{}\"? anything for yes and nothing for no: ".format(name, team_one)) else team_two
                old[game][name]["opp_team"] = " c"#team_two if old[game][name]["ply_team"] == team_one else team_one
        old[game][name]["unibet"] = {}
        old[game][name]["unibet"]["over-under"] = str(content[index + 1][6:])
        old[game][name]["unibet"]["unitbet-over"] = str(content[index + 2])
        old[game][name]["unibet"]["unibet-under"] = str(content[index + 4])


def get_from_file(path, old):
    content = []
    with open(path) as file:
        content = file.readlines()
        content = [x.replace("\n", "") for x in content]
        content = [x for x in content if x != ""]

    if len(content) > 0:
        update_match(content, old, path[len(path)-17:-7])

    return old
