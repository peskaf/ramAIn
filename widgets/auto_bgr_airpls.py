from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QRegularExpressionValidator, QIcon
from PySide6.QtCore import Signal

import pyqtgraph as pg
import numpy as np

class AutoBGRairPLS(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/background.svg")

        # put widgets into layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Background Removal - airPLS"), 0, 0)
        layout.addWidget(QLabel("No parameters to be set."), 1, 0)
        self.setLayout(layout)

    def get_params(self) -> tuple:
        return ()

    def reset(self) -> None:
        return

    def params_to_text(self) -> str:
        return f""

    def get_string_name(self) -> str:
        return "Background Removal - airPLS"
