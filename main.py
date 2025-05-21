from PySide6.QtWidgets import QApplication
import sys
from ui.main_window import MainWindow
from PySide6.QtGui import QIcon


def main():
    app = QApplication(sys.argv)

    # Főablak létrehozása
    app.setWindowIcon(QIcon("icons/python.png"))
    window = MainWindow(app)

    window.setWindowIcon(QIcon("icons/python.png"))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
