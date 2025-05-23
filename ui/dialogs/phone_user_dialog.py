from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QDialogButtonBox,
    QMessageBox,
)


class PhoneUserDialog(QDialog):
    def __init__(self, parent=None, phone="", owner=""):
        super().__init__(parent)
        self.setWindowTitle("Telefonszám szerkesztése")
        self.setMinimumWidth(360)

        self.phone_input = QLineEdit(phone)
        self.owner_input = QLineEdit(owner)

        form = QFormLayout()
        form.addRow("Telefonszám:", self.phone_input)
        form.addRow("Dolgozó neve:", self.owner_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def accept(self):
        phone = self.phone_input.text().strip()
        owner = self.owner_input.text().strip()

        if len(phone) < 3 or len(owner) < 3:
            QMessageBox.warning(
                self,
                "Hibás adat",
                "A telefonszám és a dolgozó neve is legalább 3 karakter hosszú legyen.",
            )
            return  # Nem zárja be a dialógust

        super().accept()  # Csak akkor hívódik meg, ha valid az adat

    def get_data(self):
        return self.phone_input.text(), self.owner_input.text()
