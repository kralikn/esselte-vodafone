from PySide6.QtWidgets import QApplication
import sys
import os
from ui.main_window import MainWindow
from PySide6.QtGui import QIcon
from utils.utils import get_base_path


def main():
    app = QApplication(sys.argv)

    # Főablak létrehozása
    base_path = get_base_path()
    icon_path = os.path.join(base_path, "icons", "python.png")
    app.setWindowIcon(QIcon(icon_path))

    window = MainWindow(app)

    window.setWindowIcon(QIcon(icon_path))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
