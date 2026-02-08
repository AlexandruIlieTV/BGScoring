# loading in modules
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from db.repositories import PlayerRepository, GameRepository

# creating file path
dbfile = 'd:/eLearn/Projects/bgScores/bgScore.db'
# Create a SQL connection to our SQLite database
con = sqlite3.connect(dbfile)

# creating cursor
cur = con.cursor()

players = PlayerRepository.get_all()
for p in players:
    print(p)

GameRepository.add("Paladins of the West Kingdom", 1, 4, "Medieval", 2019)
games = GameRepository.get_all()
for g in games:
    print(g)

#Testing tkinter
""" def greet():
    user_name = entry.get()
    label_result.config(text=f"Hello, {user_name}!")

#Create the main window
root = tk.Tk()
root.title("Greeting app")
root.geometry("300x150")

#Create a label
label = tk.Label(root, text="Enter your name:")
label.pack(pady=5)

#Create an entry widget
entry = tk.Entry(root)
entry.pack(pady=5)

#Create a button
button = tk.Button(root, text="Greet", command=greet)
button.pack(pady=5)

#Create a label for the result
label_result = tk.Label(root, text="")
label_result.pack(pady=5)

#Start the main loop
root.mainloop() """

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

def getTopScoresForGame(game_id):
    # Getting all entries for a certain game id
    df = pd.read_sql_query('select g.name as Game, p.name as Player, gs.player_score, gs.player_standing ' \
                            'from players p, gamesessions gs, games g' \
                            ' where p.id = gs.player_id and g.id = gs.game_id and gs.game_id= %f order by player_score desc' %(game_id), con)
    
    print(df.head(5))


#getTotalNumberOfPlays()
#getPlayerStats(1)
#getTopScoresForGame(1)


# Be sure to close the connection
con.close()