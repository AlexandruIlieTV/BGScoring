import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db.repositories import (
    GameRepository,
    PlayerRepository,
    GameSessionRepository,
    PlayerSessionRepository
)

class AddSessionPage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(self, text="Înregistrează sesiune", font=("Arial", 16)).pack(pady=10)

        self.create_form()

    def create_player_section(self):
        container = tk.Frame(self)
        container.pack(pady=10, fill="both", expand=True)

        canvas = tk.Canvas(container, height=200)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        self.players_frame = tk.Frame(canvas)

        self.players_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.players_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.player_rows = []

    def generate_player_rows(self, event=None):
        for widget in self.players_frame.winfo_children():
            widget.destroy()

        self.player_rows.clear()

        game_data = self.games_dict[self.selected_game.get()]
        min_players = game_data[2]
        max_players = game_data[3]

        self.current_max_players = max_players

        all_players = [p[1] for p in self.players]

        # Buton adăugare jucător
        tk.Button(
            self.players_frame,
            text="Adaugă jucător",
            command=lambda: self.add_player_row(all_players)
        ).pack(pady=5)

        for i in range(min_players):
            self.add_player_row(all_players)



    def add_player_row(self, all_players):

        if len(self.player_rows) >= self.current_max_players:
            messagebox.showerror("Eroare", "Ai atins numărul maxim de jucători.")
            return

        row = tk.Frame(self.players_frame)
        row.pack(pady=2)

        tk.Label(row, text=f"Jucător {len(self.player_rows)+1}", width=10).pack(side="left")

        player_var = tk.StringVar()
        player_dropdown = ttk.Combobox(
            row,
            textvariable=player_var,
            values=all_players,
            state="readonly",
            width=15
        )
        player_dropdown.pack(side="left")

        score_entry = tk.Entry(row, width=8)
        score_entry.pack(side="left", padx=5)

        self.player_rows.append((player_var, score_entry))

    def create_form(self):

        # 🔹 Joc
        tk.Label(self, text="Selectează joc:").pack()

        self.games = GameRepository.get_all()
        self.games_dict = {g[1]: g for g in self.games}

        self.selected_game = tk.StringVar()
        self.selected_game.set(list(self.games_dict.keys())[0])

        self.game_combobox = ttk.Combobox(
            self,
            textvariable=self.selected_game,
            values=list(self.games_dict.keys()),
            state="readonly"
        )
        self.game_combobox.pack(pady=5)

        #self.game_combobox.bind("<<ComboboxSelected>>", self.generate_player_rows)

        # 🔹 Jucători
        tk.Label(self, text="Jucători și scoruri:").pack(pady=5)

        self.players = PlayerRepository.get_all()

        self.create_player_section()

        # legăm schimbarea jocului
        game_combobox = ttk.Combobox(
            self,
            textvariable=self.selected_game,
            values=list(self.games_dict.keys()),
            state="readonly"
        )
        game_combobox.pack(pady=5)

        game_combobox.bind("<<ComboboxSelected>>", self.generate_player_rows)

        # generăm inițial
        self.generate_player_rows()

        # 🔹 Data
        self.date_entry = tk.Entry(self)
        self.date_entry.insert(0, str(date.today()))
        self.date_entry.pack(pady=5)

        # 🔹 Durata
        self.duration_entry = tk.Entry(self)
        self.duration_entry.insert(0, "60")
        self.duration_entry.pack(pady=5)

        tk.Button(
            self,
            text="Salvează sesiune",
            command=self.save_session
        ).pack(pady=10)

    def save_session(self):

        game_data = self.games_dict[self.selected_game.get()]
        game_id = game_data[0]
        min_players = game_data[2]
        max_players = game_data[3]

        selected_players = []
        used_names = set()

        for player_var, score_entry in self.player_rows:

            name = player_var.get()

            if name:  # dacă a fost selectat
                if name in used_names:
                    messagebox.showerror("Eroare", "Același jucător selectat de două ori!")
                    return

                used_names.add(name)

                try:
                    score = int(score_entry.get())
                except ValueError:
                    messagebox.showerror("Eroare", f"Scor invalid pentru {name}")
                    return

                # găsim player_id după nume
                player_obj = next(p for p in self.players if p[1] == name)
                selected_players.append((player_obj, score))

        if not (min_players <= len(selected_players) <= max_players):
            messagebox.showerror(
                "Eroare",
                f"Număr invalid de jucători! ({min_players}-{max_players})"
            )
            return

        try:
            duration = int(self.duration_entry.get())
        except ValueError:
            messagebox.showerror("Eroare", "Durata trebuie să fie număr.")
            return

        # 🔹 Inserăm sesiunea
        session_id = GameSessionRepository.add(
            game_id,
            self.date_entry.get(),
            duration
        )

        # 🔹 Clasament descrescător
        sorted_scores = sorted(
            selected_players,
            key=lambda x: x[1],
            reverse=True
        )

        for index, (player, score) in enumerate(sorted_scores):
            standing = index + 1
            PlayerSessionRepository.add(
                session_id,
                player[0],
                score,
                standing
            )

        messagebox.showinfo("Succes", "Sesiune salvată!")
        self.controller.show_home()
