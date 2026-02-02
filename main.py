# loading in modules
import sqlite3
import pandas as pd
#import sqlalchemy

# creating file path
dbfile = 'd:/eLearn/Projects/bgScores/bgScore.db'
# Create a SQL connection to our SQLite database
con = sqlite3.connect(dbfile)

# creating cursor
cur = con.cursor()

# reading all table names
table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
# here is you table list
#print(table_list)

def getTotalNumberOfPlays():
    # Retrieve all session_id - game_id maps
    df = pd.read_sql_query('select session_id, game_id from gamesessions', con)
    
    # Get unique ids for sessions
    distinctSessionsIds = df['session_id'].unique()
    
    # Dropping duplicates for game_ids to count what are the number of plays for each game_id from the game catalog
    topPlayedGames = df.drop_duplicates()
    topPlayedGames = topPlayedGames['game_id'].value_counts()
    print("Total number of game sessions", len(distinctSessionsIds))
    print(topPlayedGames)

def getPlayerStats(player_id):
    # Getting all entries for a certain player id
    df = pd.read_sql_query('select gs.session_id, g.name as Game, p.name as Player, gs.player_score, gs.player_standing ' \
                            'from players p, gamesessions gs, games g' \
                            ' where p.id = gs.player_id and g.id = gs.game_id and gs.player_id= %f' %(player_id), con)
    
    total_games = len(df)

    # Most played games
    most_played_games = df.value_counts(['Game'])

    # Player standing and rate of win
    standings_stats = df.value_counts(['player_standing'])
    standing_percentages = (
    df['player_standing']
    .value_counts(normalize=True)
    .mul(100)
    .rename('percentage')
    .reset_index()
    .rename(columns={'index': 'player_standing'})
    .sort_values('player_standing')
    )


    # Player standings per game as a percentage
    game_standings_percentages = (
    df
    .groupby('Game')['player_standing']
    .value_counts(normalize=True)
    .mul(100)
    .rename('percentage')
    .reset_index()
    .sort_values(['Game', 'player_standing'])
    )

    pivot = (
    game_standings_percentages
    .pivot(index='Game', columns='player_standing', values='percentage')
    .fillna(0)
    )

    print("--- Most played games ---")
    print(most_played_games)
    print("--- Player standings ---")
    print(standings_stats)
    #print(pivot)
    print(game_standings_percentages)
    #print(df)

def insertGameInCatalog():
    return

def insertPlayer():
    return

def insertGameSession():
    return

#getTotalNumberOfPlays()
getPlayerStats(1)

# Be sure to close the connection
con.close()
