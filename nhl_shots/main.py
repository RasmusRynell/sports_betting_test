import Settings
import implementations.data_handlers.csv_handler as csv_handler
import implementations.data_handlers.nhl_handler as nhl_handler
import implementations.data_handlers.player_handler as player_handler
import implementations.data_handlers.old_bets_handler as old_bets_handler
from datetime import timedelta
import argh


def playerDatabase(populate=False, update=False, test=False):
    if not Settings.init_done:
        Settings.init()
    
    have_to_save = False
    if populate:
        nhl_handler.populate_db()
        have_to_save = True
    if update:
        nhl_handler.update_db()
        have_to_save = True

    if test:
        Settings.print_json(player_handler.generate_data(2019020001, 8479318, 10, 9))

    if have_to_save:
        Settings.db.save()
        Settings.api.save()


def betsDatabase(allBets=False, startDate="", endDate="", spesDate="", p=False):
    if not Settings.init_done:
        Settings.init()
    
    have_to_save = False
    if allBets:
        if startDate == "":
            startDate = "2020-12-12"
        if endDate == "":
            endDate = "2025-12-12"
        currDate_date = Settings.string_to_standard_datetime(startDate+"T00:00:00Z")
        endDate_date = Settings.string_to_standard_datetime(endDate+"T00:00:00Z")


        tot = 0
        while (currDate_date != endDate_date):
            tot += old_bets_handler.read_new_bets(str(currDate_date.date()))
            currDate_date += timedelta(days=1)

        print(str(tot) + " bets added")

        have_to_save = True

    elif spesDate != "":
        print(str(old_bets_handler.read_new_bets(spesDate)) + " bets added")
        have_to_save = True

    if p:
        print("Bets: " + str(len(Settings.db.old_bets)))

    if have_to_save:
        Settings.db.save()
        Settings.api.save()


def generateTrainingData(allBets=False, startDate="", endDate="", spesDate=""):
    if not Settings.init_done:
        Settings.init()


    if allBets:
        if startDate == "":
            startDate = "2020-12-12"
        if endDate == "":
            endDate = "2025-12-12"
        startDate_date = Settings.string_to_standard_datetime(startDate+"T00:00:00Z")
        endDate_date = Settings.string_to_standard_datetime(endDate+"T00:00:00Z")

        print("{} files generated".format(csv_handler.generateTrainingDataFromDates(startDate_date, endDate_date)))

    elif spesDate != "":
        currDate_date = Settings.string_to_standard_datetime(spesDate+"T00:00:00Z")
        print("{} files generated".format(csv_handler.generateTrainingDataFromDates(currDate_date)))




if __name__ == "__main__":
    parser=argh.ArghParser()
    parser.add_commands([playerDatabase, betsDatabase, generateTrainingData])
    parser.dispatch()