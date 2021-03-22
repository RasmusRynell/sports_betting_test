from tqdm import tqdm
import os
import psutil
import sys
import Settings
import traceback
import csv

def create_csv(bet, path = "", path_for_one_file = ""):
    try:
        name = bet["name"]
        date = bet["date"]
        (headers, stats_for_player) = games_obj.get_stats_for_player(bet)

        if not path:
            path = "./temp2/pp_" + str(date) + "_" + str(name) + ".csv"
            path = path.lower().replace(' ', '_')

        if path_for_one_file:
            with open(str(path_for_one_file), 'a', newline='\n') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                if os.stat(path_for_one_file).st_size == 0:
                    writer.writerow(headers)
                #if not one_file:
                    #TODO: We should add the line for this current gave here.

                for game in stats_for_player:
                    writer.writerow(game.values())


        # Open and write to csv-file
        with open(str(path), 'w+', newline='\n') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(headers)

            for game in stats_for_player:
                writer.writerow(game.values())


    except BaseException as e:
        print("Cannot create CSV file for " + str(name))
        print(e)
        return ""

    if Settings.Debug["ram usage"]:
        process = psutil.Process(os.getpid())
        print("Total memory used: " + str((process.memory_info().rss / 1000000.0)) + "mb")

    return path

    #f = games_obj.get_stats_for_player(bet[])

    #for bet in tqdm(bets):
        #try:
            #files.append([data_handling.save_data_player(bet[0], bet[1]), bet[1]])
        #except BaseException as e:
            #print("Cannot create CSV file for " + str(bet))
            #print(e)
    #print(data_handling.save_data_player(bet[0]))






# # Make sure all strings are in lower case.
# all_bets = [[string.lower() for string in bet] for bet in all_bets]