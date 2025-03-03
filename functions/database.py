import sqlite3

from structures.User import User


class database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def check_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY,
            usernme TEXT NOT NULL,
            messages INTEGER DEFAULT 0
            voicetime INTEGER DEFAULT 0
            jailed INTEGER DEFAULT 0)""")


        self.conn.commit()

    def add_user(self, user: User):
        self.cursor.execute("""
        INSERT OR IGNORE INTO users (userid, username) VALUES (?, ?)""", 
        (user.userid, user.username))

        self.conn.commit()

    def add_message(self, user_id):
        self.cursor.execute("""
        UPDATE users SET messages = messages + 1 WHERE userid = ?""", (user_id,))

        self.conn.commit()

    def add_voicetime(self, user_id, time):
        self.cursor.execute("""
        UPDATE users SET voicetime = voicetime + ? WHERE userid = ?""", (time, user_id))

        self.conn.commit()


    def close(self):
        self.conn.close()