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

    # ---------- Utility lists ----------

    @classmethod
    def get_all_player_names(cls):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT name
            FROM players
            ORDER BY name
        """, conn)
        conn.close()

        if df.empty:
            return []

        return df["name"].tolist()
    
    @classmethod
    def get_all_game_titles(cls):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT title
            FROM games
            ORDER BY title
        """, conn)
        conn.close()

        if df.empty:
            return []

        return df["title"].tolist()

    @classmethod
    def get_games_played_by_player(cls, player_name):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT DISTINCT g.title
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE p.name = ?
            ORDER BY g.title
        """, conn, params=(player_name,))
        conn.close()

        if df.empty:
            return []

        return df["title"].tolist()


    # ---------- Player statistics ----------

    @classmethod
    def get_player_total_games_played(cls, player_name):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT COUNT(*) AS total_games_played
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            WHERE p.name = ?
        """, conn, params=(player_name,))
        conn.close()

        if df.empty:
            return 0

        return int(df.iloc[0]["total_games_played"])

    @classmethod
    def get_player_favourite_game(cls, player_name):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT g.title, COUNT(*) AS times_played
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE p.name = ?
            GROUP BY g.title
            ORDER BY times_played DESC, g.title ASC
            LIMIT 1
        """, conn, params=(player_name,))
        conn.close()

        if df.empty:
            return None

        return {
            "game": df.iloc[0]["title"],
            "times_played": int(df.iloc[0]["times_played"])
        }

    @classmethod
    def get_player_best_game(cls, player_name, min_plays=3):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT g.title, ps.player_standing
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE p.name = ?
        """, conn, params=(player_name,))
        conn.close()

        if df.empty:
            return None

        grouped = df.groupby("title").agg(
            games_played=("player_standing", "count"),
            wins=("player_standing", lambda x: (x == 1).sum())
        )

        grouped = grouped[grouped["games_played"] >= min_plays]

        if grouped.empty:
            return None

        grouped["win_rate"] = (grouped["wins"] / grouped["games_played"]) * 100
        grouped = grouped.sort_values(
            by=["win_rate", "games_played"],
            ascending=[False, False]
        )

        best_game = grouped.iloc[0]

        return {
            "game": grouped.index[0],
            "games_played": int(best_game["games_played"]),
            "wins": int(best_game["wins"]),
            "win_rate": float(best_game["win_rate"])
        }

    @classmethod
    def get_player_score_records(cls, player_name):
        conn = cls._get_connection()

        # Best score ever recorded for each game
        all_scores = pd.read_sql_query("""
            SELECT g.title, p.name, ps.player_score
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE ps.player_score IS NOT NULL
        """, conn)

        conn.close()

        if all_scores.empty:
            return []

        max_scores = all_scores.groupby("title")["player_score"].max().reset_index()
        merged = all_scores.merge(max_scores, on="title", suffixes=("", "_max"))
        records = merged[merged["player_score"] == merged["player_score_max"]]

        player_records = records[records["name"] == player_name][["title", "player_score"]]
        player_records = player_records.drop_duplicates().sort_values("title")

        return [
            {
                "game": row["title"],
                "score": row["player_score"]
            }
            for _, row in player_records.iterrows()
        ]

    @classmethod
    def get_player_average_score_for_game(cls, player_name, game_title):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT ps.player_score
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE p.name = ?
              AND g.title = ?
              AND ps.player_score IS NOT NULL
        """, conn, params=(player_name, game_title))
        conn.close()

        if df.empty:
            return None

        return float(df["player_score"].mean())


    # ---------- Game statistics ----------

    @classmethod
    def get_game_total_sessions(cls, game_title):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT COUNT(*) AS total_sessions
            FROM gamesessions gs
            JOIN games g ON gs.game_id = g.id
            WHERE g.title = ?
        """, conn, params=(game_title,))
        conn.close()

        if df.empty:
            return 0

        return int(df.iloc[0]["total_sessions"])

    @classmethod
    def get_game_most_frequent_player(cls, game_title):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT p.name, COUNT(*) AS times_played
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE g.title = ?
            GROUP BY p.name
            ORDER BY times_played DESC, p.name ASC
            LIMIT 1
        """, conn, params=(game_title,))
        conn.close()

        if df.empty:
            return None

        return {
            "player": df.iloc[0]["name"],
            "times_played": int(df.iloc[0]["times_played"])
        }

    @classmethod
    def get_game_best_player(cls, game_title, min_plays=3):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT p.name, ps.player_standing
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE g.title = ?
        """, conn, params=(game_title,))
        conn.close()

        if df.empty:
            return None

        grouped = df.groupby("name").agg(
            games_played=("player_standing", "count"),
            wins=("player_standing", lambda x: (x == 1).sum())
        )

        grouped = grouped[grouped["games_played"] >= min_plays]

        if grouped.empty:
            return None

        grouped["win_rate"] = (grouped["wins"] / grouped["games_played"]) * 100
        grouped = grouped.sort_values(
            by=["win_rate", "games_played"],
            ascending=[False, False]
        )

        best_player = grouped.iloc[0]

        return {
            "player": grouped.index[0],
            "games_played": int(best_player["games_played"]),
            "wins": int(best_player["wins"]),
            "win_rate": float(best_player["win_rate"])
        }

    @classmethod
    def get_game_score_record(cls, game_title):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT p.name, ps.player_score
            FROM playersessions ps
            JOIN players p ON ps.player_id = p.id
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE g.title = ?
              AND ps.player_score IS NOT NULL
            ORDER BY ps.player_score DESC, p.name ASC
            LIMIT 1
        """, conn, params=(game_title,))
        conn.close()

        if df.empty:
            return None

        return {
            "player": df.iloc[0]["name"],
            "score": df.iloc[0]["player_score"]
        }

    @classmethod
    def get_game_average_score(cls, game_title):
        conn = cls._get_connection()
        df = pd.read_sql_query("""
            SELECT ps.player_score
            FROM playersessions ps
            JOIN gamesessions gs ON ps.session_id = gs.id
            JOIN games g ON gs.game_id = g.id
            WHERE g.title = ?
              AND ps.player_score IS NOT NULL
        """, conn, params=(game_title,))
        conn.close()

        if df.empty:
            return None

        return float(df["player_score"].mean())

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
    def best_players_by_win_rate(cls, limit=5, min_games=10):
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

        grouped = grouped[grouped["games_played"] >= min_games]

        if grouped.empty:
            return pd.Series(dtype="float64")

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