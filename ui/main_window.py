import tkinter as tk
from ui.home_page import HomePage
from ui.add_game_page import AddGamePage
from ui.add_player_page import AddPlayerPage
from ui.add_session_page import AddSessionPage
from ui.statistics_page import StatisticsPage


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Board Game Tracker")
        self.root.geometry("500x400")

        self.current_frame = None

        self.show_home()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_home(self):
        self.clear_frame()
        self.current_frame = HomePage(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_add_game(self):
        self.clear_frame()
        self.current_frame = AddGamePage(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_add_player(self):
        self.clear_frame()
        self.current_frame = AddPlayerPage(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_add_session(self):
        self.clear_frame()
        self.current_frame = AddSessionPage(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_statistics(self):
        self.clear_frame()
        self.current_page = StatisticsPage(self)
        self.current_page.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()