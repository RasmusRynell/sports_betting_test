
import json
from datetime import datetime as dt
from datetime import timedelta
from unidecode import unidecode

def read_file(file):
    date = file.split("/")[-1].split(".")[0]
    betting_site = file.split("/")[-1].split(".")[1]
    with open(file, "r", encoding='utf-8') as reader:
        lines = reader.readlines()   
    
    matches= {}
    current_key = ""
    for line in lines:
        line = line.replace("\n","")
        if(line.find(" @ ") > 0):
            current_key = line
            matches[current_key] = []
        elif len(line) > 2:
            matches[current_key].append(line)

    player_names = []
    next_index = 0
    for match in matches:
        home_team = match.split(" @ ")[0]
        away_team = match.split(" @ ")[1]
        for i in range(1, len(matches[match]),2):
            if(matches[match][i] == "Över"):
                next_index = i+1
                break
            else:
                player_names.append(matches[match][i])

    over_data = []
    for match in matches:
        game = []
        start_saving = False
        for i in range(1, len(matches[match])):
            if(start_saving):
                if(matches[match][i] == "Under"):
                    break
                else:
                    over_data.append(matches[match][i])
            else:
                start_saving = matches[match][i] == "Över"

    under_data = []
    for match in matches:
        game = []
        start_saving = False
        for i in range(1, len(matches[match])):
            if(start_saving):
                if(matches[match][i].find(" @ ") > 0):
                    break
                else:
                    under_data.append(matches[match][i])
            else:
                start_saving = matches[match][i] == "Under"
    res = []
    for player_index in range(len(player_names)):
        player_name = unidecode(player_names[player_index].lower())
        player_target = over_data[2*player_index]
        player_odds_O = over_data[2*player_index+1]
        player_odds_U = under_data[2*player_index+1]
        player_info = [date, player_name, home_team, away_team, betting_site, player_odds_O, player_odds_U, player_target]
        res.append(player_info)
    return res


#read_file("../data/old_bets/2021-03-20.bet365")
