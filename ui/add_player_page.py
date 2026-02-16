import tkinter as tk
from db.repositories import PlayerRepository


class AddPlayerPage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(self, text="Adaugă jucător", font=("Arial", 16)).pack(pady=20)

        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.pack(pady=10)

        tk.Button(
            self,
            text="Salvează",
            command=self.save_player
        ).pack(pady=10)

        tk.Button(
            self,
            text="Înapoi",
            command=self.controller.show_home
        ).pack(pady=20)

    def save_player(self):
        name = self.name_entry.get()
        if name:
            PlayerRepository.add(name)
            self.name_entry.delete(0, tk.END)