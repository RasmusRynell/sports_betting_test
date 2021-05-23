
import argh
import json
from tqdm import tqdm
import os

import models.model_SVC as model_SVC 
from models.eval_model import print_eval
from models.eval_model import unit_bet
from joblib import dump, load


def split_average_odds(average_odds):
    average_odds = average_odds.split(",")
    res = {}
    for odds in average_odds:
        tmp = odds.split(":")
        if(len(tmp) > 1):
            res[tmp[0]] = float(tmp[1])
    return res

def generate_models(allModels=False, SVC=False):
    f = open("./data/input_tmp.txt")
    files = f.readlines()
    f.close()
    #Read bet info
    f = open('./data/player_ids.json',)
    player_ids = json.load(f)
    f.close()
    f = open('./data/all_bets.json',)
    all_bets = json.load(f)
    f.close()
    f = open('./generated_models/model_index.json')
    res = json.load(f)
    f.close()
    # Variables
    model_edge = 0.3    

    for tmp in tqdm(files):
        file, player_id, earliest_gamePk_index, over_unders, average_odds = tmp.split(" ")
        average_odds = split_average_odds(average_odds)
        res[file] = {}
        res[file]["average_odds"] = average_odds
        res[file]["player_id"] = player_id
        player_model_path = "./generated_models/" + all_bets[player_id]["player_name"].lower().replace(" ", "_") +"/"

        if not os.path.exists(player_model_path):
            os.makedirs(player_model_path)

        for over_under in over_unders.split(","):
            over_under = over_under.replace("\n", "")

            if(allModels):
                SVC = True
            
            if(SVC):
                model_name = "SVC"
                model_under = model_SVC.generate_model(file, "shots_this_game_U"+str(over_under), int(earliest_gamePk_index), average_odds[over_under + "_under"], model_edge)
                model_over = model_SVC.generate_model(file, "shots_this_game_O"+str(over_under), int(earliest_gamePk_index), average_odds[over_under + "_over"], model_edge)
                if model_name not in res[file]:
                    res[file][model_name] = {}
                
                model_under_filepath = player_model_path + model_name + "_under_" + str(over_under) + ".joblib" 
                model_over_filepath = player_model_path + model_name + "_over_" + str(over_under) + ".joblib"

                res[file][model_name]["shots_this_game_U"+str(over_under)] = model_under_filepath
                res[file][model_name]["shots_this_game_O"+str(over_under)] = model_over_filepath

                dump(model_under, model_under_filepath)
                dump(model_over, model_over_filepath)

            #break
        #break
    # Save a json object with information about paths for models and the precision of each model.
    json_object = json.dumps(res, indent = 4)
    with open("./generated_models/model_index.json", "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    parser=argh.ArghParser()
    parser.add_commands([generate_models])
    parser.dispatch()



