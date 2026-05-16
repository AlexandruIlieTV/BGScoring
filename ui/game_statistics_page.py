import tkinter as tk
from tkinter import ttk
from analytics.statistics import StatisticsService


class GameStatisticsPage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(
            self,
            text="Statistici joc",
            font=("Arial", 18)
        ).pack(pady=20)

        tk.Label(
            self,
            text="Selectează jocul:",
            font=("Arial", 11)
        ).pack(pady=(5, 2))

        self.game_titles = StatisticsService.get_all_game_titles()

        self.game_combo = ttk.Combobox(
            self,
            values=self.game_titles,
            state="readonly",
            width=30
        )
        self.game_combo.pack(pady=5)

        if self.game_titles:
            self.game_combo.current(0)

        tk.Button(
            self,
            text="Arată statistici",
            width=22,
            command=self.show_statistics
        ).pack(pady=10)

        self.results_frame = tk.Frame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Button(
            self,
            text="Go back",
            width=20,
            command=self.controller.show_statistics
        ).pack(pady=10)

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

    def show_statistics(self):
        self._clear_results()

        selected_game = self.game_combo.get()
        if not selected_game:
            self._add_result_line("Te rog selectează un joc.")
            return

        total_sessions = StatisticsService.get_game_total_sessions(selected_game)
        most_frequent_player = StatisticsService.get_game_most_frequent_player(selected_game)
        best_player = StatisticsService.get_game_best_player(selected_game, min_plays=3)
        score_record = StatisticsService.get_game_score_record(selected_game)
        average_score = StatisticsService.get_game_average_score(selected_game)

        self._add_result_line(f"Joc selectat: {selected_game}", bold=True)
        self._add_result_line(f"Număr sesiuni: {total_sessions}")

        if most_frequent_player:
            self._add_result_line(
                f"Jucătorul cel mai activ: {most_frequent_player['player']} "
                f"({most_frequent_player['times_played']} participări)"
            )
        else:
            self._add_result_line("Jucătorul cel mai activ: N/A")

        if best_player:
            self._add_result_line(
                f"Cel mai de succes jucător: {best_player['player']} "
                f"({best_player['win_rate']:.2f}% victorii, "
                f"{best_player['wins']} victorii din {best_player['games_played']} participări)"
            )
        else:
            self._add_result_line(
                "Cel mai de succes jucător: N/A "
                "(sunt necesare minimum 3 participări)"
            )

        if score_record:
            self._add_result_line(
                f"Record de scor: {score_record['score']} "
                f"({score_record['player']})"
            )
        else:
            self._add_result_line("Record de scor: N/A")

        if average_score is None:
            self._add_result_line("Scor mediu: N/A")
        else:
            self._add_result_line(f"Scor mediu: {average_score:.2f}")