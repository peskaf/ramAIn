from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QIcon

from data import Data
from utils import validators

class AutoCroppingRelative(QFrame):
    """
    A widget for parameters selection for automatic relative cropping method.
    Relative cropping means that user inputs how many relative data units should be
    cut off of each of the sides.
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/cut.svg")

        # inputs
        self.init_inputs_value = 0

        self.from_start = QLineEdit(str(self.init_inputs_value), validator=validators.POSITIVE_INT_VALIDATOR)
        self.from_end = QLineEdit(str(self.init_inputs_value), validator=validators.POSITIVE_INT_VALIDATOR)

        # put widgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Spectral Plot Cropping - Relative"), 0, 0)

        layout.addWidget(QLabel("Data Points to Crop (Beginning)"), 1, 0)
        layout.addWidget(self.from_start, 1, 1)

        layout.addWidget(QLabel("Data Points to Crop (End)"), 2, 0)
        layout.addWidget(self.from_end, 2, 1)

        self.setLayout(layout)

    def get_params(self) -> tuple[int, int]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (int(self.from_start.text()), int(self.from_end.text()), )
        return parameters
    
    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        return f"crop from start: {int(self.from_start.text())}, crop from end: {int(self.from_end.text())}"

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_crop_relative.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Cropping - Relative"
