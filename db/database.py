import sqlite3

DB_NAME = "d:/eLearn/Projects/bgScores/bgScore.db"

def get_connection():
    return sqlite3.connect(DB_NAME)