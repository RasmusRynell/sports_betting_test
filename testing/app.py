import sys
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from models import *
from gameHandler import *



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

    if sys.argv[1] == 'a':
        fill_all_games_from_season(session, "20202021")
    #elif sys.argv[1] == 'b':
    print_test(session)

    session.commit()
    session.close()
