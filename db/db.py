import sqlite3

def create_connection():
 connection = sqlite3.connect("db/BDD.db")
 return connection