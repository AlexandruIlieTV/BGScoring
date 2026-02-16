from db.database import get_connection
from models.player import Player
from models.game import Game
from models.session import GameSession
from models.playersession import PlayerSession
from datetime import datetime


class PlayerRepository:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM players")
        players = cursor.fetchall()

        conn.close()
        return players

    @staticmethod
    def add(name: str):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO players (name) VALUES (?)",
            (name,)
        )
        conn.commit()
        conn.close()

class GameRepository:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM games")
        games = cursor.fetchall()

        conn.close()
        return games

    @staticmethod
    def add(title, min_p, max_p, game_theme, year_of_release):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO games (title, min_players, max_players, game_theme, year_of_release)
            VALUES (?, ?, ?, ?, ?)
        """, (title, min_p, max_p, game_theme, year_of_release))

        conn.commit()
        conn.close()

    @staticmethod
    def exists(title):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM games WHERE title = ?", (title,))
        result = cursor.fetchone()

        conn.close()

        return result is not None

class GameSessionRepository:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, game_id, session_date, game_duration FROM gamesessions")
        rows = cursor.fetchall()

        conn.close()
        return [GameSession(id=row[0], game_id=row[1], session_date=row[2], game_duration=row[3]) for row in rows]
    
    @staticmethod
    def add(game_id, session_date, game_duration):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gamesessions (game_id, session_date, game_duration)
            VALUES (?, ?, ?)
        """, (game_id, session_date, game_duration))

        session_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return session_id

class PlayerSessionRepository:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT session_id, player_id, player_score, player_standing FROM playersessions")
        rows = cursor.fetchall()

        conn.close()
        return [PlayerSession(session_id=row[0], player_id=row[1], player_score=row[2], player_standing=row[3]) for row in rows]
    
    @staticmethod
    def add(session_id, player_id, player_score, player_standing):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO playersessions (session_id, player_id, player_score, player_standing)
            VALUES (?, ?, ?, ?)
        """, (session_id, player_id, player_score, player_standing))

        conn.commit()
        conn.close()