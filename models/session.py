from datetime import datetime

class GameSession:
    def __init__(
        self,
        id: int,
        game_id: int,
        date: datetime,
        duration: int
    ):
        self.id = id
        self.game_id = game_id
        self.date = date
        self.duration = duration  # minute