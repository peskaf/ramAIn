from PySide6.QtWidgets import QFrame, QGridLayout, QLineEdit, QLabel, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from data import Data
from utils import validators


class AutoPCA(QFrame):
    """
    A widget for parameters selection for automatic PCA decomposition method.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for auto PCA decomposition parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/pie.svg")

        self.init_num_of_components = 5
        self.components_range = (2, 10)

        self.num_of_components = QLineEdit(str(self.init_num_of_components), validator=validators.INT_VALIDATOR)
        self.num_of_components.editingFinished.connect(self.validate_components_range)

        layout = QGridLayout()

        layout.addWidget(QLabel("Decomposition - PCA"), 0, 0)

        layout.addWidget(QLabel("Number of components"), 1, 0)
        layout.addWidget(self.num_of_components, 1, 1)

        layout.setColumnStretch(layout.columnCount(), 1)
        layout.setAlignment(Qt.AlignVCenter)

        self.setLayout(layout)

    def validate_components_range(self) -> None:
        """
        A function to validate range of number of components input, setting it to one of the bounds
        if it's invalid.
        """

        components = float(self.num_of_components.text())
        if components < self.components_range[0]:
            self.num_of_components.setText(str(self.components_range[0]))
        elif components > self.components_range[1]:
            self.num_of_components.setText(str(self.components_range[1]))

    def get_params(self) -> tuple[int]:
        """
        A function to return parameters of the method with the correct types.

        Returns:
            parameters (tuple): Tuple of method's parameters.
        """

        parameters = (int(self.num_of_components.text()),)
        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding meanings.

        Returns:
            str_parameters (str): String of parameters and their meaning.
        """

        str_parameters = f"components: {int(self.num_of_components.text())}"
        return str_parameters

    def function_name(self) -> str:
        """
        A function to return name of the function that this widget represents.

        Returns:
            function_name (str): Name of the function that the parameters from this widget are for.
        """

        return Data.auto_PCA.__name__

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Decomposition - PCA"