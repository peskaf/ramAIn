from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QCheckBox
from PySide6.QtGui import QRegularExpressionValidator, QIcon

from data import Data

class AutoBGRPoly(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/background.svg")

        int_validator = QRegularExpressionValidator("-?[0-9]+")

        self.init_poly_deg = 5

        # range is inclusive on both sides
        self.poly_deg_range = (1, 15)
        self.poly_deg = QLineEdit(str(self.init_poly_deg), validator=int_validator)
    
        self.poly_deg.editingFinished.connect(self.validate_poly_deg_range)

        self.ignore_water_band = QCheckBox()
        self.ignore_water_band.setChecked(True)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Background Removal - Polynom Interpolation"))

        layout.addWidget(QLabel("Ignore Water Band"), 1, 0)
        layout.addWidget(self.ignore_water_band, 1, 1)

        layout.addWidget(QLabel("Polynom degree"), 2, 0)
        layout.addWidget(self.poly_deg, 2, 1)

        #TODO: add lower envelope, add spectrum opening?
        
        self.setLayout(layout)


    def validate_poly_deg_range(self) -> None:

        poly_deg = int(self.poly_deg.text())
        if poly_deg < self.poly_deg_range[0]:
            self.poly_deg.setText(str(self.poly_deg_range[0]))
        elif poly_deg > self.poly_deg_range[1]:
            self.poly_deg.setText(str(self.poly_deg_range[1]))

    def get_params(self) -> tuple[int, bool]:
        parameters = (int(self.poly_deg.text()), self.ignore_water_band.isChecked(), )
        return parameters

    def params_to_text(self) -> str:
        return f"poly deg: {int(self.poly_deg.text())}, ignore water: {self.ignore_water_band.isChecked()}"

    def reset(self) -> None:

        self.ignore_water_band.setChecked(True)
        self.poly_deg.setText(str(self.init_poly_deg))

    def function_name(self) -> str:
        return Data.auto_poly.__name__

    def get_string_name(self) -> str:
        return "Background Removal - Polynom Interpolation"