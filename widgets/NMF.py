from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLineEdit, QLabel, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt

from utils import validators

class NMF(QFrame):
    """
    A widget for parameters selection for the NMF decomposition method.
    """

    apply_clicked = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual NMF decomposition parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/pie.svg")

        self.init_num_of_components = 5
        self.components_range = (2, 10)

        self.num_of_components = QLineEdit(str(self.init_num_of_components), validator=validators.POSITIVE_INT_VALIDATOR)
        self.num_of_components.editingFinished.connect(self.validate_components_range)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        layout = QGridLayout()

        layout.addWidget(QLabel("Number of components"), 0, 0)
        layout.addWidget(self.num_of_components, 0, 1)
        layout.addWidget(self.apply_button, 1, 3)

        layout.setColumnStretch(2, 1)

        layout.setAlignment(Qt.AlignVCenter)

        self.setLayout(layout)

    def validate_components_range(self) -> None:
        """
        A function to validate range of number of components input, setting it to one of the bounds
        if the input is invalid.
        """

        components = float(self.num_of_components.text())
        if components < self.components_range[0]:
            self.num_of_components.setText(str(self.components_range[0]))
        elif components > self.components_range[1]:
            self.num_of_components.setText(str(self.components_range[1]))

    def get_params(self) -> tuple[int]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of NMF method parameters converted to correct types.
        """

        parameters = (int(self.num_of_components.text()),)
        return parameters

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "NMF"
