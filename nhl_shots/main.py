import data_processing.create_csv as create_csv
import user_io.bet365 as bet365_data
import Settings

# Get data from bet365
games = bet365_data.get_from_clipboard()

# Add home or away team
for game in games:
    home = input("Is \"{}\" the home team (TRUE, True, T or t for True...) = ".format(games[game]["team_one"]))
    if (home == "TRUE") or (home == "True") or (home == "T") or (home == "t"):
        games[game]["home_team"] = games[game]["team_one"]
        games[game]["away_team"] = games[game]["team_two"]
    else:
        games[game]["home_team"] = games[game]["team_two"]
        games[game]["away_team"] = games[game]["team_one"]

# Generate all csv files and save them
bets = []
for game in games:
    for player_name, values in games[game]["bet365-stat"].items():
        bet = [player_name, values["team"], games[game]["home_team"] if games[game]["home_team"] != values["team"] else games[game]["away_team"], \
            "Home" if games[game]["home_team"] == values["team"] else "Away"]
        bet = [string.lower() for string in bet]
        bets.append([bet, [values["over-under"], values["over"], values["under"]]])

files = create_csv.create_csv(bets, False)

#Debug
print(files)


# Call predictor to predict all csv files

# Save all predictions into one csv (or excel) file
