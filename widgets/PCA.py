from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLineEdit, QLabel
from PySide6.QtGui import QRegularExpressionValidator, QIcon
from PySide6.QtCore import Signal

class PCA(QFrame):

    apply_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/view.svg") #TODO: change

        int_validator = QRegularExpressionValidator("-?[0-9]+")

        self.init_num_of_components = 5
        self.components_range = (2, 10)

        self.num_of_components = QLineEdit(str(self.init_num_of_components), validator=int_validator)
        self.num_of_components.editingFinished.connect(self.validate_components_range)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        layout = QGridLayout()

        layout.addWidget(QLabel("Number of components"), 0, 0)
        layout.addWidget(self.num_of_components, 0, 1)
        layout.addWidget(self.apply_button, 1, 1)

        self.setLayout(layout)

    def reset(self):
        ...

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
            parameters (tuple): Tuple of PCA method parameters converted to correct types.
        """

        parameters = (int(self.num_of_components.text()),)
        return parameters

    def get_string_name(self):
        return "PCA"