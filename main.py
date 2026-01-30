# loading in modules
import sqlite3
import pandas as pd
#import sqlalchemy

# creating file path
dbfile = 'd:/eLearn/Projects/bgScores/bgScore.db'
# Create a SQL connection to our SQLite database
con = sqlite3.connect(dbfile)

# creating cursor
cur = con.cursor()

# reading all table names
table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
# here is you table list
print(table_list)

df = pd.read_sql_query('SELECT * FROM players', con)
print(df)

# Be sure to close the connection
con.close()