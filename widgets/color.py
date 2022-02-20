from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFrame, QSizePolicy

# PLACEHOLDER
class Color(QFrame):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setObjectName("color")

        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)