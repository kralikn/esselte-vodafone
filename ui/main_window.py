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
from PySide6.QtGui import QAction, QFont
from database.db_manager import DatabaseManager
from PySide6.QtCore import Qt
from pdf_handler.pdf_processor import PdfProcessor
from .dialogs.phone_user_dialog import PhoneUserDialog
from .dialogs.teszor_dialog import TeszorDialog
from .dialogs.jogcim_dialog import JogcimDialog
from .dialogs.kivetel_dialog import KivetelDialog


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.db = DatabaseManager()

        self.setWindowTitle("Vodafone számlafeldolgozás")
        self.setMinimumSize(900, 550)
        # self.setFixedSize(900, 550)

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
        label_import = QLabel("Törzsadatok:")
        label_import.setObjectName("sectionLabel")

        import_layout.addWidget(label_import)
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
        label_master_data = QLabel("Törzsadatok:")
        label_master_data.setObjectName("sectionLabel")
        admin_layout.addWidget(label_master_data)
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
        self.phone_table_widget = self.wrap_table_with_controls(
            self.phone_table,
            self.add_phone_user,
            self.edit_phone_user,
            self.delete_phone_user,
        )

        self.teszor_table = self.build_teszor_table()
        self.teszor_table_widget = self.wrap_table_with_controls(
            self.teszor_table,
            self.add_teszor,
            self.edit_teszor,
            self.delete_teszor,
        )

        self.jogcim_table = self.build_jogcim_table()
        self.jogcim_table_widget = self.wrap_table_with_controls(
            self.jogcim_table,
            self.add_jogcim,
            self.edit_jogcim,
            self.delete_jogcim,
        )

        self.kivetel_table = self.build_kivetel_table()
        self.kivetel_table_widget = self.wrap_table_with_controls(
            self.kivetel_table,
            self.add_kivetel,
            self.edit_kivetel,
            self.delete_kivetel,
        )

        # Hozzáadás stack-hez
        self.stacked_widget.addWidget(self.phone_table_widget)  # index 0
        self.stacked_widget.addWidget(self.teszor_table_widget)  # index 1
        self.stacked_widget.addWidget(self.jogcim_table_widget)  # index 2
        self.stacked_widget.addWidget(self.kivetel_table_widget)  # index 3

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

        self.setFont(QFont("Segoe UI", 9))
        self.setStyleSheet(
            """
                QLabel#sectionLabel {
                    font-size: 10pt;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 4px;
                }
                QPushButton {
                    padding: 6px 12px;
                }
                QStatusBar QLabel {
                    font-size: 8pt;
                    padding: 8px 12px;
                }
            """
        )

    def wrap_table_with_controls(self, table: QTableWidget, on_add, on_edit, on_delete):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.addWidget(table)

        button_layout = QHBoxLayout()
        btn_add = QPushButton("Hozzáadás")
        btn_edit = QPushButton("Szerkesztés")
        btn_delete = QPushButton("Törlés")

        btn_add.clicked.connect(on_add)
        btn_edit.clicked.connect(on_edit)
        btn_delete.clicked.connect(on_delete)

        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)
        layout.addLayout(button_layout)

        return wrapper

    def add_phone_user(self):
        dialog = PhoneUserDialog(self)
        if dialog.exec():
            phone, owner = dialog.get_data()
            self.db.add_phone_user(phone, owner)
            self._refresh_table(self.phone_table, self.db.get_all_phone_users)

    def edit_phone_user(self):
        selected = self.phone_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return

        row = selected[0].row()
        phone_id = int(self.phone_table.item(row, 0).text())
        phone = self.phone_table.item(row, 1).text()
        owner = self.phone_table.item(row, 2).text()

        dialog = PhoneUserDialog(self, phone, owner)
        if dialog.exec():
            new_phone, new_owner = dialog.get_data()
            self.db.update_phone_user(phone_id, new_phone, new_owner)
            self._refresh_table(self.phone_table, self.db.get_all_phone_users)

    def delete_phone_user(self):
        selected = self.phone_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return
        row = selected[0].row()
        phone_id = int(
            self.phone_table.item(row, 0).text()
        )  # ID az első, rejtett oszlop
        phone = self.phone_table.item(row, 1).text()  # Telefonszám a második oszlop

        reply = QMessageBox.question(
            self,
            "Törlés megerősítése",
            f"Biztosan törölni szeretnéd ezt a számot: {phone}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db.delete_phone_user(phone_id)
            self._refresh_table(self.phone_table, self.db.get_all_phone_users)

    def build_phone_table(self):
        table = QTableWidget()
        rows = self.db.get_all_phone_users()  # [(phone_number, owner)]

        table.setRowCount(len(rows))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ID", "Telefonszám", "Dolgozó"])

        for i, (id_, phone, owner) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(str(id_)))
            table.setItem(i, 1, QTableWidgetItem(phone))
            table.setItem(i, 2, QTableWidgetItem(owner))

        table.setColumnHidden(0, True)  # <<< Ezzel lesz rejtve az ID oszlop
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)

        return table

    def add_teszor(self):
        dialog = TeszorDialog(self)
        if dialog.exec():
            kod, megnev, afa, jogcim = dialog.get_data()
            self.db.add_teszor(kod, megnev, afa, jogcim)
            self._refresh_table(self.teszor_table, self.db.get_all_teszor)

    def edit_teszor(self):
        selected = self.teszor_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return
        row = selected[0].row()
        teszor_id = int(self.teszor_table.item(row, 0).text())
        kod = self.teszor_table.item(row, 1).text()
        megnev = self.teszor_table.item(row, 2).text()
        afa = self.teszor_table.item(row, 3).text()
        jogcim = self.teszor_table.item(row, 4).text()

        dialog = TeszorDialog(self, kod, megnev, afa, jogcim)
        if dialog.exec():
            new_kod, new_megnev, new_afa, new_jogcim = dialog.get_data()
            self.db.update_teszor(teszor_id, new_kod, new_megnev, new_afa, new_jogcim)
            self._refresh_table(self.teszor_table, self.db.get_all_teszor)

    def delete_teszor(self):
        selected = self.teszor_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return
        row = selected[0].row()
        teszor_id = int(self.teszor_table.item(row, 0).text())
        kod = self.teszor_table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Törlés megerősítése",
            f"Biztosan törölni szeretnéd ezt a TESZOR kódot: {kod}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.db.delete_teszor(teszor_id)
            self._refresh_table(self.teszor_table, self.db.get_all_teszor)

    def build_teszor_table(self):
        table = QTableWidget()
        rows = (
            self.db.get_all_teszor()
        )  # [(teszor_kod, megnevezes, afa_kulcs, jogcim_id)]
        table.setRowCount(len(rows))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["ID", "TESZOR kód", "Megnevezés", "ÁFA kulcs", "Jogcím ID"]
        )
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))

        table.setColumnHidden(0, True)
        # table.setColumnHidden(4, True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)

        return table

    def add_jogcim(self):
        dialog = JogcimDialog(self)
        if dialog.exec():
            nev, afa_kulcs, afa_kod, fokonyvi = dialog.get_data()
            self.db.add_jogcim(nev, afa_kulcs, afa_kod, fokonyvi)
            self._refresh_table(self.jogcim_table, self.db.get_all_jogcimek)

    def edit_jogcim(self):
        selected = self.jogcim_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return

        row = selected[0].row()
        jogcim_id = int(self.jogcim_table.item(row, 0).text())
        nev = self.jogcim_table.item(row, 1).text()
        afa_kulcs = self.jogcim_table.item(row, 2).text()
        afa_kod = self.jogcim_table.item(row, 3).text()
        fokonyvi = self.jogcim_table.item(row, 4).text()

        dialog = JogcimDialog(self, nev, afa_kulcs, afa_kod, fokonyvi)
        if dialog.exec():
            new_nev, new_afa_kulcs, new_afa_kod, new_fokonyvi = dialog.get_data()
            self.db.update_jogcim(
                jogcim_id, new_nev, new_afa_kulcs, new_afa_kod, new_fokonyvi
            )
            self._refresh_table(self.jogcim_table, self.db.get_all_jogcimek)

    def delete_jogcim(self):
        selected = self.jogcim_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return

        row = selected[0].row()
        jogcim_id = int(self.jogcim_table.item(row, 0).text())
        nev = self.jogcim_table.item(row, 1).text()
        afa_kod = self.jogcim_table.item(row, 3).text()
        fokonyvi = self.jogcim_table.item(row, 4).text()

        message = (
            f"Biztosan törölni szeretnéd ezt a jogcímet?\n\n"
            f"Név: {nev}\n"
            f"ÁFA kód: {afa_kod}\n"
            f"Főkönyvi szám: {fokonyvi}"
        )

        reply = QMessageBox.question(
            self,
            "Törlés megerősítése",
            message,
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.db.delete_jogcim(jogcim_id)
            self._refresh_table(self.jogcim_table, self.db.get_all_jogcimek)

    def build_jogcim_table(self):
        table = QTableWidget()
        rows = self.db.get_all_jogcimek()  # [(nev, afa_kulcs, afa_kod, fokonyvi_szam)]
        table.setRowCount(len(rows))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["ID", "Jogcím", "ÁFA kulcs", "ÁFA kód", "Főkönyvi szám"]
        )
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)

        return table

    def add_kivetel(self):
        dialog = KivetelDialog(self)
        if dialog.exec():
            megnev, teszor, afa, jogcim = dialog.get_data()
            self.db.add_kivetel(megnev, teszor, afa, jogcim)
            self._refresh_table(self.kivetel_table, self.db.get_all_kivetelek)

    def edit_kivetel(self):
        selected = self.kivetel_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return

        row = selected[0].row()
        kiv_id = int(self.kivetel_table.item(row, 0).text())
        megnev = self.kivetel_table.item(row, 1).text()
        teszor = self.kivetel_table.item(row, 2).text()
        afa = self.kivetel_table.item(row, 3).text()
        jogcim = self.kivetel_table.item(row, 4).text()

        dialog = KivetelDialog(self, megnev, teszor, afa, jogcim)
        if dialog.exec():
            new_megnev, new_teszor, new_afa, new_jogcim = dialog.get_data()
            self.db.update_kivetel(kiv_id, new_megnev, new_teszor, new_afa, new_jogcim)
            self._refresh_table(self.kivetel_table, self.db.get_all_kivetelek)

    def delete_kivetel(self):
        selected = self.kivetel_table.selectedItems()
        if not selected:
            self.show_message("Hiba", "Nincs kijelölt sor.", QMessageBox.Warning)
            return

        row = selected[0].row()
        kiv_id = int(self.kivetel_table.item(row, 0).text())
        megnev = self.kivetel_table.item(row, 1).text()
        teszor = self.kivetel_table.item(row, 2).text()
        afa_kulcs = self.kivetel_table.item(row, 4).text()

        message = (
            f"Biztosan törölni szeretnéd ezt a kivételt?\n\n"
            f"Megnevezés: {megnev}\n"
            f"TESZOR szám: {teszor}\n"
            f"ÁFA kulcs: {afa_kulcs}"
        )

        reply = QMessageBox.question(
            self,
            "Törlés megerősítése",
            message,
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.db.delete_kivetel(kiv_id)
            self._refresh_table(self.kivetel_table, self.db.get_all_kivetelek)

    def build_kivetel_table(self):
        table = QTableWidget()
        rows = (
            self.db.get_all_kivetelek()
        )  # [(megnevezes, teszor_kod, afa_kulcs, jogcim_id)]
        table.setRowCount(len(rows))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["ID", "Megnevezés", "TESZOR kód", "ÁFA kulcs", "Jogcím ID"]
        )
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))

        table.setColumnHidden(0, True)
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
