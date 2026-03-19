import sqlite3
import pandas as pd



class StatisticsService:
    DB_PATH = "d:/eLearn/Projects/bgScores/bgScore.db"

    @classmethod
    def _get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)
    
    @classmethod
    def total_sessions(cls):
        conn = cls._get_connection()
        df = pd.read_sql_query("SELECT * FROM gamesessions", conn)
        conn.close()
        return len(df)

    @classmethod
    def total_players(cls):
        conn = cls._get_connection()
        df = pd.read_sql_query("SELECT * FROM players", conn)
        conn.close()
        return len(df)

    @classmethod
    def most_played_games(cls, limit=5):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT g.title
            FROM gamesessions gs
            JOIN games g ON gs.game_id = g.id
        """, conn)
        conn.close()

        if df.empty:
            return pd.Series(dtype="int64")

        return df["title"].value_counts().head(limit)

    @classmethod
    def most_active_players(cls, limit=5):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT p.name
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
        """, conn)
        conn.close()

        if df.empty:
            return pd.Series(dtype="int64")

        return df["name"].value_counts().head(limit)

    @classmethod
    def best_players_by_win_rate(cls, limit=5):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT p.name, ps.player_standing
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
        """, conn)
        conn.close()

        if df.empty:
            return pd.Series(dtype="float64")

        grouped = df.groupby("name").agg(
            games_played=("player_standing", "count"),
            wins=("player_standing", lambda x: (x == 1).sum())
        )

        grouped["win_rate"] = (grouped["wins"] / grouped["games_played"]) * 100

        return grouped["win_rate"].sort_values(ascending=False).head(limit)

    @classmethod
    def total_playtime_per_game(cls, limit=5):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT g.title, gs.game_duration
            FROM gamesessions gs
            JOIN games g ON gs.game_id = g.id
        """, conn)
        conn.close()

        if df.empty:
            return pd.Series(dtype="int64")

        return (
            df.groupby("title")["game_duration"]
            .sum()
            .sort_values(ascending=False)
            .head(limit)
        )

    @classmethod
    def average_score_per_player(cls, limit=5):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT p.name, ps.player_score
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
        """, conn)
        conn.close()

        if df.empty:
            return pd.Series(dtype="float64")

        return (
            df.groupby("name")["player_score"]
            .mean()
            .sort_values(ascending=False)
            .head(limit)
        )