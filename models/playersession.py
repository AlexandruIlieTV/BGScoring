# A player session will have the session id, the player id, the score and the final standing

class PlayerSession:
    def __init__(
        self,
        session_id: int,
        player_id: int,
        player_score: int,
        player_standing: int
    ):
        self.session_id = session_id
        self.player_id = player_id
        self.player_score = player_score
        self.player_standing = player_standing

    def __repr__(self):
        return f"PlayerSession({self.session_id}, {self.player_id}, {self.player_score}, {self.player_standing})"