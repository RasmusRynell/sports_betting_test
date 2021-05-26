import bet_parsers.parse_betsson as betsson
import bet_parsers.parse_betway as betway
import bet_parsers.parse_unibet as unibet
import bet_parsers.parse_bet365 as bet365
import bet_parsers.parse_wh as wh
import bet_parsers.parse_ss as ss
from models.bets_models import *
from models.nhl_models import *
from datetime import date
from datetime import datetime
from sqlalchemy import func, and_, or_, not_


def add_file_to_db(file, nhl_session, bets_session):
    end = file.split(".")[-1]

    bets = []
    if end == "bet365":
        bets = bet365.read_file(file)
    elif end == "betsson":
        bets = betsson.read_file(file)
    elif end == "betway":
        bets = betway.read_file(file)
    elif end == "unibet":
        bets = unibet.read_file(file)
    elif end == "wh":
        bets = wh.read_file(file)
    elif end == "ss":
        bets = ss.read_file(file)

    for bet in bets:
            add_bet_to_db(bet, nhl_session, bets_session)


def add_bet_to_db(bet, nhl_session, bets_session):
    new_bet = Bet()

    try:
        new_bet.playerId = get_player_id_from_name(bet[1], nhl_session)
        new_bet.homeTeamId = bet[2]
        new_bet.awayTeamId = bet[3]
        new_bet.dateTime = datetime.strptime(bet[0], '%Y-%m-%d')
        new_bet.site = bet[4]
        new_bet.overUnder = str(bet[7]).replace(",", ".")
        new_bet.oddsOver = str(bet[5]).replace(",", ".")
        new_bet.oddsUnder = str(bet[6]).replace(",", ".")

        bets_session.add(new_bet)
    except Exception as e:
        pass


def get_player_id_from_name(name, nhl_session):
    ids = nhl_session.query(Person).filter(func.lower(Person.fullName).contains(func.lower(name))).all()
    if len(ids) == 0:
        ids = nhl_session.query(PersonNicknames).filter(func.lower(PersonNicknames.nickname).contains(func.lower(name))).all()
    
    if len(ids) > 1:
        print("More than one id for:")
        print(name)
        raise "More than one id..."

    if len(ids) == 0:
        print("Cant find a player with that name for:")
        print(name)
        raise "Cant find a player with that name..."

    return ids[0]




def get_team_id_from_name(name, nhl_session):
    return "3"


def add_nickname(name, nickname, nhl_session):
    name = name.replace("\"", "")
    ids = nhl_session.query(Person).filter(func.lower(Person.fullName).contains(func.lower(name))).all()

    if len(ids) > 1:
        print("More than one id for:")
        print(name)
        print(nhl_session.query(Person).filter(func.lower(Person.fullName).contains(func.lower(name))))
        return
        raise "More than one id..."

    if len(ids) == 0:
        print("Cant find a player with that name for:")
        print(name)
        print(nhl_session.query(Person).filter(func.lower(Person.fullName).contains(func.lower(name))))
        return
        raise "Cant find a player with that name..."

    if not nhl_session.query(PersonNicknames).filter(and_(PersonNicknames.personId == ids[0].id, func.lower(PersonNicknames.nickname) == func.lower(nickname))).first():
        new_nickname = PersonNicknames()

        new_nickname.personId = ids[0].id
        new_nickname.nickname = nickname

        nhl_session.add(new_nickname)

