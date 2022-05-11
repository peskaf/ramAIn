from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QCheckBox, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from data import Data
from utils import validators


class AutoBGRIModPoly(QFrame):
    """
    A widget for parameters selection for automatic I-ModPoly bg subtraction method.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto I-ModPoly bg subtraction parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/background.svg")

        self.init_poly_deg = 5

        # range is inclusive on both sides
        self.poly_deg_range = (1, 15)
        self.poly_deg = QLineEdit(str(self.init_poly_deg), validator=validators.INT_VALIDATOR)
    
        self.poly_deg.editingFinished.connect(self.validate_poly_deg_range)

        self.ignore_water_band = QCheckBox()
        self.ignore_water_band.setChecked(True)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Background Removal - I-ModPoly"))

        layout.addWidget(QLabel("Ignore Water Band"), 1, 0)
        layout.addWidget(self.ignore_water_band, 1, 1)

        layout.addWidget(QLabel("Polynom degree"), 2, 0)
        layout.addWidget(self.poly_deg, 2, 1)

        layout.setColumnStretch(layout.columnCount(), 1)
        layout.setAlignment(Qt.AlignVCenter)

        # TODO: lower envelope, spectrum opening ?
        
        self.setLayout(layout)


    def validate_poly_deg_range(self) -> None:
        """
        A function to validate `self.poly_deg` input, setting it to correct value if it's unsatisfactory.
        """

        poly_deg = int(self.poly_deg.text())
        if poly_deg < self.poly_deg_range[0]:
            self.poly_deg.setText(str(self.poly_deg_range[0]))
        elif poly_deg > self.poly_deg_range[1]:
            self.poly_deg.setText(str(self.poly_deg_range[1]))

    def get_params(self) -> tuple[int, bool]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (int(self.poly_deg.text()), self.ignore_water_band.isChecked(), )
        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"poly deg: {int(self.poly_deg.text())}, ignore water: {self.ignore_water_band.isChecked()}"
        return str_parameters

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_imodpoly.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Background Removal - I-ModPoly"
