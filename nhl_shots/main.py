import Settings
import implementations.data_handlers.manager as manager
import implementations.data_handlers.nhl_handler as nhl_handler
import implementations.data_handlers.player_handler as player_handler
import implementations.data_handlers.old_bets_handler as old_bets_handler
from datetime import timedelta
import argh


def playerDatabase(populate=False, update=False, printdb=False, printPlayerdb=False):
    Settings.init(True, True)
    
    have_to_save = False
    if populate:
        nhl_handler.populate_db()
        have_to_save = True
    if update:
        nhl_handler.update_db()
        have_to_save = True

    if printdb:
        Settings.print_json(Settings.db.games)
    
    if printPlayerdb:
        Settings.print_json(Settings.db.player_ids)

    if have_to_save:
        Settings.db.save()
        Settings.api.save()


def betsDatabase(allBets=False, startDate="", endDate="", spesDate="", printdb=False, override=False):
    Settings.init(False, True)
    
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
            tot += old_bets_handler.read_new_bets(str(currDate_date.date()), override)
            currDate_date += timedelta(days=1)

        print(str(tot) + " bets added")

        have_to_save = True

    elif spesDate != "":
        print(str(old_bets_handler.read_new_bets(spesDate, override)) + " bets added")
        have_to_save = True

    if printdb:
        Settings.print_json(Settings.db.old_bets)

    if have_to_save:
        Settings.db.save()


def generateTrainingData(allBets=False, startDate="", endDate="", spesDate=""):
    call_func_for_dates(allBets, startDate, endDate, spesDate, manager.generateTrainingDataFromDates)
    Settings.db.save()


def predict(allBets=False, startDate="", endDate="", spesDate=""):
    call_func_for_dates(allBets, startDate, endDate, spesDate, manager.generatePredictionsFromDates)
    Settings.db.save()


def validatePredictions(allBets=False, startDate="", endDate="", spesDate=""):
    call_func_for_dates(allBets, startDate, endDate, spesDate, manager.analyzePredictionsFromDates)
    Settings.db.save()




def call_func_for_dates(allBets, startDate, endDate, spesDate, func):
    Settings.init(False, True)
    if allBets:
        if startDate == "" and endDate == "":
            print("{} generated".format(func()))
        else:
            if startDate == "":
                startDate = "2020-12-12"
            if endDate == "":
                endDate = "2025-12-12"
            startDate_date = Settings.string_to_standard_datetime(startDate+"T00:00:00Z")
            endDate_date = Settings.string_to_standard_datetime(endDate+"T00:00:00Z")

            print("{} generated".format(func(startDate_date, endDate_date)))

    elif spesDate != "":
        currDate_date = Settings.string_to_standard_datetime(spesDate+"T00:00:00Z")
        print("{} generated".format(func(currDate_date)))




if __name__ == "__main__":
    parser=argh.ArghParser()
    parser.add_commands([playerDatabase, betsDatabase, generateTrainingData, predict, validatePredictions])
    parser.dispatch()
