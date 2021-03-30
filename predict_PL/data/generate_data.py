
import numpy as np
import pandas as pd
from datetime import datetime as dt
import itertools
from tqdm import tqdm

def num_goals_scored(data, team, stop_index):
    goal_counter = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break
        if(row["HomeTeam"] == team):
            goal_counter += row["FTHG"]
        if(row["AwayTeam"] == team):
            goal_counter += row["FTAG"]

    return goal_counter   

def num_goals_concieded(data, team, stop_index):
    goal_counter = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break
        if(row["HomeTeam"] == team):
            goal_counter += row["FTAG"]
        if(row["AwayTeam"] == team):
            goal_counter += row["FTHG"]

    return goal_counter   

def get_stats_last_games(data, team, num_games_back, stop_index):
    team_stats = []
    tmp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    team_stats.append(tmp)
    team_stats.append(tmp)
    team_stats.append(tmp)
    team_stats.append(tmp)
    team_stats.append(tmp)
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if row["HomeTeam"] == team or row["AwayTeam"] == team:
            tmp = [row["FTHG"], row["FTAG"], row["HS"], row["AS"], row["HST"], row["AST"], row["HF"], row["AF"], \
                row["HC"], row["AC"], row["HY"], row["AY"], row["HR"], row["AR"]]
            team_stats.append(tmp)

    return team_stats[-num_games_back]

def get_points_last_games(data, team, num_games_back, stop_index):
    points_last_games = []
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            if row["FTR"] == "H":
                points_last_games.append(3)
            elif row["FTR"] == "D":
                points_last_games.append(1)
            else:
                points_last_games.append(0)
        if(row["AwayTeam"] == team):
            if row["FTR"] == "A":
                points_last_games.append(3)
            elif row["FTR"] == "D":
                points_last_games.append(1)
            else:
                points_last_games.append(0)

    return sum(points_last_games[-num_games_back:])

def get_points_this_season(data, team, stop_index):
    points_this_season = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            if row["FTR"] == "H":
                points_this_season += 3
            elif row["FTR"] == "D":
                points_this_season += 1
            else:
                points_this_season += 0
        if(row["AwayTeam"] == team):
            if row["FTR"] == "A":
                points_this_season += 3
            elif row["FTR"] == "D":
                points_this_season += 1
            else:
                points_this_season += 0
    return points_this_season

def get_yellow_cards_last_games(data, team, num_games_back, stop_index):
    yellow_last_games = []
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            yellow_last_games.append(row["HY"])
        if(row["AwayTeam"] == team):
            yellow_last_games.append(row["AY"])
    return sum(yellow_last_games[-num_games_back:])

def get_yellow_cards_this_season(data, team, stop_index):
    yellow_this_season = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            yellow_this_season += row["HY"]
        if(row["AwayTeam"] == team):
            yellow_this_season += row["AY"]
    return yellow_this_season

def get_corners_last_games(data, team, num_games_back, stop_index):
    corners_last_games = []
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            corners_last_games.append(row["HC"])
        if(row["AwayTeam"] == team):
            corners_last_games.append(row["AC"])
    return sum(corners_last_games[-num_games_back:])

def get_corners_this_season(data, team, stop_index):
    corners_this_season = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            corners_this_season += row["HY"]
        if(row["AwayTeam"] == team):
            corners_this_season += row["AY"]
    return corners_this_season

def get_free_kicks_for_last_games(data, team, num_games_back, stop_index):
    free_kicks_last_games = []
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            free_kicks_last_games.append(row["AF"])
        if(row["AwayTeam"] == team):
            free_kicks_last_games.append(row["HF"])
    return sum(free_kicks_last_games[-num_games_back:])

def get_free_kicks_for_this_season(data, team, stop_index):
    free_kicks_this_season = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            free_kicks_this_season += row["AF"]
        if(row["AwayTeam"] == team):
            free_kicks_this_season += row["HF"]
    return free_kicks_this_season

def get_free_kicks_against_last_games(data, team, num_games_back, stop_index):
    free_kicks_last_games = []
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            free_kicks_last_games.append(row["HF"])
        if(row["AwayTeam"] == team):
            free_kicks_last_games.append(row["AF"])
    return sum(free_kicks_last_games[-num_games_back:])

def get_free_kicks_against_this_season(data, team, stop_index):
    free_kicks_this_season = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            free_kicks_this_season += row["HF"]
        if(row["AwayTeam"] == team):
            free_kicks_this_season += row["AF"]
    return free_kicks_this_season

def calc_xG(num_shots, num_shots_on_goal, num_corners, num_free_kicks):
    return (num_shots*0.1 + num_shots_on_goal*0.5 + num_corners*0.01 + num_free_kicks*0.01)

def get_xG_last_games(data, team, num_games_back, stop_index):
    xG_last_games = []
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            xG_last_games.append(calc_xG(row["HS"], row["HST"], row["HC"], row["AF"]))
        if(row["AwayTeam"] == team):
            xG_last_games.append(calc_xG(row["AS"], row["AST"], row["AC"], row["HF"]))
    return sum(xG_last_games[-num_games_back:])

def get_xG_this_season(data, team, stop_index):
    xG_this_season = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            xG_this_season += calc_xG(row["HS"], row["HST"], row["HC"], row["AF"])
        if(row["AwayTeam"] == team):
            xG_this_season += calc_xG(row["AS"], row["AST"], row["AC"], row["HF"])
    return xG_this_season

def get_xGA_last_games(data, team, num_games_back, stop_index):
    xGA_last_games = []
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            xGA_last_games.append(calc_xG(row["AS"], row["AST"], row["AC"], row["HF"]))
        if(row["AwayTeam"] == team):
            xGA_last_games.append(calc_xG(row["HS"], row["HST"], row["HC"], row["AF"]))
    return sum(xGA_last_games[-num_games_back:])

def get_xGA_this_season(data, team, stop_index):
    xGA_this_season = 0
    for index, row in data.iterrows():
        if index == stop_index:
            break

        if(row["HomeTeam"] == team):
            xGA_this_season += calc_xG(row["AS"], row["AST"], row["AC"], row["HF"])
        if(row["AwayTeam"] == team):
            xGA_this_season += calc_xG(row["HS"], row["HST"], row["HC"], row["AF"])
    return xGA_this_season

def get_number_of_corners(data, index):
    return data.iloc[index]["HC"] + data.iloc[index]["AC"]

def get_number_of_yellow_cards(data, index):
    return data.iloc[index]["HY"] + data.iloc[index]["AY"]

def get_number_of_free_kicks(data, index):
    return data.iloc[index]["HF"] + data.iloc[index]["AF"]

def get_number_of_goals(data, index):
    return data.iloc[index]["FTHG"] + data.iloc[index]["FTAG"]

def get_game_result(data, index):
    return data.iloc[index]["FTR"]

########################################################################

seasons = ["2020-2021.csv", "2019-2020.csv", "2018-2019.csv", "2017-2018.csv", "2016-2017.csv", "2015-2016.csv", "2014-2015.csv", \
    "2013-2014.csv", "2012-2013.csv", "2011-2012.csv", "2010-2011.csv", "2009-2010.csv", "2008-2009.csv", "2007-2008.csv", "2006-2007.csv", "2005-2006.csv"]

save_x = []
y_corners = []
y_yellow_cards = []
y_free_kicks = []
y_goals = []
y_result = []

for season in tqdm(seasons):
    data = pd.read_csv("./data/premier_league_data/" + season)
    for index, row in tqdm(data.iterrows()):  
        #Calculate the answers
        y_corners.append(get_number_of_corners(data, index))
        y_yellow_cards.append(get_number_of_yellow_cards(data, index))
        y_free_kicks.append(get_number_of_free_kicks(data, index))
        y_goals.append(get_number_of_goals(data, index))
        y_result.append(get_game_result(data, index))


        #Just for the home team  
        tmp = []
        tmp.append(num_goals_scored(data, row["HomeTeam"], index))
        tmp.append(num_goals_concieded(data, row["HomeTeam"], index))

        tmp += get_stats_last_games(data, row["HomeTeam"], 1, index)
        tmp += get_stats_last_games(data, row["HomeTeam"], 2, index)
        tmp += get_stats_last_games(data, row["HomeTeam"], 3, index)
        tmp += get_stats_last_games(data, row["HomeTeam"], 4, index)
        tmp += get_stats_last_games(data, row["HomeTeam"], 5, index)

        tmp.append(get_points_last_games(data, row["HomeTeam"], 5, index))
        tmp.append(get_points_this_season(data, row["HomeTeam"], index))

        tmp.append(get_yellow_cards_last_games(data, row["HomeTeam"], 5, index))
        tmp.append(get_yellow_cards_this_season(data, row["HomeTeam"], index))

        tmp.append(get_corners_last_games(data, row["HomeTeam"], 5, index))
        tmp.append(get_corners_this_season(data, row["HomeTeam"], index))

        tmp.append(get_free_kicks_for_last_games(data, row["HomeTeam"], 5, index))
        tmp.append(get_free_kicks_for_this_season(data, row["HomeTeam"], index))
        tmp.append(get_free_kicks_against_last_games(data, row["HomeTeam"], 5, index))
        tmp.append(get_free_kicks_against_this_season(data, row["HomeTeam"], index))

        tmp.append(get_xG_last_games(data, row["HomeTeam"], 5, index))
        tmp.append(get_xGA_last_games(data, row["HomeTeam"], 5, index))
        tmp.append(get_xG_this_season(data, row["HomeTeam"], index))
        tmp.append(get_xGA_this_season(data, row["HomeTeam"], index))

        #Just for the away team  
        tmp.append(num_goals_scored(data, row["AwayTeam"], index))
        tmp.append(num_goals_concieded(data, row["AwayTeam"], index))

        tmp += get_stats_last_games(data, row["AwayTeam"], 1, index)
        tmp += get_stats_last_games(data, row["AwayTeam"], 2, index)
        tmp += get_stats_last_games(data, row["AwayTeam"], 3, index)
        tmp += get_stats_last_games(data, row["AwayTeam"], 4, index)
        tmp += get_stats_last_games(data, row["AwayTeam"], 5, index)

        tmp.append(get_points_last_games(data, row["AwayTeam"], 5, index))
        tmp.append(get_points_this_season(data, row["AwayTeam"], index))

        tmp.append(get_yellow_cards_last_games(data, row["AwayTeam"], 5, index))
        tmp.append(get_yellow_cards_this_season(data, row["AwayTeam"], index))

        tmp.append(get_corners_last_games(data, row["AwayTeam"], 5, index))
        tmp.append(get_corners_this_season(data, row["AwayTeam"], index))

        tmp.append(get_free_kicks_for_last_games(data, row["AwayTeam"], 5, index))
        tmp.append(get_free_kicks_for_this_season(data, row["AwayTeam"], index))
        tmp.append(get_free_kicks_against_last_games(data, row["AwayTeam"], 5, index))
        tmp.append(get_free_kicks_against_this_season(data, row["AwayTeam"], index))

        tmp.append(get_xG_last_games(data, row["AwayTeam"], 5, index))
        tmp.append(get_xGA_last_games(data, row["AwayTeam"], 5, index))
        tmp.append(get_xG_this_season(data, row["AwayTeam"], index))
        tmp.append(get_xGA_this_season(data, row["AwayTeam"], index))

        save_x.append(tmp)


df = pd.DataFrame(save_x)

df["num corners"] = y_corners
df["num yellow cards"] = y_yellow_cards
df["num free kicks"] = y_free_kicks
df["num goals"] = y_goals
df["result"] = y_result

df.to_csv("./final_dataset.csv")

print("[DONE]")
