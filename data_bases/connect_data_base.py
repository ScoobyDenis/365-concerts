import sqlite3

DB_NAME = "users.db"
ADMINS = [1372933011,1088508317, 364640169]

def connect_db(db_name):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    return (connect, cursor)