import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analytics.statistics import StatisticsService


class StatisticsPage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.canvas = None

        tk.Label(
            self,
            text="Statistici",
            font=("Arial", 18)
        ).pack(pady=20)

        # Summary
        total_sessions = StatisticsService.total_sessions()

        tk.Label(self, text=f"Sesiuni totale: {total_sessions}").pack()

        # Buttons
        tk.Label(self, text="Alege o statistică:", font=("Arial", 12)).pack(pady=10)

        tk.Button(
            self,
            text="Top jocuri",
            width=25,
            command=self.show_top_games
        ).pack(pady=3)

        tk.Button(
            self,
            text="Top jucători activi",
            width=25,
            command=self.show_top_players
        ).pack(pady=3)

        tk.Button(
            self,
            text="Top rata de victorie",
            width=25,
            command=self.show_top_win_rate
        ).pack(pady=3)

        # Chart area
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, pady=10)

        # Back button
        tk.Button(
            self,
            text="Go back",
            width=20,
            command=self.controller.show_home
        ).pack(pady=10)

    # --- Chart handling ---

    def _clear_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.canvas = None

    def _draw_chart(self, series, title, chart_type="bar"):
        self._clear_chart()

        if series.empty:
            tk.Label(self.chart_frame, text="Nu există date.").pack()
            return

        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        if chart_type == "bar":
            ax.bar(series.index.astype(str), series.values)
            ax.tick_params(axis='x', rotation=25)

        elif chart_type == "pie":
            ax.pie(
                series.values,
                labels=series.index.astype(str),
                autopct='%1.1f%%'
            )

        ax.set_title(title)
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # --- Button actions ---

    def show_top_games(self):
        data = StatisticsService.most_played_games()
        self._draw_chart(data, "Top jocuri", chart_type="pie")

    def show_top_players(self):
        data = StatisticsService.most_active_players()
        self._draw_chart(data, "Top jucători activi")

    def show_top_win_rate(self):
        data = StatisticsService.best_players_by_win_rate()
        self._draw_chart(data, "Top rata de victorie")