
import pandas as pd
import numpy as np 
from joblib import dump, load

gamePk = 2020030182
player_model = "./generated_models/blake_wheeler/SVC_over_2.5joblib"
file_name = "./data/td/pp_blake_wheeler.csv"
pred_this = "shots_this_game_O2.5"

clf = load(player_model)

data = pd.read_csv(file_name)
data = data.replace(np.nan, 0)

drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]

drop_this = [x for x in drop_this if x != pred_this]
data.drop(drop_this,1, inplace=True)

pred_data = data.loc[data['gamePk'] == gamePk].drop([pred_this],1)

y_pred = clf["model"].predict(pred_data)
print(y_pred)
y_pred = clf["model"].decision_function(pred_data)
print(y_pred)
