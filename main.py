# loading in modules
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from db.repositories import PlayerRepository, GameRepository, GameSessionRepository, PlayerSessionRepository
from ui.statistics_page import StatisticsPage
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()