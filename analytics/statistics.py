import sqlite3
import pandas as pd

DB_NAME = "d:/eLearn/Projects/bgScores/bgScore.db"

def get_top_5_most_played_games():
    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT g.title, COUNT(gs.id) AS play_count
        FROM gamesessions gs
        JOIN games g ON gs.game_id = g.id
        GROUP BY g.id, g.title
        ORDER BY play_count DESC
        LIMIT 5
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def get_leaderboard_for_game(game_title):
    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT p.name, ps.player_score
        FROM playersessions ps
        JOIN players p ON ps.player_id = p.id
        JOIN gamesessions gs ON ps.session_id = gs.id
        JOIN games g ON gs.game_id = g.id
        WHERE g.title = ?
        ORDER BY ps.player_score DESC
    """

    df = pd.read_sql_query(query, conn, params=(game_title,))
    conn.close()

    return df

def get_all_games():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT title FROM games", conn)
    conn.close()
    return df