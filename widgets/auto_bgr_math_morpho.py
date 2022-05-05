from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QCheckBox, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from data import Data

class AutoBGRMathMorpho(QFrame):
    """
    A widget for parameters selection for automatic math morpho bg subtraction method.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto math morpho bg subtraction parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

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

        layout.setColumnStretch(layout.columnCount(), 1)
        layout.setAlignment(Qt.AlignVCenter)

        # TODO: lower envelope,spectrum opening?

        self.setLayout(layout)

    def get_params(self) -> tuple[bool]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (self.ignore_water_band.isChecked(), )
        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"ignore water: {self.ignore_water_band.isChecked()}"
        return str_parameters

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_math_morpho.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Background Removal - Mathematical Morphology"