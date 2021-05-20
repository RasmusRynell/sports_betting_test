
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, accuracy_score, precision_score

from handler import api

api = api("https://statsapi.web.nhl.com/api/v1/", True, True)

def get_num_shots(gamePk, player_id):
    response_json = api.send_request("game/"+str(gamePk)+"/boxscore")
    num_shots = None
    if "ID" + str(player_id) in response_json["teams"]["home"]["players"]:
        num_shots = response_json["teams"]["home"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]

    if "ID" + str(player_id) in response_json["teams"]["away"]["players"]:
        num_shots = response_json["teams"]["away"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]
    return num_shots


def eval_model(pipeline, X_all, Y_all):

    score_acc = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="accuracy").mean(), 3)
    scorer = make_scorer(precision_score, zero_division=0.0)
    score_precision = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring=scorer).mean(), 3)

    X_train, X_test, y_train, y_test = train_test_split(X_all, Y_all, test_size=0.33, random_state=42)
    svc_model = pipeline.fit(X_train, y_train)
    pred = svc_model.predict(X_test)
    matrix = confusion_matrix(y_test, pred)

    return {"confusion matrix": matrix, "accuracy": score_acc, "precision accuracy": score_precision}


def print_eval(res):
    for player_file in res:
        print("--------------------------------------------------")
        print(player_file)
        for over_under in res[player_file]["preds"]:
            print(over_under)
            print(res[player_file]["preds"][over_under]["precision accuracy"])
            for gamePk, prediction in res[player_file]["preds"][over_under]["model predictions"].items():
                if (prediction["prediction"] == 1):
                    print("GamePk: {}, prediction = {} with decision function {} and proba {}. Num shots this game: {}".format(gamePk, over_under.split("_")[1], prediction["decision_function"], \
                        prediction["proba"], get_num_shots(gamePk, res[player_file]["player_id"])))

    print("--------------------------------------------------")

def unit_bet(unit_size, res, all_bets):
    tot_money_betted = 0
    tot_money_won = 0

    for player_file in res:
        money_betted = 0
        money_won = 0
        games = all_bets[str(res[player_file]["player_id"])]["games"]
        for gamePk in games:
            for bet in games[gamePk]["bets"]:
                model_pred_under = 0
                model_pred_over = 0
                if str(games[gamePk]["bets"][bet]["over_under"])+"_under" in res[player_file]["preds"]:
                    model_pred_under = res[player_file]["preds"][str(games[gamePk]["bets"][bet]["over_under"])+"_under"]["model predictions"][int(gamePk)]["prediction"]

                if str(games[gamePk]["bets"][bet]["over_under"])+"_over" in res[player_file]["preds"]:
                    model_pred_over = res[player_file]["preds"][str(games[gamePk]["bets"][bet]["over_under"])+"_over"]["model predictions"][int(gamePk)]["prediction"]

                if model_pred_under == 1:
                    money_betted += unit_size
                    tot_money_betted += unit_size
                    if(float(games[gamePk]["bets"][bet]["over_under"]) > get_num_shots(gamePk, res[player_file]["player_id"])):
                        money_won += float(games[gamePk]["bets"][bet]["under"].replace(",", ".")) * unit_size
                        tot_money_won += float(games[gamePk]["bets"][bet]["under"].replace(",", ".")) * unit_size

                if model_pred_over == 1:
                    money_betted += unit_size
                    tot_money_betted += unit_size
                    if(float(games[gamePk]["bets"][bet]["over_under"]) < get_num_shots(gamePk, res[player_file]["player_id"])):
                        money_won += float(games[gamePk]["bets"][bet]["over"].replace(",", ".")) * unit_size
                        tot_money_won += float(games[gamePk]["bets"][bet]["over"].replace(",", ".")) * unit_size
        if money_betted != 0:
            print("After player: {} we have ROI of {}".format(player_file, round(money_won/money_betted, 3))) 
        else:
            print("no games betted")  
                  
    if tot_money_betted != 0:   
        return round(tot_money_won/tot_money_betted, 3)
    else:
        return -1
