
import argh
import json
from tqdm import tqdm

from handler import api

import models.model_SVC as model_SVC 
from models.eval_model import print_eval
from models.eval_model import unit_bet

api = api("https://statsapi.web.nhl.com/api/v1/", True, True)

def get_num_shots(gamePk, player_id):
    response_json = api.send_request("game/"+str(gamePk)+"/boxscore")
    num_shots = None
    if "ID" + str(player_id) in response_json["teams"]["home"]["players"]:
        num_shots = response_json["teams"]["home"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]

    if "ID" + str(player_id) in response_json["teams"]["away"]["players"]:
        num_shots = response_json["teams"]["away"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]
    return num_shots


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
    #Read bet info
    f = open('./data/player_ids.json',)
    player_ids = json.load(f)
    f = open('./data/all_bets.json',)
    all_bets = json.load(f)
    # Variables
    model_edge = 0.3
    
    res = {}
    for tmp in tqdm(files):
        file, player_id, earliest_gamePk_index, over_unders, average_odds = tmp.split(" ")
        average_odds = split_average_odds(average_odds)
        for over_under in over_unders.split(","):
            over_under = over_under.replace("\n", "")
            if(allModels):
                SVC = True
            
            if(SVC):
                res_under = model_SVC.generate_model(file, "shots_this_game_U"+str(over_under), int(earliest_gamePk_index), average_odds[over_under + "_under"], model_edge)
                res_over = model_SVC.generate_model(file, "shots_this_game_O"+str(over_under), int(earliest_gamePk_index), average_odds[over_under + "_over"], model_edge)

                if((average_odds[over_under + "_under"] - (1/float(res_under["precision accuracy"]))) > model_edge):
                    if file not in res:
                        res[file] = {}
                        res[file]["player_id"] = player_id
                        res[file]["preds"] = {}
                    res[file]["preds"][str(over_under)+"_under"] = res_under

                if((average_odds[over_under + "_over"] - (1/float(res_over["precision accuracy"]))) > model_edge):
                    if file not in res:
                        res[file] = {}
                        res[file]["player_id"] = player_id
                        res[file]["preds"] = {}
                    res[file]["preds"][str(over_under)+"_over"] = res_over
            #break
        #break
    #print_eval(res)
    print("Result from unit bet: {}".format(unit_bet(2, res, all_bets)))

if __name__ == "__main__":
    parser=argh.ArghParser()
    parser.add_commands([generate_models])
    parser.dispatch()



