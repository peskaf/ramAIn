from PySide6.QtWidgets import QFrame, QHBoxLayout
from PySide6.QtCore import Qt

from widgets.title import Title
from widgets.control_buttons import ControlButtons

class Header(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")

        layout = QHBoxLayout()

        layout.addWidget(Title(self))
        layout.addStretch()
        layout.addWidget(ControlButtons(self))

        layout.setAlignment(Qt.AlignLeft)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)