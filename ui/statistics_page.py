import tkinter as tk


class StatisticsPage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(
            self,
            text="Statistici",
            font=("Arial", 18)
        ).pack(pady=30)

        tk.Button(
            self,
            text="Statistici jucător",
            width=25,
            height=2,
            command=self.controller.show_player_statistics
        ).pack(pady=10)

        tk.Button(
            self,
            text="Statistici joc",
            width=25,
            height=2,
            command=self.controller.show_game_statistics
        ).pack(pady=10)

        tk.Button(
            self,
            text="Go back",
            width=20,
            command=self.controller.show_home
        ).pack(pady=20)