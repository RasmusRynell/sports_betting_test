import clipboard
import json
from datetime import datetime as dt
from datetime import timedelta
import Settings
import pytz


def make_date(date):
    d = date
    (date_day, date_month, date_time) = date.split(" ")

    if date_month == "maj":
        date_month = "may"
    elif date_month == "okt":
        date_month = "oct"
    
    date = str(date_day) + " "
    date += str(date_month) + " "
    date += str(date_time) + ":"
    date += str(Settings.current_season)

    date = dt.strptime(date, "%d %b %H:%M:%Y")

    # create both timezone objects
    old_timezone = pytz.timezone("Europe/Stockholm")
    new_timezone = pytz.timezone("Europe/London")
    new_timezone_timestamp = old_timezone.localize(date).astimezone(new_timezone)

    return str(new_timezone_timestamp.date())

def get_from_clipboard():
    text = clipboard.paste()  # text will have the content of clipboard
    clipboard.copy(text)
    text = text.replace("\r", "")
    new_list = text.split("\n")
    everything = [x for x in new_list if x != ' ' and x != '']

    current_game = ""
    current_game_time = ""
    current_game_team_one = ""
    current_game_team_two = ""
    current_player = ""


    bet_index = 0

    is_under = False

    results = {}

    for sentence in everything:
        if '@' in sentence:
            results[sentence] = {}
            current_game = sentence
        elif ':' in sentence:
            results[current_game]["Date-time"] = sentence
        elif '.' in sentence and ('0' in sentence or '1' in sentence or '2' in sentence or '3' in sentence):
            if "1.5" == sentence or "2.5" == sentence or "3.5" == sentence:
                results[current_game]["bet365-stat"][list(results[current_game]["bet365-stat"].keys())[bet_index]]["over-under"] = sentence
            elif is_under:
                results[current_game]["bet365-stat"][list(results[current_game]["bet365-stat"].keys())[bet_index]]["under"] = sentence
                bet_index += 1
            else:
                results[current_game]["bet365-stat"][list(results[current_game]["bet365-stat"].keys())[bet_index]]["over"] = sentence
                bet_index += 1
        else:
            if "Över" in sentence:
                bet_index = 0
                is_under = False
            elif "Under" in sentence:
                bet_index = 0
                is_under = True
            elif sentence.lower() in Settings.teams_translate.keys():
                results[current_game]["bet365-stat"][current_player]["team"] = sentence
            else:
                if "bet365-stat" not in results[current_game]:
                    results[current_game]["bet365-stat"] = {}
                results[current_game]["bet365-stat"][sentence] = {}
                current_player = sentence

    for key, value in results.items():
        (value["team_one"], value["team_two"]) = key.split("@")
        value["team_one"] = value["team_one"][:-1]
        value["team_two"] = value["team_two"][1:]


    # Convert bet365 date into reasonable date
    for key in results:
        date = str(results[key]["Date-time"][4:])
        date = make_date()

        results[key]["Date-time"] = date

    return results



def get_match(content):
    done = {}
    team_one, team_two = content[0].split("@")
    team_one = Settings.teams_translate[team_one[:-1].lower()]
    team_two = Settings.teams_translate[team_two[1:].lower()]
    date_time = make_date(content[1][5:])
    done[team_one+" @ "+team_two+"-"+date_time] = {}

    is_on_players = True
    players = []
    for index in range(2, len(content), 2):
        if "ver" in str(content[index]) and len(content[index]) == 5:
            index += 1
            is_on_players = False

        if is_on_players:
            players.append((content[index].lower(),  Settings.teams_translate[content[index+1].lower()]))
        else:
            i = 0
            for player in players:
                done[team_one+" @ "+team_two+"-"+date_time][player[0]] = { 
                        "name": player[0],
                        "ply_team": player[1],
                        "opp_team": team_one if player[1] == team_two else team_two,
                        "date_time": date_time,
                        "bet-365": {
                            "over_under": content[index + i],
                            "over": content[index + i + 1],
                            "under": content[index + len(players)*2 + i + 2]
                    }}
                i += 2

            if index + len(players)*4 + 1 < len(content):
                if "@" in content[index + len(players)*4 + 1]:
                    done.update(get_match(content[index + len(players)*4 + 1:]))
            break
    return done


def get_from_file(path):
    content = []
    with open(path) as file:
        content = file.readlines()
        content = [x.replace("\n", "") for x in content]
        content = [x for x in content if x not in [" ", ""]]
    
    done = {}
    if len(content) > 0:
        done.update(get_match(content))

    return done