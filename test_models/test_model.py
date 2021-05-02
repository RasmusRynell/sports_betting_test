import argh
import json
from tqdm import tqdm
from unidecode import unidecode

from handler import api

#Import all models
import models.models.pred_SVC as pred_SVC
import models.models.pred_SVC_opt as pred_SVC_opt
import models.models.pred_logistic_regression as pred_logistic_regression
import models.models.pred_KNN as pred_KNN

# Fixa mina modeller med "pipe" och korrekt skalning https://scikit-learn.org/stable/modules/preprocessing.html
# Bra post, https://stackoverflow.com/questions/38077190/how-to-increase-the-model-accuracy-of-logistic-regression-in-scikit-python 
# Tror jag har missat att skala om datan för slutgiltiga prediction

f = open("./pred_data/preds.json")
all_bets = json.load(f)

player_preds = {}

models = ["SVC", "SVC-OPT", "log-reg", "KNN"]

over_acc = []
under_acc = []

player_acc = {}


for player_id, games in (all_bets.items()):
    player_name = games["player_name"]
    player_acc[player_name] = {}
    for model in models:
        player_acc[player_name][model] = {}
        player_acc[player_name][model]["over_acc"] = []
        player_acc[player_name][model]["under_acc"] = []
        over_tmp = []
        under_tmp = []
        for gamePk, game in games["games"].items():
            for i in game["predictions"][model]:
                over_acc.append(float(game["predictions"][model][i]["pred_over"]["acc"]))
                under_acc.append(float(game["predictions"][model][i]["pred_over"]["acc"]))
                over_tmp.append(float(game["predictions"][model][i]["pred_over"]["acc"]))
                under_tmp.append(float(game["predictions"][model][i]["pred_over"]["acc"]))
        player_acc[player_name][model]["over_acc"].append(sum(over_tmp)/len(over_tmp)) 
        player_acc[player_name][model]["under_acc"].append(sum(under_tmp)/len(under_tmp))        

#print(json.dumps(player_acc, indent=4, sort_keys=True))

tmp = []
models = ["SVC", "SVC-OPT", "log-reg", "KNN"]
for model in models:
    print("--------------------")
    print(model)
    tmp = []
    for player, pred in player_acc.items():
        if float(pred[model]["over_acc"][0]) >= 0.6:
            tmp.append(float(pred[model]["over_acc"][0]))
        if float(pred[model]["under_acc"][0]) >= 0.6:
            tmp.append(float(pred[model]["under_acc"][0]))

    print(len(tmp)/2)
    print(len(player_acc))
    print(round((len(tmp)/2)/(len(player_acc)), 3))

print("--------------------")

