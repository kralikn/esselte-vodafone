from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QMessageBox,
)


class TeszorDialog(QDialog):
    def __init__(self, parent=None, kod="", megnevezes="", afa_kulcs="", jogcim_id=""):
        super().__init__(parent)
        self.setWindowTitle("TESZOR szerkesztése")
        self.setMinimumWidth(360)

        self.kod_input = QLineEdit(kod)
        self.megnevezes_input = QLineEdit(megnevezes)
        self.afa_input = QLineEdit(afa_kulcs)
        self.jogcim_input = QLineEdit(jogcim_id)

        form = QFormLayout()
        form.addRow("TESZOR kód:", self.kod_input)
        form.addRow("Megnevezés:", self.megnevezes_input)
        form.addRow("ÁFA kulcs:", self.afa_input)
        form.addRow("Jogcím ID:", self.jogcim_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def accept(self):
        if any(
            len(field.text().strip()) < 1
            for field in [
                self.kod_input,
                self.megnevezes_input,
                self.afa_input,
                self.jogcim_input,
            ]
        ):
            QMessageBox.warning(
                self, "Hiba", "Minden mező legalább 1 karakter hosszú legyen."
            )
            return
        super().accept()

    def get_data(self):
        return (
            self.kod_input.text().strip(),
            self.megnevezes_input.text().strip(),
            self.afa_input.text().strip(),
            self.jogcim_input.text().strip(),
        )
