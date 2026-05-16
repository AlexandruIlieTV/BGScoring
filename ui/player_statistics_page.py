import tkinter as tk
from tkinter import ttk
from analytics.statistics import StatisticsService


class PlayerStatisticsPage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(
            self,
            text="Statistici jucător",
            font=("Arial", 18)
        ).pack(pady=20)

        tk.Label(
            self,
            text="Selectează jucătorul:",
            font=("Arial", 11)
        ).pack(pady=(5, 2))

        self.player_names = StatisticsService.get_all_player_names()

        self.player_combo = ttk.Combobox(
            self,
            values=self.player_names,
            state="readonly",
            width=30
        )
        self.player_combo.pack(pady=5)

        if self.player_names:
            self.player_combo.current(0)

        tk.Button(
            self,
            text="Arată statistici",
            width=22,
            command=self.show_statistics
        ).pack(pady=10)

        tk.Label(
            self,
            text="Scor mediu pentru un joc jucat:",
            font=("Arial", 11)
        ).pack(pady=(15, 2))

        self.game_combo = ttk.Combobox(
            self,
            values=[],
            state="readonly",
            width=30
        )
        self.game_combo.pack(pady=5)

        tk.Button(
            self,
            text="Arată scor mediu",
            width=22,
            command=self.show_average_score_for_selected_game
        ).pack(pady=8)

        self.results_frame = tk.Frame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=15)

        tk.Button(
            self,
            text="Go back",
            width=20,
            command=self.controller.show_statistics
        ).pack(pady=10)

        self.player_combo.bind("<<ComboboxSelected>>", self._update_game_combobox)

        if self.player_names:
            self._update_game_combobox()

    def _clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def _add_result_line(self, text, bold=False):
        font = ("Arial", 11, "bold") if bold else ("Arial", 11)
        tk.Label(
            self.results_frame,
            text=text,
            font=font,
            anchor="w",
            justify="left"
        ).pack(fill="x", pady=2)

    def _update_game_combobox(self, event=None):
        selected_player = self.player_combo.get()

        if not selected_player:
            self.game_combo["values"] = []
            self.game_combo.set("")
            return

        games = StatisticsService.get_games_played_by_player(selected_player)
        self.game_combo["values"] = games

        if games:
            self.game_combo.current(0)
        else:
            self.game_combo.set("")

    def show_statistics(self):
        self._clear_results()

        selected_player = self.player_combo.get()
        if not selected_player:
            self._add_result_line("Te rog selectează un jucător.")
            return

        total_games = StatisticsService.get_player_total_games_played(selected_player)
        favourite_game = StatisticsService.get_player_favourite_game(selected_player)
        best_game = StatisticsService.get_player_best_game(selected_player, min_plays=3)
        score_records = StatisticsService.get_player_score_records(selected_player)

        self._add_result_line(f"Jucător selectat: {selected_player}", bold=True)
        self._add_result_line(f"Total participări: {total_games}")

        if favourite_game:
            self._add_result_line(
                f"Joc favorit: {favourite_game['game']} "
                f"({favourite_game['times_played']} participări)"
            )
        else:
            self._add_result_line("Joc favorit: N/A")

        if best_game:
            self._add_result_line(
                f"Cel mai bun joc: {best_game['game']} "
                f"({best_game['win_rate']:.2f}% victorii, "
                f"{best_game['wins']} victorii din {best_game['games_played']} jocuri)"
            )
        else:
            self._add_result_line(
                "Cel mai bun joc: N/A "
                "(sunt necesare minimum 3 participări la același joc)"
            )

        if score_records:
            self._add_result_line(
                f"Recorduri de scor deținute: {len(score_records)}",
                bold=True
            )
            for record in score_records:
                self._add_result_line(
                    f"• {record['game']}: {record['score']}"
                )
        else:
            self._add_result_line("Recorduri de scor deținute: 0")

    def show_average_score_for_selected_game(self):
        self._clear_results()

        selected_player = self.player_combo.get()
        selected_game = self.game_combo.get()

        if not selected_player:
            self._add_result_line("Te rog selectează un jucător.")
            return

        if not selected_game:
            self._add_result_line("Te rog selectează un joc.")
            return

        avg_score = StatisticsService.get_player_average_score_for_game(
            selected_player,
            selected_game
        )

        self._add_result_line(f"Jucător: {selected_player}", bold=True)
        self._add_result_line(f"Joc: {selected_game}")

        if avg_score is None:
            self._add_result_line("Scor mediu: N/A")
        else:
            self._add_result_line(f"Scor mediu: {avg_score:.2f}")