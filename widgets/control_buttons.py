from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

# OK
class ControlButtons(QFrame):
    def __init__(self):
        super(ControlButtons, self).__init__()

        # name for styling in qss file
        self.setObjectName("control_buttons")

        buttons = [
            QPushButton(icon=QIcon("icons/collapse.svg")),
            QPushButton(icon=QIcon("icons/maximize.svg")),
            QPushButton(icon=QIcon("icons/exit.svg"))
        ]

        layout = QHBoxLayout()

        for button in buttons:
            layout.addWidget(button)

        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)