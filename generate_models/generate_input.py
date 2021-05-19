
import json
import pandas as pd
import numpy as np



f = open("./data/all_bets.json")
all_bets = json.load(f)

f1 = open("./data/input_tmp.txt", "w")

for player_id, player_data in all_bets.items():
    file_path = "./data/td/pp_" + player_data["player_name"].lower().replace(" ", "_") + ".csv"
    over_unders = []
    earliest_gamePk = None
    data = pd.read_csv(file_path)
    data = data.replace(np.nan, 0)
    average_odds = {}
    for gamePk, game_data in player_data["games"].items():
        game_index = data.loc[data["gamePk"] == int(gamePk)].index[0]
        if (earliest_gamePk == None or game_index < earliest_gamePk):
            earliest_gamePk = game_index

        for bet in game_data["bets"]:
            if (game_data["bets"][bet]["over_under"] not in over_unders):
                over_unders.append(game_data["bets"][bet]["over_under"])

            if(str(game_data["bets"][bet]["over_under"])+"_over" not in average_odds):
                average_odds[str(game_data["bets"][bet]["over_under"])+"_over"] = []
                average_odds[str(game_data["bets"][bet]["over_under"])+"_under"] = []
            average_odds[str(game_data["bets"][bet]["over_under"])+"_over"].append(float(game_data["bets"][bet]["over"].replace(",", ".")))
            average_odds[str(game_data["bets"][bet]["over_under"])+"_under"].append(float(game_data["bets"][bet]["under"].replace(",", ".")))
    
    tmp = ""
    for odds in average_odds:
        tmp += str(odds) + ":" + str(round(sum(average_odds[odds])/len(average_odds[odds]), 2)) + ","
    
    output_line = file_path + " " + player_id + " " + str(earliest_gamePk) + " " + str(over_unders).replace(" ", "").replace("[", "").replace("]", "").replace("'","") +  " " + tmp + "\n"
    f1.write(output_line)
f1.close()