from models.bets_models import *
from models.nhl_models import *
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, or_, not_, asc, desc
import pandas as pd
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.orm import aliased
import csv

def generate_data_for(player_id, nhl_session, path=None):
    PlayerTeamStats = aliased(TeamStats)
    OppTeamStats = aliased(TeamStats)
    query = (
        select(SkaterStats, Game, PlayerTeamStats, OppTeamStats)
        .where(SkaterStats.playerId == player_id)
        .join(Game, SkaterStats.gamePk == Game.gamePk)
        .join(PlayerTeamStats, and_(SkaterStats.gamePk == PlayerTeamStats.gamePk, PlayerTeamStats.teamId == SkaterStats.team))
        .join(OppTeamStats, and_(SkaterStats.gamePk == OppTeamStats.gamePk, OppTeamStats.teamId != SkaterStats.team))
        .order_by(asc(Game.gameDate))
    )
    playerStatsForGames = pd.read_sql(query, nhl_session.bind)

    playerStatsForGames.columns = [u + "_SkaterStats" for u in SkaterStats.__table__.columns.keys()]\
                                + [u + "_Game" for u in Game.__table__.columns.keys()] \
                                + [u + "_PlayerTeamStats" for u in PlayerTeamStats.__table__.columns.keys()] \
                                + [u + "_OppTeamStats" for u in OppTeamStats.__table__.columns.keys()]

    if path:
        stats_csv = playerStatsForGames.to_csv(path, sep=',', encoding='utf-8', index=False)
        return path
    return playerStatsForGames


def add_games_back(df, games_to_go_back, path=None):

    df_total = pd.DataFrame()
    for i in range(games_to_go_back):
        dfc = df.copy()
        dfc = dfc.shift(periods=1)
        dfc.columns = [u + "_{}_games_back".format(i) for u in dfc.head()]
        df_total = pd.concat([df_total, dfc], axis=1)

    df = pd.concat([df, df_total], axis=1)

    if path:
        stats_csv = df.to_csv(path, sep=',', encoding='utf-8', index=False)
        return path
    return df
