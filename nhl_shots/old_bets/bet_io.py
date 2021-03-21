import old_bets.parse_betsson as betsson
import old_bets.parse_betway as betway
import old_bets.parse_unibet as unibet
import old_bets.parse_bet365 as bet365
import old_bets.parse_WH as wh
import Settings

def get_from_file(date):
    full_list = []

    #try:
        #full_list.extend(bet365.read_file("./data/old_bets/{}.bet365".format(date)))
    #except:
        #pass

    try:
        full_list.extend(betsson.read_file("./data/old_bets/{}.betsson".format(date)))
    except:
        pass

    try:
        full_list.extend(betway.read_file("./data/old_bets/{}.betway".format(date)))
    except:
        pass

    try:
        full_list.extend(unibet.read_file("./data/old_bets/{}.unibet".format(date)))
    except:
        pass

    try:
        full_list.extend(wh.read_file("./data/old_bets/{}.WH".format(date)))
    except:
        pass

    return full_list