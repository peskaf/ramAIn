from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QIcon

from data import Data
from utils import validators


class AutoLinearization(QFrame):
    """
    A widget for parameters selection for automatic linearization method.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto linearization parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/equal.svg")

        self.init_data_step = 1

        # range is inclusive on both sides
        self.data_step_range = (0.1, 5)
        self.data_step = QLineEdit(str(self.init_data_step), validator=validators.REAL_VALIDATOR)
        self.data_step.editingFinished.connect(self.validate_data_step_range)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Linearization"), 0, 0)

        layout.addWidget(QLabel("Step"), 1, 0)
        layout.addWidget(self.data_step, 1, 1)
      
        self.setLayout(layout)
    
    def validate_data_step_range(self) -> None:
        """
        A function to validate range of linearization step, setting it to one of the bounds
        if it's invalid.
        """

        step = float(self.data_step.text())
        if step < self.data_step_range[0]:
            self.data_step.setText(str(self.data_step_range[0]))
        elif step > self.data_step_range[1]:
            self.data_step.setText(str(self.data_step_range[1]))

    def get_params(self) -> tuple[float]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (float(self.data_step.text()), )
        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"step size: {float(self.data_step.text())}"
        return str_parameters

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_linearize.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Linearization"
