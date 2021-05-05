
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



def generate_models(allModels=False, SVC=False):
    f = open("./data/input.txt")
    files = f.readlines()
    res = {}
    for tmp in (files):
        file, earliest_gamePk_index, over_unders = tmp.split(" ")
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

    api.save()
    print(json.dumps(res, indent=4, sort_keys=True))
if __name__ == "__main__":
    parser=argh.ArghParser()
    parser.add_commands([generate_models])
    parser.dispatch()



