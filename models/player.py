# A player will have an id and a name

class Player:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Player({self.id}, {self.name})"