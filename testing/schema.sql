
DROP TABLE IF EXISTS myTable;


DROP TABLE IF EXISTS team;
CREATE TABLE team (id INTEGER, name VARCHAR(100), link VARCHAR(100), teamName VARCHAR(100), locationName VARCHAR(100), firstYearOfPlay VARCHAR(100),
franchise VARCHAR(100), shortName VARCHAR(100), active BOOLEAN,
PRIMARY KEY(id));


DROP TABLE IF EXISTS person;
CREATE TABLE person (id INTEGER, fName VARCHAR(100), lName VARCHAR(100), birthDate DATETIME, birthPlace VARCHAR(100),
PRIMARY KEY(id));


DROP TABLE IF EXISTS game;
CREATE TABLE game (pk INTEGER, gameType VARCHAR(1), season VARCHAR(8), dateTime DATETIME, statusCode INTEGER, homeTeamId INTEGER, awayTeamId INTEGER,
FOREIGN KEY(homeTeamId) REFERENCES team(id),
FOREIGN KEY(awayTeamId) REFERENCES team(id),
PRIMARY KEY(pk));


DROP TABLE IF EXISTS gameStatus;
CREATE TABLE gameStatus (pk INTEGER, abstractGameState VARCHAR(100), codedGameState INTEGER, detailedState VARCHAR(100), statusCode INTEGER, startTimeTBD BOOLEAN,
FOREIGN KEY(pk) REFERENCES game(pk),
PRIMARY KEY(pk));


DROP TABLE IF EXISTS player;
CREATE TABLE player (pk INTEGER, person INTEGER, currentTeam INTEGER, captain BOOLEAN, rookie BOOLEAN, shootsCatches FLOAT, rosterStatus VARCHAR(1), primaryPosition VARCHAR(1),
FOREIGN KEY(pk) REFERENCES game(pk),
FOREIGN KEY(person) REFERENCES person(id),
PRIMARY KEY(pk, person));


DROP TABLE IF EXISTS skaterStats;
CREATE TABLE skaterStats (pk INTEGER, person INTEGER, team INTEGER, position VARCHAR(1), timeOnIce FLOAT, assists INTEGER, goals INTEGER, shots INTEGER,
hits INTEGER, powerPlayGoals INTEGER, powerPlayAssists INTEGER, penaltyMinutes INTEGER, faceOffWins INTEGER, faceoffTaken INTEGER, takeaways INTEGER,
giveaways INTEGER, shortHandedGoals INTEGER, shortHandedAssist INTEGER, blocked INTEGER, plusMinus INTEGER, evenTimeOnIce FLOAT, powerPlayTimeOnIce FLOAT, shortHandedTimeOnIce FLOAT,
FOREIGN KEY(pk) REFERENCES game(pk),
FOREIGN KEY(person) REFERENCES person(id),
FOREIGN KEY(team) REFERENCES team(id),
PRIMARY KEY(pk, person, team));


DROP TABLE IF EXISTS goalieStats;
CREATE TABLE goalieStats (pk INTEGER, person INTEGER, team INTEGER, position VARCHAR(1), timeOnIce FLOAT, assists INTEGER, goals INTEGER, pim INTEGER,
shots INTEGER, saves INTEGER, powerPlaySaves INTEGER, shortHandedSaves INTEGER, evenSaves INTEGER, evenShotsAgainst INTEGER,
powerPlayShotsAgainst INTEGER, decision VARCHAR(1), savePercentage INTEGER, powerPlayPercentage INTEGER, evenStrengthPercentage INTEGER,
FOREIGN KEY(pk) REFERENCES game(pk),
FOREIGN KEY(person) REFERENCES person(id),
FOREIGN KEY(team) REFERENCES team(id),
PRIMARY KEY(pk, person, team));


DROP TABLE IF EXISTS teamStatsGame;
CREATE TABLE teamStatsGame (pk INTEGER, team INTEGER, score INTEGER, wins INTEGER, losses INTEGER, ots INTEGER, goals INTEGER, pim INTEGER, 
shots INTEGER, powerPlayPercentage FLOAT, powerPlayGoals INTEGER, powerPlayOpportunuties INTEGER, faceOffWinPercentage FLOAT, 
blocked INTEGER, takeaways INTEGER, giveaways INTEGER, hits INTEGER,
FOREIGN KEY(pk) REFERENCES game(pk),
FOREIGN KEY(team) REFERENCES team(id),
PRIMARY KEY(pk, team));


DROP TABLE IF EXISTS bet;
CREATE TABLE bet (gamePk INTEGER, playerId INTEGER, betSite VARCHAR(100), overUnder FLOAT, overOdds FLOAT, underOdds FLOAT,
FOREIGN KEY(gamePk) REFERENCES game(pk),
FOREIGN KEY(playerId) REFERENCES person(id),
PRIMARY KEY(gamePk, playerId, betSite))