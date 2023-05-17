import sqlite3
from config import settings


class Database:
    def __init__(self):
        self.connection = sqlite3.connect(settings["dbname"])
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            id INT,
            cash BIGINT,
            rep INT,
            lvl INT,
            xp INT,
            _update INT
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
            id_channel INT,
            id_role INT,
            cost BIGINT
        )""")
        self.connection.commit()

    def quarry(self, quarry, commit: bool = False):
        self.cursor.execute(quarry)
        if commit:
            self.connection.commit()

    def register_user(self, user):
        self.cursor.execute(f"INSERT INTO users VALUES ('{user.name}', {user.id}, 150, 1, 1, {settings['base_xp']}, 1)")
        self.connection.commit()

    def delete_user(self, user):
        self.cursor.execute(f"DELETE FROM users WHERE id = {user.id}")
        self.connection.commit()

    def check_user(self, user_id):
        return self.cursor.execute(f"SELECT id FROM users WHERE id = {user_id}").fetchone()

    def get_user_all(self, user):
        return self.cursor.execute(f"SELECT * FROM users WHERE id = {user.id}").fetchone()

    def get_users_all(self):
        return self.cursor.execute(f"SELECT * FROM users").fetchall()

    def get_update(self, user):
        """Need user id to get update int"""
        return self.cursor.execute(f"SELECT _update FROM users WHERE id = {user.id}").fetchone()[0]

    def get_money(self, user):
        return self.cursor.execute(f"SELECT cash FROM users WHERE id = {user.id}").fetchone()[0]

    def give_reputation(self, user, amount: int = 1):
        self.cursor.execute(f"UPDATE users SET rep = rep + {amount} WHERE id = {user.id}")
        self.connection.commit()

    def give_cash(self, user=None, amount: int = None):
        self.cursor.execute(f"UPDATE users SET cash = cash + {amount} WHERE id = {user.id}")
        self.connection.commit()

    def give_exp(self, user=None, amount: int = None):
        self.cursor.execute(f"UPDATE users SET xp = xp + {amount} WHERE id = {user.id}")
        self.connection.commit()

    def remove_cash(self, user, amount: int = 0):
        self.cursor.execute(f"UPDATE users SET cash = cash - {amount} WHERE id = {user.id}")
        self.connection.commit()

    def set_cash(self, user, amount: int = 0):
        self.cursor.execute(f"UPDATE users SET cash = {amount} WHERE id = {user.id}")
        self.connection.commit()

    def set_reputation(self, user, amount: int = 0):
        self.cursor.execute(f"UPDATE users SET rep = {amount} WHERE id = {user.id}")
        self.connection.commit()

    def set_update(self, user, amount: int = 0):
        self.cursor.execute(f"UPDATE users SET _update = {amount} WHERE id = {user.id}")
        self.connection.commit()

    def set_level(self, user, amount: int = 0):
        self.cursor.execute(f"UPDATE users SET lvl = {amount} WHERE id = {user.id}")
        self.connection.commit()

    def shop_add(self, role: int = None, channel: int = None, amount: int = None):
        if role and channel:
            self.cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(channel, role, amount))
        elif role and not channel:
            self.cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(0, role, amount))
        elif channel and not role:
            self.cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(channel, 0, amount))
        self.connection.commit()

    def shop_remove(self, role: int = None, channel: int = None):
        if role:
            self.cursor.execute("DELETE FROM shop WHERE id_role = {}".format(role))
        elif channel:
            self.cursor.execute("DELETE FROM shop WHERE id_channel = {}".format(channel))
        self.connection.commit()

    def shop_get_all(self):
        return self.cursor.execute("SELECT id_role, id_channel, cost FROM shop")

    def shop_get_price(self, channel_id: int = None, role_id: int = None):
        if role_id and channel_id:
            return self.cursor.execute("SELECT cost FROM shop WHERE id_role = {}".format(role_id)).fetchone()[0]
        elif role_id:
            return self.cursor.execute("SELECT cost FROM shop WHERE id_role = {}".format(role_id)).fetchone()[0]
        elif channel_id:
            return self.cursor.execute("SELECT cost FROM shop WHERE id_channel = {}".format(channel_id)).fetchone()[0]

