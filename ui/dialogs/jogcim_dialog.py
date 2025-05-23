from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QMessageBox,
)


class JogcimDialog(QDialog):
    def __init__(self, parent=None, nev="", afa_kulcs="", afa_kod="", fokonyvi=""):
        super().__init__(parent)
        self.setWindowTitle("Jogcím szerkesztése")
        self.setMinimumWidth(360)

        self.nev_input = QLineEdit(nev)
        self.afa_kulcs_input = QLineEdit(afa_kulcs)
        self.afa_kod_input = QLineEdit(afa_kod)
        self.fokonyvi_input = QLineEdit(fokonyvi)

        form = QFormLayout()
        form.addRow("Jogcím neve:", self.nev_input)
        form.addRow("ÁFA kulcs:", self.afa_kulcs_input)
        form.addRow("ÁFA kód:", self.afa_kod_input)
        form.addRow("Főkönyvi szám:", self.fokonyvi_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def accept(self):
        if (
            len(self.nev_input.text().strip()) < 3
            or len(self.afa_kod_input.text().strip()) < 3
            or len(self.fokonyvi_input.text().strip()) < 3
        ):
            QMessageBox.warning(
                self,
                "Hiba",
                "A jogcím neve, ÁFA kód és főkönyvi szám legalább 3 karakter hosszú legyen.",
            )
            return
        super().accept()

    def get_data(self):
        return (
            self.nev_input.text().strip(),
            self.afa_kulcs_input.text().strip(),
            self.afa_kod_input.text().strip(),
            self.fokonyvi_input.text().strip(),
        )
