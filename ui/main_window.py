from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
)
from PySide6.QtGui import QAction
from database.db_manager import DatabaseManager
from PySide6.QtCore import Qt
from pdf_handler.pdf_processor import PdfProcessor


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.db = DatabaseManager()

        self.setWindowTitle("Vodafone számlafeldolgozás")
        self.setFixedSize(1000, 550)

        """Menük létrehozása."""
        menu_bar = self.menuBar()
        exit_action = QAction("Kilépés", self)
        exit_action.triggered.connect(self.quit_app)
        menu_bar.addAction(exit_action)

        # Központi widget beállítása
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Fő horizontális layout
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        centered_layout = QVBoxLayout()
        centered_layout.setAlignment(Qt.AlignCenter)

        self.import_button = QPushButton("Vodafone számla importálása")
        self.import_button.clicked.connect(self.import_pdf)

        self.status_info_label = QLabel("")
        self.status_info_label.setAlignment(Qt.AlignCenter)

        centered_layout.addWidget(self.import_button)
        centered_layout.addWidget(self.status_info_label)

        # button_layout = QHBoxLayout()
        # button_layout.addStretch()
        # button_layout.addWidget(self.import_button)
        # button_layout.addStretch()

        # label_layout = QHBoxLayout()
        # label_layout.addStretch()
        # label_layout.addWidget(self.status_info_label)
        # label_layout.addStretch()

        left_layout.addStretch()
        left_layout.addLayout(centered_layout)
        left_layout.addStretch()

        center_layout = QVBoxLayout()

        table = QTableWidget()
        rows = self.db.get_all_phone_users()
        table.setRowCount(len(rows))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Telefonszám", "Dolgozó"])

        for row_index, (sim_number, owner) in enumerate(rows):
            table.setItem(row_index, 0, QTableWidgetItem(sim_number))
            table.setItem(row_index, 1, QTableWidgetItem(owner))

        # table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        center_layout.addWidget(table)

        right_layout = QVBoxLayout()

        teszor_table = QTableWidget()
        rows = self.db.get_all_teszor_categories()

        teszor_table.setRowCount(len(rows))
        teszor_table.setColumnCount(2)
        teszor_table.setHorizontalHeaderLabels(["TESZOR", "Kategória"])

        for row_index, (teszor, category) in enumerate(rows):
            teszor_table.setItem(row_index, 0, QTableWidgetItem(teszor))
            teszor_table.setItem(row_index, 1, QTableWidgetItem(category))

        # table.horizontalHeader().setStretchLastSection(True)
        teszor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        right_layout.addWidget(teszor_table)

        # Oszlopokat hozzáadjuk a fő layouthoz
        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(center_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=2)

        # Layout beállítása a központi widgetre
        central_widget.setLayout(main_layout)

        # Státuszsor
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Esselte v0.1")
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)

    def import_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDF fájl kiválasztása", "", "PDF fájlok (*.pdf)"
        )

        if file_path:
            file_name = file_path.split("/")[-1]
            self.status_info_label.setText(f"Kiválasztott fájl: {file_name}")

            processor = PdfProcessor(file_path, self.db)
            success, message = processor.process("Vodafone_szamla.xlsx")

            self.status_info_label.setText(message)
        else:
            self.status_info_label.setText("Nincs fájl kiválasztva.")

    def quit_app(self):
        """Kilépés az alkalmazásból."""
        self.db.close()
        self.app.quit()
