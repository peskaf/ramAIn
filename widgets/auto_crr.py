from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from data import Data


class AutoCRR(QFrame):
    """
    A widget for parameters selection for automatic cosmic ray removal method.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto cosmic ray removal parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/signal.svg")

        # put widgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Cosmic Ray Removal"), 0, 0)
        layout.addWidget(QLabel("No parameters to be set."), 1, 0)

        layout.setColumnStretch(layout.columnCount(), 1)
        layout.setAlignment(Qt.AlignVCenter)

        self.setLayout(layout)

    def get_params(self) -> tuple:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = ()
        return parameters
    
    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f""
        return str_parameters

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_remove_spikes.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Cosmic Ray Removal"
