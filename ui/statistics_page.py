import tkinter as tk

class StatisticsPage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(self, text="Statistici", font=("Arial", 16)).pack(pady=15)

        tk.Button(
            self,
            text="Cele mai jucate jocuri",
            width=25,
            command=self.show_most_played
        ).pack(pady=5)

        tk.Button(
            self,
            text="Top scoruri",
            width=25,
            command=self.show_top_scores
        ).pack(pady=5)

        tk.Button(
            self,
            text="Înapoi",
            width=25,
            command=self.controller.show_home
        ).pack(pady=15)