import implementations.data_handlers.bet_parsers.parse_betsson as betsson
import implementations.data_handlers.bet_parsers.parse_betway as betway
import implementations.data_handlers.bet_parsers.parse_unibet as unibet
import implementations.data_handlers.bet_parsers.parse_bet365 as bet365
import implementations.data_handlers.bet_parsers.parse_wh as wh
import implementations.data_handlers.bet_parsers.parse_ss as ss
import implementations.data_handlers.nhl_handler as nhl_handler
from datetime import timedelta
import Settings
from tqdm import tqdm


def read_new_bets(date_string):
    total = 0
    bets = get_from_file(date_string)
    if len(bets) > 0:
        for bet in tqdm(bets, desc="Adding bets for {}".format(date_string)):
            bet.insert(0, match_bet_with_pk(bet))
            if add_bet_to_db(bet):
                total += 1
    return total


def get_from_file(date):
    full_list = []

    full_list.extend(bet365.read_file("./saved_bets/{}.bet365".format(date)))

    full_list.extend(betsson.read_file("./saved_bets/{}.betsson".format(date)))

    full_list.extend(betway.read_file("./saved_bets/{}.betway".format(date)))

    full_list.extend(unibet.read_file("./saved_bets/{}.unibet".format(date)))

    full_list.extend(wh.read_file("./saved_bets/{}.wh".format(date)))

    #full_list.extend(ss.read_file("./saved_bets/{}.ss".format(date)))

    return full_list


def match_bet_with_pk(bet):
    date = Settings.string_to_standard_datetime(str(bet[0]) + "T00:00:00Z")
    season = Settings.date_to_season(date)
    for gamePk in Settings.db.games["seasons"][str(season)]["played"]:
        game = Settings.db.games["games_information"][str(gamePk)]
        game_date = Settings.string_to_standard_datetime(game["date"]) - timedelta(hours=12)
        if str(game_date.date()) == str(bet[0]):
            if nhl_handler.get_team_id(str(bet[2])) == game["teams"]["home"] and \
                nhl_handler.get_team_id(str(bet[3])) == game["teams"]["away"]:
                return game["gamePk"]
    print("Could not find a gamePk for: " + str(bet))


def add_bet_to_db(bet):
    gamePk = bet[0]
    date = bet[1]
    player_name = bet[2]
    home_team_name = bet[3]
    away_team_name = bet[4]
    site = bet[5]
    over = bet[6]
    under = bet[7]
    over_under = ""
    if len(bet) > 7:
        over_under = bet[8]

    if player_name.lower() in Settings.banned_players:
        return False

    player_id = nhl_handler.get_player_id(player_name)
    home_team_id = nhl_handler.get_team_id(home_team_name)
    away_team_id = nhl_handler.get_team_id(away_team_name)

    if not nhl_handler.player_in_game(player_id, gamePk):
        return False

    player_team_id = away_team_id
    opp_team_id = home_team_id
    if nhl_handler.player_in_team(player_id, home_team_id, str(gamePk)):
        player_team_id = home_team_id
        opp_team_id = away_team_id

    if str(player_id) not in Settings.db.old_bets:
        Settings.db.old_bets[str(player_id)] = {
            "player_name": player_name,
            "player_id": player_id,
            "newest_game_date": date,
            "newest_game_gamePk": gamePk,
            "games": {
                str(gamePk): {
                "gamePk": gamePk,
                "date": date,
                "home_team_name": home_team_name,
                "home_team_id": home_team_id,
                "away_team_name": away_team_name,
                "away_team_id": away_team_id,
                "player_team_id": player_team_id,
                "opp_team_id": opp_team_id,
                "bets": {str(site): {
                    "over": over,
                    "under": under,
                    "over_under": over_under
                }}
            }}
        }
    else:
        if str(gamePk) not in Settings.db.old_bets[str(player_id)]["games"]:
            Settings.db.old_bets[str(player_id)]["games"][str(gamePk)] = {
                "gamePk": gamePk,
                "date": date,
                "home_team_name": home_team_name,
                "home_team_id": home_team_id,
                "away_team_name": away_team_name,
                "away_team_id": away_team_id,
                "player_team_id": player_team_id,
                "opp_team_id": opp_team_id,
                "bets": {str(site): {
                    "over": over,
                    "under": under,
                    "over_under": over_under
                }}
            }
        else:
            Settings.db.old_bets[str(player_id)]["games"][str(gamePk)]["bets"][str(site)] = {
                    "over": over,
                    "under": under,
                    "over_under": over_under
                    }
        if Settings.string_to_standard_datetime(Settings.db.old_bets[str(player_id)]["newest_game_date"])\
            < Settings.string_to_standard_datetime(date):
            Settings.db.old_bets[str(player_id)]["newest_game_date"] = date
            Settings.db.old_bets[str(player_id)]["newest_game_gamePk"] = gamePk

    return True
