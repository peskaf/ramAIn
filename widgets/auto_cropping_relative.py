from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QRegularExpressionValidator, QIcon

from widgets.data import Data

class AutoCroppingRelative(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/cut.svg")

        # inputs
        self.init_inputs_value = 0

        positive_int_validator = QRegularExpressionValidator("[0-9]+")
        self.from_start = QLineEdit(str(self.init_inputs_value), validator=positive_int_validator)
        self.from_end = QLineEdit(str(self.init_inputs_value), validator=positive_int_validator)

        # put widgets into layout
        layout = QGridLayout()
        # Spectral plot cropping parameters
        layout.addWidget(QLabel("Spectral Plot Cropping - Relative"), 0, 0)

        layout.addWidget(QLabel("Data Points to Crop from the Beggining"), 1, 0)
        layout.addWidget(QLabel("Data Points to Crop from the End"), 2, 0)

        layout.addWidget(self.from_start, 1, 1)
        layout.addWidget(self.from_end, 2, 1)

        self.setLayout(layout)

    def get_params(self) -> tuple[int, int]:

        parameters = (int(self.from_start.text()), int(self.from_end.text()), )
        return parameters
    
    def params_to_text(self) -> str:
        return f"crop from start: {int(self.from_start.text())}, crop from end: {int(self.from_end.text())}"

    def reset(self) -> None:
        inputs = [
            self.from_start,
            self.from_end
            ]

        for input in inputs:
            input.setText(str(self.init_inputs_value))

    def function_name(self) -> str:
        return Data.auto_crop_relative.__name__

    def get_string_name(self) -> str:
        return "Cropping - Relative"
