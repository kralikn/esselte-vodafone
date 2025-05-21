# utils.py
import os
import sys


def get_base_path():
    """Visszaadja az aktuális mappa elérési útját PyInstaller kompatibilisen."""
    if getattr(sys, "frozen", False):
        # PyInstaller esetén az exe mappája (external files-hez)
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


def get_resource_path(relative_path):
    """Visszaadja a resource fájlok elérési útját PyInstaller kompatibilisen."""
    if getattr(sys, "frozen", False):
        # PyInstaller esetén a bundled resources
        base_path = sys._MEIPASS
    else:
        # Fejlesztési környezet
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
