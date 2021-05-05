
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
    for gamePk, game_data in player_data["games"].items():
        game_index = data.loc[data["gamePk"] == int(gamePk)].index[0]
        if (earliest_gamePk == None or game_index < earliest_gamePk):
            earliest_gamePk = game_index

        for bet in game_data["bets"]:
            if (game_data["bets"][bet]["over_under"] not in over_unders):
                over_unders.append(game_data["bets"][bet]["over_under"])
    
    output_line = file_path + " " + str(earliest_gamePk) + " " + str(over_unders).replace(" ", "").replace("[", "").replace("]", "").replace("'","") + "\n"
    f1.write(output_line)
f1.close()