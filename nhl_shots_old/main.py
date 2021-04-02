import dateutil.parser
import Settings
import implementation.database.handler as db



if __name__ == "__main__":
    





















all_games = list(Settings.data_handling.get_all_games_in_season("2020").values())

start = Settings.string_to_standard_datetime("2021-03-18T23:00:00Z")

all_games = sorted(all_games, key=lambda date: Settings.string_to_standard_datetime(date["date"]))

for game in all_games:
    curr = Settings.string_to_standard_datetime(game["date"])
    if start > curr:
        print("NOW")
    print(str(curr) + ", " + str(game["gamePk"]) + ", \"" + str(game["teams"]["home"]["team"]["name"]) + "\" VS \"" + str(game["teams"]["away"]["team"]["name"])+ "\"")
    start = curr



    # db.add_game(game_id, insert_game)

