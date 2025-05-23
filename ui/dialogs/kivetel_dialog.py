from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QMessageBox,
)


class KivetelDialog(QDialog):
    def __init__(
        self, parent=None, megnev="", teszor_kod="", afa_kulcs="", jogcim_id=""
    ):
        super().__init__(parent)
        self.setWindowTitle("Kivétel szerkesztése")
        self.setMinimumWidth(360)

        self.megnev_input = QLineEdit(megnev)
        self.teszor_input = QLineEdit(teszor_kod)
        self.afa_input = QLineEdit(afa_kulcs)
        self.jogcim_input = QLineEdit(jogcim_id)

        form = QFormLayout()
        form.addRow("Megnevezés:", self.megnev_input)
        form.addRow("TESZOR kód:", self.teszor_input)
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
                self.megnev_input,
                self.teszor_input,
                self.afa_input,
                self.jogcim_input,
            ]
        ):
            QMessageBox.warning(
                self,
                "Hiba",
                "Minden mező legalább 1 karakter hosszú legyen.",
            )
            return
        super().accept()

    def get_data(self):
        return (
            self.megnev_input.text().strip(),
            self.teszor_input.text().strip(),
            self.afa_input.text().strip(),
            self.jogcim_input.text().strip(),
        )
