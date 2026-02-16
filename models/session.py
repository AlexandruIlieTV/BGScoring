from datetime import datetime

class GameSession:
    def __init__(
        self,
        id: int,
        game_id: int,
        session_date: datetime,
        game_duration: int
    ):
        self.id = id
        self.game_id = game_id
        self.session_date = session_date
        self.game_duration = game_duration  # minute

    def __repr__(self):
        return f"GameSession({self.id}, {self.game_id}, {self.session_date}, {self.game_duration})"