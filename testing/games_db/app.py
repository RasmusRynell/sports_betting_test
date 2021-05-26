import sys
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from models import *
from gameHandler import *
from tqdm import tqdm



# Create engine
#engine = create_engine('sqlite:///:memory:', echo=False, future=True)
engine = create_engine('sqlite:///testing.db', echo=False, future=True)

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session factory
Session = sessionmaker(bind=engine)


if __name__ == "__main__":
    # Create specific session
    session = Session()

    fill_teams_and_persons(session)
    for season in tqdm(range(2010, 2021)):
        fill_all_games_from_season(session, str(season) + str(season+1))

    session.commit()
    session.close()
