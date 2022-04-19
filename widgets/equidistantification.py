from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QRadioButton, QCheckBox, QPushButton
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Signal

class Equidistantification(QFrame):
    apply_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO: move these validators to sep. utils file ??
        real_validator = QRegularExpressionValidator("-?[0-9]+(\.[0-9]+)?")

        self.init_data_step = 1

        # range is inclusive on both sides
        self.data_step_range = (0.1, 5)
        self.data_step = QLineEdit(str(self.init_data_step), validator=real_validator)
    
        self.data_step.editingFinished.connect(self.validate_data_step_range)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Step"), 0, 0)
        layout.addWidget(self.data_step, 0, 1)

        layout.addWidget(self.apply_button, 1, 1)
        
        self.setLayout(layout)
    
    def validate_data_step_range(self) -> None:

        step = float(self.data_step.text())
        if step < self.data_step_range[0]:
            self.data_step.setText(str(self.data_step_range[0]))
        elif step > self.data_step_range[1]:
            self.data_step.setText(str(self.data_step_range[1]))

    def get_params(self) -> tuple[float]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of equidistantification method parameters converted to correct types.
        """

        parameters = (float(self.data_step.text()), )
        return parameters

    def reset(self) -> None:
        """
        The function to reset all widgets to initial state.
        """

        self.data_step.setText(str(self.init_data_step))

    def get_string_name(self):
        return "Equidistantification"
