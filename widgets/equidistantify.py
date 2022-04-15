from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Signal

class Equidistantify(QFrame):
    apply_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        ...
