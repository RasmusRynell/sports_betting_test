import sys
import glob
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from models.bets_models import *
from models.nhl_models import *
from bets_handler import *
from nhl_handler import *
from nhl_gen import *
from tqdm import tqdm
from datetime import date, datetime, timedelta
import csv


def fill_or_update_nhl_db(nhl_session, season=None):
   if not season:
      fill_teams_and_persons(nhl_session)
      for season in tqdm(range(2010, 2021)):
         fill_all_games_from_season(nhl_session, str(season) + str(season+1))
   else:
      fill_all_games_from_season(season)

   nhl_session.commit()

def add_nicknames(nhl_session):
   with open("./nicknames/player_nicknames.csv", encoding='utf-8') as f:
      datareader = csv.reader(f)
      for row in datareader:
         add_person_nickname(row[0], row[1], nhl_session)

   with open("./nicknames/team_nicknames.csv", encoding='utf-8') as f:
      datareader = csv.reader(f)
      for row in datareader:
         add_team_nickname(row[0], row[1], nhl_session)

   nhl_session.commit()

def add_bets(nhl_session, bet_session):
   os.chdir("./saved_bets")
   for file in glob.glob("*"):
      add_file_to_db(file, nhl_session, bet_session)

   bet_session.commit()



if __name__ == "__main__":
   # Create engines
   engine_bets = create_engine('sqlite:///databases/bets.db', echo=False, future=False)
   engine_nhl = create_engine('sqlite:///databases/testing.db', echo=False, future=False)

   # Create all tables
   Base_bets.metadata.create_all(bind=engine_bets)
   Base_nhl.metadata.create_all(bind=engine_nhl)

   # Create session factory
   Session_bets = sessionmaker(bind=engine_bets)
   Session_nhl = sessionmaker(bind=engine_nhl)

   # Create sessions
   bet_session = Session_bets()
   nhl_session = Session_nhl()


   if len(sys.argv) > 1:
      if sys.argv[1] == "add":
         # Add seasons
         fill_or_update_nhl_db(nhl_session)

         # Add nicknames
         add_nicknames(nhl_session)

         # Add all bets
         add_bets(nhl_session, bet_session)

      elif sys.argv[1] == "gen":
         start_time = datetime(2017, 9, 15)
         end_time = datetime.now()
         player_id = 8475167
         add_games_back(generate_data_for(
             player_id, nhl_session), 5, "./csvs/{}".format(player_id))



   bet_session.close()
   nhl_session.close()
