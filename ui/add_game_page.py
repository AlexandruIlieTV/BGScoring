import tkinter as tk
import sqlite3
from tkinter import messagebox
from db.repositories import GameRepository


class AddGamePage(tk.Frame):

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        tk.Label(self, text="Adaugă joc", font=("Arial", 16)).pack(pady=15)

        self.create_form()

    def create_form(self):

        self.title_entry = self.create_labeled_entry("Titlu")
        self.min_entry = self.create_labeled_entry("Min jucători")
        self.max_entry = self.create_labeled_entry("Max jucători")
        self.theme_entry = self.create_labeled_entry("Temă")
        self.year_entry = self.create_labeled_entry("An lansare")

        tk.Button(
            self,
            text="Salvează",
            command=self.save_game,
            width=15
        ).pack(pady=10)

        tk.Button(
            self,
            text="Înapoi",
            command=self.controller.show_home,
            width=15
        ).pack(pady=5)

    def create_labeled_entry(self, label_text):
        frame = tk.Frame(self)
        frame.pack(pady=5)

        tk.Label(frame, text=label_text, width=15, anchor="w").pack(side="left")
        entry = tk.Entry(frame, width=20)
        entry.pack(side="left")

        return entry

    def save_game(self):

        title = self.title_entry.get().strip()
        min_p = self.min_entry.get().strip()
        max_p = self.max_entry.get().strip()
        theme = self.theme_entry.get().strip()
        year = self.year_entry.get().strip()

        # 🔎 Validări

        if not title:
            messagebox.showerror("Eroare", "Titlul este obligatoriu.")
            return

        #if GameRepository.exists(title):
            #messagebox.showerror("Eroare", "Acest joc există deja.")
            #return

        try:
            min_p = int(min_p)
            max_p = int(max_p)
            year = int(year)
        except ValueError:
            messagebox.showerror("Eroare", "Min, Max și An trebuie să fie numere.")
            return

        if min_p <= 0:
            messagebox.showerror("Eroare", "Min jucători trebuie să fie > 0.")
            return

        if max_p < min_p:
            messagebox.showerror("Eroare", "Max jucători trebuie să fie ≥ Min jucători.")
            return

        # ✅ Salvare
        try:
            GameRepository.add(title, min_p, max_p, theme, year)
            messagebox.showinfo("Succes", "Joc adăugat cu succes!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Eroare", "Jocul există deja.")
        
        # curăță formularul
        self.clear_form()

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.min_entry.delete(0, tk.END)
        self.max_entry.delete(0, tk.END)
        self.theme_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)