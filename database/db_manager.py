import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_path="database.sqlite"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Kapcsolódik az adatbázishoz, vagy létrehozza azt, ha nem létezik."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Létrehozza a szükséges táblákat, ha még nem léteznek."""
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS teszor_category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teszor TEXT UNIQUE,
                    category TEXT
                )
            """
        )

        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS phone_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sim_number TEXT UNIQUE,
                    owner TEXT
                )
            """
        )
        self.conn.commit()

    def get_all_phone_users(self):
        """Visszaadja a phone_user tábla összes rekordját (sim_number, owner)."""
        self.cursor.execute("SELECT sim_number, owner FROM phone_user")
        return self.cursor.fetchall()

    def get_all_teszor_categories(self):
        """Visszaadja a teszor_category tábla összes rekordját (teszor, category)."""
        self.cursor.execute("SELECT teszor, category FROM teszor_category")
        return self.cursor.fetchall()

    def close(self):
        """Bezárja az adatbázis kapcsolatot."""
        if self.conn:
            self.conn.close()
