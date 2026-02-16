import tkinter as tk


class HomePage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(
            self,
            text="Board Game Tracker",
            font=("Arial", 18)
        ).pack(pady=30)

        tk.Button(
            self,
            text="🎮 Înregistrează sesiune",
            width=25,
            height=2,
            command=self.controller.show_add_session
        ).pack(pady=10)

        tk.Button(
            self,
            text="🎲 Adaugă joc",
            width=25,
            height=2,
            command=self.controller.show_add_game
        ).pack(pady=10)

        tk.Button(
            self,
            text="👤 Adaugă jucător",
            width=25,
            height=2,
            command=self.controller.show_add_player
        ).pack(pady=10)

        tk.Button(
        self,
        text="Statistici",
        width=20,
        command=self.controller.show_statistics
        ).pack(pady=5)