import Settings
import implementations.data_handlers.player_handler as player_handler
import os
import csv
import psutil



def create_csv(bet, path = "", path_for_one_file = ""):
    try:
        name = bet["player_name"]
        player_id = bet["player_id"]

        headers, stats_for_player = player_handler.generate_training_data(player_id)

        if not path:
            path = "./data/td/pp_" + str(name) + ".csv"
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

    return path
