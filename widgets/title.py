from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

# HEADER
class Title(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("title")

        layout = QHBoxLayout()

        icon = QLabel()
        icon.setPixmap(QPixmap("icons/icon.svg"))
        layout.addWidget(icon)

        layout.addWidget(QLabel("RamAIn"))
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)