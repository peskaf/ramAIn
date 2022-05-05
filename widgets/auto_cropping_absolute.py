from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QIcon

from data import Data
from utils import validators


class AutoCroppingAbsolute(QFrame):
    """
    A widget for parameters selection for automatic absolute cropping method.
    Absolute cropping means that user inputs absolute values of the bounds that the output
    should acquire.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto absolute cropping parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/cut.svg")

        # inputs
        self.init_inputs_value = 0

        self.input_plot_start = QLineEdit(str(self.init_inputs_value), validator=validators.REAL_VALIDATOR)
        self.input_plot_end = QLineEdit(str(self.init_inputs_value), validator=validators.REAL_VALIDATOR)

        # put widgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Spectral Plot Cropping - Absolute"), 0, 0)

        layout.addWidget(QLabel("Start Position"), 1, 0)
        layout.addWidget(self.input_plot_start, 1, 1)

        layout.addWidget(QLabel("End Position"), 2, 0)
        layout.addWidget(self.input_plot_end, 2, 1)

        self.setLayout(layout)

    def get_params(self) -> tuple[float, float]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (float(self.input_plot_start.text()), float(self.input_plot_end.text()), )
        return parameters
    
    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"x start: {float(self.input_plot_start.text())}, x end: {float(self.input_plot_end.text())}"
        return str_parameters

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_crop_absolute.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Cropping - Absolute"
