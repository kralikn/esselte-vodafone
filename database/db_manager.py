import sqlite3
import os
from utils.utils import get_base_path


class DatabaseManager:
    def __init__(self):
        base_path = get_base_path()
        self.db_path = os.path.join(base_path, "database.sqlite")
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
                CREATE TABLE IF NOT EXISTS jogcim (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nev TEXT NOT NULL,
                    afa_kulcs TEXT,  -- NOT NULL eltávolítva
                    afa_kod TEXT NOT NULL,
                    fokonyvi_szam TEXT NOT NULL
                )
            """
        )
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS kivetel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    megnevezes TEXT NOT NULL,
                    teszor_kod TEXT NOT NULL,
                    afa_kulcs TEXT NOT NULL,
                    jogcim_id INTEGER NOT NULL,
                    FOREIGN KEY (jogcim_id) REFERENCES jogcim(id),
                    UNIQUE (megnevezes, teszor_kod, afa_kulcs)
                )
            """
        )
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS teszor (
                    id INTEGER PRIMARY KEY,
                    teszor_kod TEXT NOT NULL,
                    megnevezes TEXT NOT NULL,
                    afa_kulcs TEXT NOT NULL,
                    jogcim_id INTEGER NOT NULL,
                    FOREIGN KEY (jogcim_id) REFERENCES jogcim(id),
                    UNIQUE (teszor_kod, afa_kulcs)
                )
            """
        )

        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS phone_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT UNIQUE,
                    owner TEXT
                )
            """
        )
        self.conn.commit()

    def get_all_phone_users(self):
        """Visszaadja a phone_user tábla összes rekordját (sim_number, owner)."""
        self.cursor.execute("SELECT * FROM phone_user")
        return self.cursor.fetchall()

    def get_all_teszor(self):
        self.cursor.execute("SELECT * FROM teszor ORDER BY teszor_kod")
        return self.cursor.fetchall()

    def get_all_jogcimek(self):
        self.cursor.execute("SELECT * FROM jogcim ORDER BY nev")
        return self.cursor.fetchall()

    def get_all_kivetelek(self):
        self.cursor.execute("SELECT * FROM kivetel ORDER BY megnevezes")
        return self.cursor.fetchall()

    def get_all_teszor_categories(self):
        """Visszaadja a teszor tábla egyedi (teszor_kod, megnevezes) párosait."""
        self.cursor.execute(
            """
            SELECT DISTINCT teszor_kod, megnevezes
            FROM teszor
        """
        )
        return self.cursor.fetchall()

    def get_jogcim_info(self, megnevezes: str, teszor_kod: str, afa_kulcs: str):
        # Először próbáljuk a kivételt: ellenőrizzük, hogy a megadott megnevezés ezzel kezdődik-e
        self.cursor.execute(
            """
            SELECT jc.nev, jc.afa_kod, jc.fokonyvi_szam
            FROM kivetel k
            JOIN jogcim jc ON jc.id = k.jogcim_id
            WHERE ? LIKE k.megnevezes || '%' AND k.teszor_kod = ? AND k.afa_kulcs = ?
        """,
            (megnevezes, teszor_kod, afa_kulcs),
        )
        result = self.cursor.fetchone()
        if result:
            return result

        # Ha nincs kivétel, akkor alapértelmezett TESZOR
        self.cursor.execute(
            """
            SELECT jc.nev, jc.afa_kod, jc.fokonyvi_szam
            FROM teszor t
            JOIN jogcim jc ON jc.id = t.jogcim_id
            WHERE t.teszor_kod = ? AND t.afa_kulcs = ?
        """,
            (teszor_kod, afa_kulcs),
        )
        return self.cursor.fetchone()

    def add_phone_user(self, phone_number: str, owner: str):
        self.cursor.execute(
            "INSERT INTO phone_user (phone_number, owner) VALUES (?, ?)",
            (phone_number, owner),
        )
        self.conn.commit()

    def delete_phone_user(self, phone_id: int):
        self.cursor.execute("DELETE FROM phone_user WHERE id = ?", (phone_id,))
        self.conn.commit()

    def update_phone_user(self, phone_id: int, phone_number: str, owner: str):
        self.cursor.execute(
            """
            UPDATE phone_user
            SET phone_number = ?, owner = ?
            WHERE id = ?
            """,
            (phone_number, owner, phone_id),
        )
        self.conn.commit()

    def clear_phone_users(self):
        self.cursor.execute("DELETE FROM phone_user")
        self.conn.commit()

    def add_teszor(self, kod: str, megnevezes: str, afa_kulcs: str, jogcim_id: int):
        self.cursor.execute(
            """
            INSERT INTO teszor (teszor_kod, megnevezes, afa_kulcs, jogcim_id)
            VALUES (?, ?, ?, ?)
            """,
            (kod, megnevezes, afa_kulcs, jogcim_id),
        )
        self.conn.commit()

    def delete_teszor(self, teszor_id: int):
        self.cursor.execute("DELETE FROM teszor WHERE id = ?", (teszor_id,))
        self.conn.commit()

    def update_teszor(
        self, teszor_id: int, kod: str, megnevezes: str, afa_kulcs: str, jogcim_id: int
    ):
        self.cursor.execute(
            """
            UPDATE teszor
            SET teszor_kod = ?, megnevezes = ?, afa_kulcs = ?, jogcim_id = ?
            WHERE id = ?
            """,
            (kod, megnevezes, afa_kulcs, jogcim_id, teszor_id),
        )
        self.conn.commit()

    def add_jogcim(self, nev: str, afa_kulcs: str, afa_kod: str, fokonyvi: str):
        self.cursor.execute(
            "INSERT INTO jogcim (nev, afa_kulcs, afa_kod, fokonyvi_szam) VALUES (?, ?, ?, ?)",
            (nev, afa_kulcs, afa_kod, fokonyvi),
        )
        self.conn.commit()

    def update_jogcim(
        self, jogcim_id: int, nev: str, afa_kulcs: str, afa_kod: str, fokonyvi: str
    ):
        self.cursor.execute(
            """
            UPDATE jogcim
            SET nev = ?, afa_kulcs = ?, afa_kod = ?, fokonyvi_szam = ?
            WHERE id = ?
            """,
            (nev, afa_kulcs, afa_kod, fokonyvi, jogcim_id),
        )
        self.conn.commit()

    def delete_jogcim(self, jogcim_id: int):
        self.cursor.execute("DELETE FROM jogcim WHERE id = ?", (jogcim_id,))
        self.conn.commit()

    def add_kivetel(self, megnev, teszor_kod, afa_kulcs, jogcim_id):
        self.cursor.execute(
            "INSERT INTO kivetel (megnevezes, teszor_kod, afa_kulcs, jogcim_id) VALUES (?, ?, ?, ?)",
            (megnev, teszor_kod, afa_kulcs, jogcim_id),
        )
        self.conn.commit()

    def update_kivetel(self, kiv_id, megnev, teszor_kod, afa_kulcs, jogcim_id):
        self.cursor.execute(
            """
            UPDATE kivetel
            SET megnevezes = ?, teszor_kod = ?, afa_kulcs = ?, jogcim_id = ?
            WHERE id = ?
            """,
            (megnev, teszor_kod, afa_kulcs, jogcim_id, kiv_id),
        )
        self.conn.commit()

    def delete_kivetel(self, kiv_id):
        self.cursor.execute("DELETE FROM kivetel WHERE id = ?", (kiv_id,))
        self.conn.commit()

    def close(self):
        """Bezárja az adatbázis kapcsolatot."""
        if self.conn:
            self.conn.close()
