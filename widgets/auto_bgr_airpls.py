from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QWidget, QLineEdit
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from utils import validators
from data import Data


class AutoBGRairPLS(QFrame):
    """
    A widget for parameters selection for automatic airPLS method.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto airPLS parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")

        self.icon = QIcon("icons/background.svg")

        # inputs
        self.init_lambda = 10000
        self.lambda_ = QLineEdit(str(self.init_lambda), validator=validators.POSITIVE_INT_VALIDATOR)

        # put widgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Background Removal - airPLS"), 0, 0)
        
        layout.addWidget(QLabel("Lambda"), 1, 0)
        layout.addWidget(self.lambda_, 1, 1)

        layout.setColumnStretch(layout.columnCount(), 1)
        layout.setAlignment(Qt.AlignVCenter)

        self.setLayout(layout)

    def get_params(self) -> tuple[int]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (int(self.lambda_.text()), )
        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"lambda: {int(self.lambda_.text())}"
        return str_parameters

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_airPLS.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Background Removal - airPLS"
