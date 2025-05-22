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
    QMessageBox,
    QProgressDialog,
    QStackedWidget,
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
        self.setFixedSize(900, 550)

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

        self.import_button = QPushButton("Vodafone számla")
        self.import_button.clicked.connect(self.import_pdf)

        # Felső rész: Importálás
        import_layout = QVBoxLayout()
        import_layout.setAlignment(Qt.AlignTop)
        import_layout.addWidget(QLabel("PDF importálás:"))
        import_layout.addWidget(self.import_button)

        # Alsó rész: Törzsadat gombok
        self.jogcim_button = QPushButton("Jogcímek")
        self.teszor_button = QPushButton("TESZOR számok")
        self.kivetel_button = QPushButton("Kivételek")
        self.phoneuser_button = QPushButton("Telefonszámok")

        self.phoneuser_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )
        self.teszor_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(1)
        )
        self.jogcim_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(2)
        )
        self.kivetel_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(3)
        )

        admin_layout = QVBoxLayout()
        admin_layout.setAlignment(Qt.AlignTop)
        admin_layout.addWidget(QLabel("Törzsadatok:"))
        admin_layout.addWidget(self.jogcim_button)
        admin_layout.addWidget(self.teszor_button)
        admin_layout.addWidget(self.kivetel_button)
        admin_layout.addWidget(self.phoneuser_button)

        # Két különálló frame, hogy tagolt legyen
        import_frame = QWidget()
        import_frame.setLayout(import_layout)

        admin_frame = QWidget()
        admin_frame.setLayout(admin_layout)

        left_layout.addWidget(import_frame)
        left_layout.addWidget(admin_frame)

        self.stacked_widget = QStackedWidget()

        # Táblák létrehozása külön metódusokkal
        self.phone_table = self.build_phone_table()
        self.teszor_table = self.build_teszor_table()
        self.jogcim_table = self.build_jogcim_table()
        self.kivetel_table = self.build_kivetel_table()

        # Hozzáadás stack-hez
        self.stacked_widget.addWidget(self.phone_table)  # index 0
        self.stacked_widget.addWidget(self.teszor_table)  # index 1
        self.stacked_widget.addWidget(self.jogcim_table)  # index 2
        self.stacked_widget.addWidget(self.kivetel_table)  # index 3

        self.stacked_widget.currentChanged.connect(self.refresh_table_on_switch)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.stacked_widget)

        # Oszlopokat hozzáadjuk a fő layouthoz
        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=6)

        # Layout beállítása a központi widgetre
        central_widget.setLayout(main_layout)

        # Státuszsor
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Esselte v0.1")
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)

    def build_phone_table(self):
        table = QTableWidget()
        rows = self.db.get_all_phone_users()  # [(phone_number, owner)]
        table.setRowCount(len(rows))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Telefonszám", "Dolgozó"])
        for i, (phone, owner) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(phone))
            table.setItem(i, 1, QTableWidgetItem(owner))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)

        return table

    def build_teszor_table(self):
        table = QTableWidget()
        rows = (
            self.db.get_all_teszor()
        )  # [(teszor_kod, megnevezes, afa_kulcs, jogcim_id)]
        table.setRowCount(len(rows))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            ["TESZOR kód", "Megnevezés", "ÁFA kulcs", "Jogcím ID"]
        )
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)

        return table

    def build_jogcim_table(self):
        table = QTableWidget()
        rows = self.db.get_all_jogcimek()  # [(nev, afa_kulcs, afa_kod, fokonyvi_szam)]
        table.setRowCount(len(rows))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            ["Jogcím", "ÁFA kulcs", "ÁFA kód", "Főkönyvi szám"]
        )
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)

        return table

    def build_kivetel_table(self):
        table = QTableWidget()
        rows = (
            self.db.get_all_kivetelek()
        )  # [(megnevezes, teszor_kod, afa_kulcs, jogcim_id)]
        table.setRowCount(len(rows))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            ["Megnevezés", "TESZOR kód", "ÁFA kulcs", "Jogcím ID"]
        )
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)

        return table

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec()

    def update_progress(self, current, total):
        self.progress.setLabelText(
            f"{self.file_name}: {current}/{total}. oldal feldolgozása…"
        )
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.app.processEvents()

    def refresh_table_on_switch(self, index):
        if index == 0:
            self._refresh_table(self.phone_table, self.db.get_all_phone_users)
        elif index == 1:
            self._refresh_table(self.teszor_table, self.db.get_all_teszor)
        elif index == 2:
            self._refresh_table(self.jogcim_table, self.db.get_all_jogcimek)
        elif index == 3:
            self._refresh_table(self.kivetel_table, self.db.get_all_kivetelek)

    def _refresh_table(self, table: QTableWidget, data_func):
        rows = data_func()
        table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(i, j, item)

    def import_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDF fájl kiválasztása", "", "PDF fájlok (*.pdf)"
        )

        if file_path:
            self.file_name = file_path.split("/")[-1]
            # self.status_info_label.setText(f"Kiválasztott fájl: {file_name}")

            # Folyamatjelző dialógus
            self.progress = QProgressDialog(
                "Feldolgozás folyamatban...", None, 0, 0, self
            )
            self.progress.setWindowTitle("Feldolgozás")
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setCancelButton(None)
            self.progress.setMinimumDuration(0)  # Azonnal jelenjen meg
            self.progress.show()

            # Azonnali frissítés (különben nem jelenik meg időben)
            self.app.processEvents()

            processor = PdfProcessor(file_path, self.db)
            success, message = processor.process(
                "Vodafone_szamla.xlsx", progress_callback=self.update_progress
            )

            self.progress.close()

            self.show_message(
                "Feldolgozás eredménye",
                message,
                QMessageBox.Information if success else QMessageBox.Warning,
            )

            # self.status_info_label.setText(message)
        else:
            self.show_message(
                "Nincs fájl kiválasztva",
                "Nem történt fájl kiválasztás.",
                QMessageBox.Warning,
            )
            # self.status_info_label.setText("Nincs fájl kiválasztva.")

    def quit_app(self):
        """Kilépés az alkalmazásból."""
        self.db.close()
        self.app.quit()
