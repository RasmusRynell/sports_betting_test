import Settings
import implementations.data_handlers.player_handler as player_handler
import os
import csv
import psutil
from tqdm import tqdm

def generateTrainingDataFromDates(startDate_date, endDate_date=None):
    tot = 0
    tot_l = []
    for gamePk, info in Settings.db.old_bets.items():
        if endDate_date==None:
            if str(info["date"]) == str(startDate_date.date()):
                tot_l.append(info)
                tot += 1

        else:
            currDate_date = Settings.string_to_standard_datetime(info["date"] + "T00:00:00Z")
            if startDate_date <= currDate_date and currDate_date <= endDate_date:
                tot_l.append(info)
                tot += 1

    for info in tqdm(tot_l):
        print(create_csv(info))

    return tot




def create_csv(bet, path = "", path_for_one_file = ""):
    try:
        name = bet["player_name"]
        player_id = bet["player_id"]
        date = bet["date"]
        gamePk = bet["gamePk"]

        team_id = bet["player_team_id"]
        opp_team_id = bet["opp_team_id"]

        headers, stats_for_player = player_handler.generate_training_data(gamePk, player_id, team_id, opp_team_id)

        if not path:
            path = "./data/td/pp_" + str(gamePk) + "_" + str(name) + ".csv"
            path = path.lower().replace(' ', '_')

        if path_for_one_file:
            with open(str(path_for_one_file), 'a', newline='\n') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                if os.stat(path_for_one_file).st_size == 0:
                    writer.writerow(headers)

                for game in stats_for_player:
                    writer.writerow(game.values())


        # Open and write to csv-file
        with open(str(path), 'w+', newline='\n') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(headers)

            for game in stats_for_player:
                writer.writerow(game.values())


    except Exception as e:
        print("Cannot create CSV file for " + str(name))
        print(e)
        return ""

    # return path