# utils.py
import os
import sys


def get_base_path():
    """Visszaadja az aktuális mappa elérési útját PyInstaller kompatibilisen."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # .exe csomagolt környezet
    return os.path.abspath(".")
