from db.database import get_connection
from models.player import Player
from models.game import Game
from models.session import GameSession
from datetime import datetime


class PlayerRepository:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM players")
        rows = cursor.fetchall()

        conn.close()
        return [Player(id=row[0], name=row[1]) for row in rows]

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

        cursor.execute("SELECT id, title, min_players, max_players, game_theme, year_of_release FROM games")
        rows = cursor.fetchall()

        conn.close()
        return [Game(id=row[0], title=row[1], min_players=row[2], max_players=row[3], game_theme=row[4], year_of_release=row[5]) for row in rows]

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