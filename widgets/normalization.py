from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QRegularExpressionValidator, QIcon
from PySide6.QtCore import Signal

class Normalization(QFrame):
    apply_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/normalize.svg")
        ...

    def reset(self) -> None:
        ...

    def get_string_name(self):
        return "Normalization"

