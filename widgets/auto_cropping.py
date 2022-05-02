from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QRegularExpressionValidator, QIcon
from PySide6.QtCore import Signal

import pyqtgraph as pg
import numpy as np

class AutoCropping(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/cut.svg")

        # inputs
        self.init_inputs_value = 0
        real_validator = QRegularExpressionValidator("-?[0-9]+(\.[0-9]+)?")
        self.input_plot_start = QLineEdit(str(self.init_inputs_value), validator=real_validator)
        self.input_plot_end = QLineEdit(str(self.init_inputs_value), validator=real_validator)

        # put widgets into layout
        layout = QGridLayout()

        # Spectral plot cropping parameters
        layout.addWidget(QLabel("Spectral Plot Cropping"), 0, 0)

        layout.addWidget(QLabel("Start Position"), 1, 0)
        layout.addWidget(QLabel("End Position"), 2, 0)

        layout.addWidget(self.input_plot_start, 1, 1)
        layout.addWidget(self.input_plot_end, 2, 1)

        self.setLayout(layout)

    def get_params(self) -> tuple[float, float]:

        parameters = (float(self.input_plot_start.text()), float(self.input_plot_end.text()), )
        return parameters

    def reset(self) -> None:
        inputs = [
            self.input_plot_start,
            self.input_plot_end
            ]

        for input in inputs:
            input.setText(str(self.init_inputs_value))

    def get_string_name(self) -> str:
        return "Cropping"
