from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QRadioButton, QCheckBox, QPushButton
from PySide6.QtGui import QRegularExpressionValidator, QIcon
from PySide6.QtCore import Signal

class AutoBGRMathMorpho(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/background.svg")

        self.ignore_water_band = QCheckBox()
        self.ignore_water_band.setChecked(True)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Background Removal - Mathematical Morphology"))

        layout.addWidget(QLabel("Ignore Water Band"), 1, 0)
        layout.addWidget(self.ignore_water_band, 1, 1)

        #TODO: add lower envelope, add spectrum opening?
        
        self.setLayout(layout)

    def get_params(self) -> tuple[bool]:

        parameters = (self.ignore_water_band.isChecked(), )
        return parameters

    def reset(self) -> None:
        self.ignore_water_band.setChecked(True)

    def get_string_name(self) -> str:
        return "Background Removal - Mathematical Morphology"