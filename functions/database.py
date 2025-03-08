import sqlite3

from structures.User import User


class database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.check_tables()

    def check_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            messages INTEGER DEFAULT 0,
            voicetime INTEGER DEFAULT 0,
            jailed INTEGER DEFAULT 0)""")


        self.conn.commit()

    def add_user(self, user: User):
        self.cursor.execute("""
        INSERT OR IGNORE INTO users (userid, username) VALUES (?, ?)""", 
        (user.userid, user.username))

        self.conn.commit()

    def get_user(self, userid) -> User:
        self.cursor.execute("""
        SELECT * FROM users WHERE userid = ?""", (userid,))

        fetched_user = self.cursor.fetchone()

        user = User(userid=userid, username=fetched_user[1], messages=fetched_user[2], voicetime=fetched_user[3], jailed=fetched_user[4])
        return user

    def add_message(self, user_id):
        self.cursor.execute("""
        UPDATE users SET messages = messages + 1 WHERE userid = ?""", (user_id,))

        self.conn.commit()

    def add_voicetime(self, user_id: int, time: int = 1):
        self.cursor.execute("""
        UPDATE users SET voicetime = voicetime + ? WHERE userid = ?""", (time, user_id))

        self.conn.commit()

    def get_message_leaderboard(self) -> list[User]:
        self.cursor.execute("""
        SELECT * FROM users ORDER BY messages DESC LIMIT 10""")

        fetched_users = self.cursor.fetchall()
        users = []
        for user in fetched_users:
            users.append(User(userid=user[0], username=user[1], messages=user[2], voicetime=user[3], jailed=user[4]))

        return users
    
    def get_voicetime_leaderboard(self) -> list[User]:
        self.cursor.execute("""
        SELECT * FROM users ORDER BY voicetime DESC LIMIT 10""")

        fetched_users = self.cursor.fetchall()
        users = []
        for user in fetched_users:
            users.append(User(userid=user[0], username=user[1], messages=user[2], voicetime=user[3], jailed=user[4]))

        return users