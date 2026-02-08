# A game will have an ID, a name, a min-max player definition and the year of release

class Game:
    def __init__(self, id: int, title: str, min_players: int, max_players: int, game_theme: str, year_of_release: int):
        self.id = id
        self.title = title
        self.min_players = min_players
        self.max_players = max_players
        self.game_theme = game_theme
        self.year_of_release = year_of_release

    def __repr__(self):
        return f"Game({self.title}, {self.min_players}, {self.max_players}, {self.game_theme}, {self.year_of_release})"