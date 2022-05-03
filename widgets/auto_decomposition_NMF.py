from PySide6.QtWidgets import QFrame, QGridLayout, QLineEdit, QLabel
from PySide6.QtGui import QRegularExpressionValidator, QIcon

from data import Data

class AutoNMF(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/pie.svg")

        int_validator = QRegularExpressionValidator("-?[0-9]+")

        self.init_num_of_components = 5
        self.components_range = (2, 10)

        self.num_of_components = QLineEdit(str(self.init_num_of_components), validator=int_validator)
        self.num_of_components.editingFinished.connect(self.validate_components_range)

        layout = QGridLayout()

        layout.addWidget(QLabel("Decomposition - NMF"), 0, 0)
        layout.addWidget(QLabel("Number of components"), 1, 0)
        layout.addWidget(self.num_of_components, 1, 1)

        self.setLayout(layout)

    def reset(self):
        self.num_of_components.setText(str(self.init_num_of_components))

    def validate_components_range(self) -> None:
        """
        The function to validate range of number of components input.
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

    def params_to_text(self) -> str:
        return f"components: {int(self.num_of_components.text())}"

    def function_name(self) -> str:
        return Data.auto_NMF.__name__

    def get_string_name(self):
        return "Decomposition - NMF"