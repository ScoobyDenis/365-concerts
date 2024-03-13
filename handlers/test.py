import sqlite3

DB_NAME = "users.db"
def connect_db(db_name):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    return (connect, cursor)
connect, cursor = connect_db(DB_NAME)
cursor.execute(f"SELECT offer_status FROM users")
offer_status = cursor.fetchone()[0]
print(offer_status)