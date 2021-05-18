
import argh
import json
from tqdm import tqdm

from handler import api

import models.model_SVC as model_SVC 

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
    res = {}
    for tmp in tqdm(files):
        file, earliest_gamePk_index, over_unders, average_odds = tmp.split(" ")
        average_odds = split_average_odds(average_odds)
        for over_under in over_unders.split(","):
            over_under = over_under.replace("\n", "")
            if(allModels):
                SVC = True
            
            if(SVC):
                res_under = model_SVC.generate_model(file, "shots_this_game_U"+str(over_under), int(earliest_gamePk_index))
                res_over = model_SVC.generate_model(file, "shots_this_game_O"+str(over_under), int(earliest_gamePk_index))
                if file not in res:
                    res[file] = {}
                res[file]["shots_this_game_U"+str(over_under)] = res_under
                res[file]["shots_this_game_O"+str(over_under)] = res_over

                if(average_odds[over_under + "_under"] > (1/float(res_under["precision accuracy"]))):
                    print("--------------------------------------------------")
                    print("Player: {}".format(file))
                    print("Target: {}".format(over_under + "_under"))
                    print("Confusion matrix:\n {}".format(res_under["confusion matrix"]))
                    print("Accuracy: {}\tPrecision accuracy: {}"\
                        .format(res_under["accuracy"], res_under["precision accuracy"]))
                    print("Odds edge: {} - {} = {}".format(average_odds[over_under + "_under"], round(1/float(res_under["precision accuracy"]), 3), \
                        round(average_odds[over_under + "_under"] - 1/float(res_under["precision accuracy"]), 3)))
                    print("--------------------------------------------------")
                if(average_odds[over_under + "_over"] > (1/float(res_over["precision accuracy"]))):
                    print("--------------------------------------------------")
                    print("Player: {}".format(file))
                    print("Target: {}".format(over_under + "_over"))
                    print("Confusion matrix:\n {}".format(res_over["confusion matrix"]))
                    print("Accuracy: {}\tPrecision accuracy: {}"\
                        .format(res_over["accuracy"], res_over["precision accuracy"]))
                    print("Odds edge: {} - {} = {}".format(average_odds[over_under + "_over"], round(1/float(res_over["precision accuracy"]), 3), \
                        round(average_odds[over_under + "_over"] - 1/float(res_over["precision accuracy"]), 3)))
                    print("--------------------------------------------------")
                #print(res_over["confusion matrix"])
            #break
        #break
    api.save()
    #print(json.dumps(res, indent=4, sort_keys=True))
if __name__ == "__main__":
    parser=argh.ArghParser()
    parser.add_commands([generate_models])
    parser.dispatch()



