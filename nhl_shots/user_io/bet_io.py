import user_io.bet365_io as bet365
import user_io.unibet_io as unibet
import Settings

def get_from_file(path):
    all_games = bet365.get_from_file(path + ".bet365")
    unibet.get_from_file(path + ".unibet", all_games)

    return all_games