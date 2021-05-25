from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Time, Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Person(Base):
    __tablename__ = "person"

    id = Column('id', Integer, primary_key=True)
    fullName = Column('fullName', String(50))
    firstName = Column('firstName', String(50))
    lastName = Column('lastName', String(50))
    currentTeamId = Column('currentTeamId', Integer, ForeignKey('team.id'))
    primaryPositionCode = Column('primaryPositionCode', Integer)
    positionCode = Column('positionCode', Integer)


class Team(Base):
    __tablename__ = "team"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50))


class Game(Base):
    __tablename__ = "game"

    gamePk = Column('gamePk', Integer, primary_key=True)
    gameType = Column('gameType', String(2))
    season = Column('season', String(8))
    gameDate = Column('gameDate', DateTime)

    abstractGameState = Column('abstractGameState', String(20))
    codedGameState = Column('codedGameState', Integer)
    detailedState = Column('detailedState', String(20))
    statusCode = Column('statusCode', Integer)
    startTimeTBD = Column('startTimeTBD', Boolean)

    homeTeamId = Column('homeTeamId', Integer, ForeignKey('team.id'))
    awayTeamId = Column('awayTeamId', Integer, ForeignKey('team.id'))


class teamStats(Base):
    __tablename__ = "teamStats"

    gamePk = Column('gamePk', Integer, ForeignKey('game.gamePk'), primary_key=True)
    teamId = Column('teamId', Integer, ForeignKey('team.id'), primary_key=True)

    goals = Column('goals', Integer)
    pim = Column('pim', Integer)
    shots = Column('shots', Integer)
    powerPlayPercentage = Column('powerPlayPercentage', Float)
    powerPlayGoals = Column('powerPlayGoals', Float)
    powerPlayOpportunities = Column('powerPlayOpportunities', Float)
    faceOffWinPercentage = Column('faceOffWinPercentage', Float)
    blocked = Column('blocked', Integer)
    takeaways = Column('takeaways', Integer)
    giveaways = Column('giveaways', Integer)
    hits = Column('hits', Integer)

    wins = Column('wins', Integer)
    losses = Column('losses', Integer)
    ot = Column('ot', Integer)
    leagueRecordType = Column('leagueRecordType', String(50))
    score = Column('score', Integer)



class skaterStats(Base):
    __tablename__ = "skaterStats"

    playerId = Column('playerId', Integer, ForeignKey('person.id'), primary_key=True)
    gamePk = Column('gamePk', Integer, ForeignKey('game.gamePk'), primary_key=True)
    currentTeamId = Column('currentTeamId', Integer)
    position = Column('position', Integer)

    timeOnIce = Column('timeOnIce', Time)
    assists = Column('assists', Integer)
    goals = Column('goals', Integer)
    shots = Column('shots', Integer)
    hits = Column('hits', Integer)
    powerPlayGoals = Column('powerPlayGoals', Integer)
    powerPlayAssists = Column('powerPlayAssists', Integer)
    penaltyMinutes = Column('penaltyMinutes', Integer)
    faceOffWins = Column('faceOffWins', Integer)
    faceoffTaken = Column('faceoffTaken', Integer)
    takeaways = Column('takeaways', Integer)
    giveaways = Column('giveaways', Integer)
    shortHandedGoals = Column('shortHandedGoals', Integer)
    shortHandedAssists = Column('shortHandedAssists', Integer)
    blocked = Column('blocked', Integer)
    plusMinus = Column('plusMinus', Integer)
    evenTimeOnIce = Column('evenTimeOnIce', Time)
    powerPlayTimeOnIce = Column('powerPlayTimeOnIce', Time)
    shortHandedTimeOnIce = Column('shortHandedTimeOnIce', Time)


class goalieStats(Base):
    __tablename__ = "goalieStats"

    playerId = Column('playerId', Integer, ForeignKey('person.id'), primary_key=True)
    gamePk = Column('gamePk', Integer, ForeignKey('game.gamePk'), primary_key=True)
    currentTeamId = Column('currentTeamId', Integer)
    position = Column('position', Integer)

    timeOnIce = Column('timeOnIce', Time)
    assists = Column('assists', Integer)
    goals = Column('goals', Integer)
    pim = Column('pim', Integer)
    shots = Column('shots', Integer)
    saves = Column('saves', Integer)
    powerPlaySaves = Column('powerPlaySaves', Integer)
    shortHandedSaves = Column('shortHandedSaves', Integer)
    evenSaves = Column('evenSaves', Integer)
    shortHandedShotsAgainst = Column('shortHandedShotsAgainst', Integer)
    evenShotsAgainst = Column('evenShotsAgainst', Integer)
    powerPlayShotsAgainst = Column('powerPlayShotsAgainst', Integer)
    decision = Column('decision', String(1))
    savePercentage = Column('savePercentage', Float)
    powerPlaySavePercentage = Column('powerPlaySavePercentage', Float)
    evenStrengthSavePercentage = Column('evenStrengthSavePercentage', Float)
