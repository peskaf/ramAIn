from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QCheckBox
from PySide6.QtGui import QIcon

from widgets.data import Data

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

    def params_to_text(self) -> str:
        return f"ignore water: {self.ignore_water_band.isChecked()}"

    def reset(self) -> None:
        self.ignore_water_band.setChecked(True)

    def function_name(self) -> str:
        return Data.auto_math_morpho.__name__

    def get_string_name(self) -> str:
        return "Background Removal - Mathematical Morphology"