import sys
import glob
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from models.bets_models import *
from models.nhl_models import *
from bets_handler import *
from nhl_handler import *
from tqdm import tqdm
import csv




if __name__ == "__main__":
    # Create engines
    engine_bets = create_engine('sqlite:///databases/bets.db', echo=False, future=True)
    engine_nhl = create_engine('sqlite:///databases/testing.db', echo=True, future=True)

    # Create all tables
    Base_bets.metadata.create_all(bind=engine_bets)
    Base_nhl.metadata.create_all(bind=engine_nhl)

    # Create session factory
    Session_bets = sessionmaker(bind=engine_bets)
    Session_nhl = sessionmaker(bind=engine_nhl)

    # Create specific session
    bet_session = Session_bets()

    # Create specific session
    nhl_session = Session_nhl()

    # fill_teams_and_persons(nhl_session)
    # for season in tqdm(range(2010, 2021)):
    #    fill_all_games_from_season(nhl_session, str(season) + str(season+1))


    with open("./nicknames/player_nicknames.csv", 'r') as f:
       datareader = csv.reader(f)
       for row in datareader:
           add_nickname(row[1], row[0], nhl_session)



    # Loop though all files
    #os.chdir("./saved_bets")
    #for file in glob.glob("*"):
    #    add_file_to_db(file, nhl_session, bet_session)


    bet_session.commit()
    bet_session.close()

    nhl_session.commit()
    nhl_session.close()
