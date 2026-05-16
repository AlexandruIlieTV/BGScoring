from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "bgScore.db"


class DashboardRepository:
    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        return connection

    def get_dashboard_payload(self) -> dict:
        return {
            "summary": self.get_summary(),
            "highlights": self.get_highlights(),
            "recent_sessions": self.get_recent_sessions(limit=5),
            "top_games": self.get_game_spotlight(limit=6),
            "top_players": self.get_player_spotlight(limit=6),
            "timeline": self.get_monthly_activity(limit=8),
            "player_names": self.get_player_names(),
            "game_titles": self.get_game_titles(),
            "player_catalog": self.get_player_catalog(),
            "game_catalog": self.get_game_catalog(),
        }

    def get_player_names(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name FROM players ORDER BY name ASC"
            ).fetchall()

        return [row["name"] for row in rows]

    def get_game_titles(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT title FROM games ORDER BY title ASC"
            ).fetchall()

        return [row["title"] for row in rows]

    def get_player_catalog(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, name FROM players ORDER BY name ASC"
            ).fetchall()

        return [dict(row) for row in rows]

    def get_game_catalog(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, min_players, max_players, game_theme, year_of_release
                FROM games
                ORDER BY title ASC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_summary(self) -> dict:
        query = """
            SELECT
                (SELECT COUNT(*) FROM games) AS total_games,
                (SELECT COUNT(*) FROM players) AS total_players,
                (SELECT COUNT(*) FROM gamesessions) AS total_sessions,
                (SELECT COALESCE(SUM(game_duration), 0) FROM gamesessions) AS total_minutes,
                (
                    SELECT COALESCE(AVG(player_count), 0)
                    FROM (
                        SELECT COUNT(*) AS player_count
                        FROM playersessions
                        GROUP BY session_id
                    )
                ) AS average_table_size
        """

        with self._connect() as connection:
            row = connection.execute(query).fetchone()

        total_minutes = row["total_minutes"] or 0

        return {
            "total_games": row["total_games"],
            "total_players": row["total_players"],
            "total_sessions": row["total_sessions"],
            "total_hours": round(total_minutes / 60, 1),
            "average_table_size": round(row["average_table_size"] or 0, 1),
        }

    def get_highlights(self) -> dict:
        with self._connect() as connection:
            busiest_game = connection.execute(
                """
                SELECT g.title, COUNT(*) AS sessions
                FROM gamesessions gs
                JOIN games g ON g.id = gs.game_id
                GROUP BY g.id, g.title
                ORDER BY sessions DESC, g.title ASC
                LIMIT 1
                """
            ).fetchone()

            most_active_player = connection.execute(
                """
                SELECT
                    p.name,
                    COUNT(*) AS plays,
                    SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END) AS wins
                FROM playersessions ps
                JOIN players p ON p.id = ps.player_id
                GROUP BY p.id, p.name
                ORDER BY plays DESC, p.name ASC
                LIMIT 1
                """
            ).fetchone()

            latest_session = connection.execute(
                """
                SELECT
                    gs.id,
                    g.title,
                    gs.session_date,
                    gs.game_duration,
                    COUNT(ps.player_id) AS players
                FROM gamesessions gs
                JOIN games g ON g.id = gs.game_id
                LEFT JOIN playersessions ps ON ps.session_id = gs.id
                GROUP BY gs.id, g.title, gs.session_date, gs.game_duration
                ORDER BY gs.session_date DESC, gs.id DESC
                LIMIT 1
                """
            ).fetchone()

        return {
            "busiest_game": dict(busiest_game) if busiest_game else None,
            "most_active_player": dict(most_active_player) if most_active_player else None,
            "latest_session": dict(latest_session) if latest_session else None,
        }

    def get_recent_sessions(self, limit: int = 10) -> list[dict]:
        query = """
            SELECT
                gs.id,
                g.title,
                gs.session_date,
                gs.game_duration,
                COUNT(ps.player_id) AS players,
                GROUP_CONCAT(p.name, ', ') AS roster
            FROM gamesessions gs
            JOIN games g ON g.id = gs.game_id
            LEFT JOIN playersessions ps ON ps.session_id = gs.id
            LEFT JOIN players p ON p.id = ps.player_id
            GROUP BY gs.id, g.title, gs.session_date, gs.game_duration
            ORDER BY gs.session_date DESC, gs.id DESC
            LIMIT ?
        """

        with self._connect() as connection:
            rows = connection.execute(query, (limit,)).fetchall()

        return [dict(row) for row in rows]

    def get_game_spotlight(self, limit: int = 6) -> list[dict]:
        query = """
            SELECT
                g.title,
                g.game_theme,
                g.year_of_release,
                COUNT(gs.id) AS sessions,
                COALESCE(SUM(gs.game_duration), 0) AS total_minutes,
                ROUND(AVG(gs.game_duration), 1) AS avg_duration
            FROM games g
            LEFT JOIN gamesessions gs ON gs.game_id = g.id
            GROUP BY g.id, g.title, g.game_theme, g.year_of_release
            ORDER BY sessions DESC, g.title ASC
            LIMIT ?
        """

        with self._connect() as connection:
            rows = connection.execute(query, (limit,)).fetchall()

        return [dict(row) for row in rows]

    def get_player_spotlight(self, limit: int = 6) -> list[dict]:
        query = """
            SELECT
                p.name,
                COUNT(ps.session_id) AS plays,
                SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END) AS wins,
                ROUND(AVG(ps.player_score), 1) AS average_score,
                ROUND(
                    100.0 * SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(ps.session_id), 0),
                    1
                ) AS win_rate
            FROM players p
            LEFT JOIN playersessions ps ON ps.player_id = p.id
            GROUP BY p.id, p.name
            ORDER BY plays DESC, p.name ASC
            LIMIT ?
        """

        with self._connect() as connection:
            rows = connection.execute(query, (limit,)).fetchall()

        return [dict(row) for row in rows]

    def get_monthly_activity(self, limit: int = 8) -> list[dict]:
        query = """
            SELECT
                substr(session_date, 1, 7) AS month,
                COUNT(*) AS sessions,
                COALESCE(SUM(game_duration), 0) AS minutes
            FROM gamesessions
            GROUP BY substr(session_date, 1, 7)
            ORDER BY month DESC
            LIMIT ?
        """

        with self._connect() as connection:
            rows = connection.execute(query, (limit,)).fetchall()

        timeline = [dict(row) for row in rows]
        timeline.reverse()
        return timeline

    def get_player_details(self, player_name: str) -> dict | None:
        with self._connect() as connection:
            overview = connection.execute(
                """
                SELECT
                    p.name,
                    COUNT(ps.session_id) AS total_plays,
                    SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END) AS wins,
                    ROUND(
                        100.0 * SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END)
                        / NULLIF(COUNT(ps.session_id), 0),
                        1
                    ) AS win_rate,
                    ROUND(AVG(ps.player_score), 1) AS average_score,
                    MAX(ps.player_score) AS best_score
                FROM players p
                LEFT JOIN playersessions ps ON ps.player_id = p.id
                WHERE p.name = ?
                GROUP BY p.id, p.name
                """,
                (player_name,),
            ).fetchone()

            if not overview:
                return None

            favorite_game = connection.execute(
                """
                SELECT g.title, COUNT(*) AS plays
                FROM playersessions ps
                JOIN gamesessions gs ON gs.id = ps.session_id
                JOIN games g ON g.id = gs.game_id
                JOIN players p ON p.id = ps.player_id
                WHERE p.name = ?
                GROUP BY g.id, g.title
                ORDER BY plays DESC, g.title ASC
                LIMIT 1
                """,
                (player_name,),
            ).fetchone()

            best_game = connection.execute(
                """
                SELECT
                    g.title,
                    COUNT(*) AS plays,
                    SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END) AS wins,
                    ROUND(
                        100.0 * SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END)
                        / NULLIF(COUNT(*), 0),
                        1
                    ) AS win_rate
                FROM playersessions ps
                JOIN gamesessions gs ON gs.id = ps.session_id
                JOIN games g ON g.id = gs.game_id
                JOIN players p ON p.id = ps.player_id
                WHERE p.name = ?
                GROUP BY g.id, g.title
                HAVING COUNT(*) >= 3
                ORDER BY win_rate DESC, plays DESC, g.title ASC
                LIMIT 1
                """,
                (player_name,),
            ).fetchone()

            recent_sessions = connection.execute(
                """
                SELECT
                    gs.session_date,
                    g.title,
                    ps.player_score,
                    ps.player_standing
                FROM playersessions ps
                JOIN gamesessions gs ON gs.id = ps.session_id
                JOIN games g ON g.id = gs.game_id
                JOIN players p ON p.id = ps.player_id
                WHERE p.name = ?
                ORDER BY gs.session_date DESC, gs.id DESC
                LIMIT 6
                """,
                (player_name,),
            ).fetchall()

            score_records = connection.execute(
                """
                WITH score_records AS (
                    SELECT g.id AS game_id, g.title, MAX(ps.player_score) AS max_score
                    FROM playersessions ps
                    JOIN gamesessions gs ON gs.id = ps.session_id
                    JOIN games g ON g.id = gs.game_id
                    WHERE ps.player_score IS NOT NULL
                    GROUP BY g.id, g.title
                )
                SELECT sr.title, sr.max_score AS score
                FROM score_records sr
                JOIN gamesessions gs ON gs.game_id = sr.game_id
                JOIN playersessions ps ON ps.session_id = gs.id
                JOIN players p ON p.id = ps.player_id
                WHERE p.name = ? AND ps.player_score = sr.max_score
                GROUP BY sr.game_id, sr.title, sr.max_score
                ORDER BY sr.title ASC
                """,
                (player_name,),
            ).fetchall()

        return {
            "overview": dict(overview),
            "favorite_game": dict(favorite_game) if favorite_game else None,
            "best_game": dict(best_game) if best_game else None,
            "recent_sessions": [dict(row) for row in recent_sessions],
            "score_records": [dict(row) for row in score_records],
        }

    def get_game_details(self, game_title: str) -> dict | None:
        with self._connect() as connection:
            overview = connection.execute(
                """
                SELECT
                    g.title,
                    g.game_theme,
                    g.year_of_release,
                    g.min_players,
                    g.max_players,
                    (
                        SELECT COUNT(*)
                        FROM gamesessions gs_count
                        WHERE gs_count.game_id = g.id
                    ) AS total_sessions,
                    (
                        SELECT COALESCE(SUM(gs_sum.game_duration), 0)
                        FROM gamesessions gs_sum
                        WHERE gs_sum.game_id = g.id
                    ) AS total_minutes,
                    (
                        SELECT ROUND(AVG(gs_avg.game_duration), 1)
                        FROM gamesessions gs_avg
                        WHERE gs_avg.game_id = g.id
                    ) AS average_duration,
                    ROUND(AVG(ps.player_score), 1) AS average_score
                FROM games g
                LEFT JOIN gamesessions gs ON gs.game_id = g.id
                LEFT JOIN playersessions ps ON ps.session_id = gs.id
                WHERE g.title = ?
                GROUP BY g.id, g.title, g.game_theme, g.year_of_release, g.min_players, g.max_players
                """,
                (game_title,),
            ).fetchone()

            if not overview:
                return None

            most_frequent_player = connection.execute(
                """
                SELECT p.name, COUNT(*) AS plays
                FROM playersessions ps
                JOIN players p ON p.id = ps.player_id
                JOIN gamesessions gs ON gs.id = ps.session_id
                JOIN games g ON g.id = gs.game_id
                WHERE g.title = ?
                GROUP BY p.id, p.name
                ORDER BY plays DESC, p.name ASC
                LIMIT 1
                """,
                (game_title,),
            ).fetchone()

            best_player = connection.execute(
                """
                SELECT
                    p.name,
                    COUNT(*) AS plays,
                    SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END) AS wins,
                    ROUND(
                        100.0 * SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END)
                        / NULLIF(COUNT(*), 0),
                        1
                    ) AS win_rate
                FROM playersessions ps
                JOIN players p ON p.id = ps.player_id
                JOIN gamesessions gs ON gs.id = ps.session_id
                JOIN games g ON g.id = gs.game_id
                WHERE g.title = ?
                GROUP BY p.id, p.name
                HAVING COUNT(*) >= 3
                ORDER BY win_rate DESC, plays DESC, p.name ASC
                LIMIT 1
                """,
                (game_title,),
            ).fetchone()

            recent_sessions = connection.execute(
                """
                SELECT
                    gs.session_date,
                    gs.game_duration,
                    COUNT(ps.player_id) AS players,
                    GROUP_CONCAT(p.name, ', ') AS roster
                FROM gamesessions gs
                LEFT JOIN playersessions ps ON ps.session_id = gs.id
                LEFT JOIN players p ON p.id = ps.player_id
                JOIN games g ON g.id = gs.game_id
                WHERE g.title = ?
                GROUP BY gs.id, gs.session_date, gs.game_duration
                ORDER BY gs.session_date DESC, gs.id DESC
                LIMIT 6
                """,
                (game_title,),
            ).fetchall()

            leaderboard = connection.execute(
                """
                SELECT
                    p.name,
                    COUNT(*) AS plays,
                    SUM(CASE WHEN ps.player_standing = 1 THEN 1 ELSE 0 END) AS wins,
                    ROUND(AVG(ps.player_score), 1) AS average_score
                FROM playersessions ps
                JOIN players p ON p.id = ps.player_id
                JOIN gamesessions gs ON gs.id = ps.session_id
                JOIN games g ON g.id = gs.game_id
                WHERE g.title = ?
                GROUP BY p.id, p.name
                ORDER BY wins DESC, average_score DESC, plays DESC, p.name ASC
                LIMIT 8
                """,
                (game_title,),
            ).fetchall()

        return {
            "overview": dict(overview),
            "most_frequent_player": dict(most_frequent_player) if most_frequent_player else None,
            "best_player": dict(best_player) if best_player else None,
            "recent_sessions": [dict(row) for row in recent_sessions],
            "leaderboard": [dict(row) for row in leaderboard],
        }

    def add_player(self, name: str) -> dict:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Player name is required.")

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id FROM players WHERE lower(name) = lower(?)",
                (clean_name,),
            ).fetchone()
            if existing:
                raise ValueError("A player with this name already exists.")

            cursor = connection.execute(
                "INSERT INTO players (name) VALUES (?)",
                (clean_name,),
            )
            connection.commit()

        return {"id": cursor.lastrowid, "name": clean_name}

    def add_game(
        self,
        title: str,
        min_players: int,
        max_players: int,
        game_theme: str,
        year_of_release: int | str,
    ) -> dict:
        clean_title = title.strip()
        clean_theme = game_theme.strip()

        if not clean_title:
            raise ValueError("Game title is required.")
        if min_players <= 0:
            raise ValueError("Minimum players must be greater than 0.")
        if max_players < min_players:
            raise ValueError("Maximum players must be greater than or equal to minimum players.")

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id FROM games WHERE lower(title) = lower(?)",
                (clean_title,),
            ).fetchone()
            if existing:
                raise ValueError("A game with this title already exists.")

            cursor = connection.execute(
                """
                INSERT INTO games (title, min_players, max_players, game_theme, year_of_release)
                VALUES (?, ?, ?, ?, ?)
                """,
                (clean_title, min_players, max_players, clean_theme, str(year_of_release)),
            )
            connection.commit()

        return {
            "id": cursor.lastrowid,
            "title": clean_title,
            "min_players": min_players,
            "max_players": max_players,
        }

    def add_session(
        self,
        game_title: str,
        session_date: str,
        game_duration: int,
        players: list[dict],
    ) -> dict:
        clean_title = game_title.strip()
        clean_date = session_date.strip()

        if not clean_title:
            raise ValueError("Game title is required.")
        if not clean_date:
            raise ValueError("Session date is required.")
        if game_duration <= 0:
            raise ValueError("Game duration must be greater than 0.")
        if not players:
            raise ValueError("At least one player is required.")

        normalized_players = []
        used_names: set[str] = set()
        for entry in players:
            name = str(entry.get("name", "")).strip()
            if not name:
                continue
            if name.lower() in used_names:
                raise ValueError("The same player cannot be selected twice.")
            used_names.add(name.lower())

            try:
                score = int(entry.get("score"))
            except (TypeError, ValueError):
                raise ValueError(f"Invalid score for player {name}.")

            normalized_players.append({"name": name, "score": score})

        if not normalized_players:
            raise ValueError("At least one valid player entry is required.")

        with self._connect() as connection:
            game = connection.execute(
                """
                SELECT id, title, min_players, max_players
                FROM games
                WHERE lower(title) = lower(?)
                """,
                (clean_title,),
            ).fetchone()
            if not game:
                raise ValueError("Selected game was not found.")

            if not (game["min_players"] <= len(normalized_players) <= game["max_players"]):
                raise ValueError(
                    f"Player count must be between {game['min_players']} and {game['max_players']} for this game."
                )

            player_ids: list[dict] = []
            for entry in normalized_players:
                player = connection.execute(
                    "SELECT id, name FROM players WHERE lower(name) = lower(?)",
                    (entry["name"],),
                ).fetchone()
                if not player:
                    raise ValueError(f"Player {entry['name']} was not found.")
                player_ids.append({"id": player["id"], "name": player["name"], "score": entry["score"]})

            cursor = connection.execute(
                """
                INSERT INTO gamesessions (game_id, session_date, game_duration)
                VALUES (?, ?, ?)
                """,
                (game["id"], clean_date, game_duration),
            )
            session_id = cursor.lastrowid

            standings = sorted(
                player_ids,
                key=lambda item: (-item["score"], item["name"].lower()),
            )

            for index, entry in enumerate(standings, start=1):
                connection.execute(
                    """
                    INSERT INTO playersessions (session_id, player_id, player_score, player_standing)
                    VALUES (?, ?, ?, ?)
                    """,
                    (session_id, entry["id"], entry["score"], index),
                )

            connection.commit()

        return {"id": session_id, "game_title": game["title"], "session_date": clean_date}
