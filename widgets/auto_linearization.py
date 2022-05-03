from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit
from PySide6.QtGui import QRegularExpressionValidator, QIcon

from widgets.data import Data

class AutoLinearization(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("method_instance")
        self.icon = QIcon("icons/equal.svg")

        # TODO: move these validators to sep. utils file ??
        real_validator = QRegularExpressionValidator("-?[0-9]+(\.[0-9]+)?")

        self.init_data_step = 1

        # range is inclusive on both sides
        self.data_step_range = (0.1, 5)
        self.data_step = QLineEdit(str(self.init_data_step), validator=real_validator)
    
        self.data_step.editingFinished.connect(self.validate_data_step_range)

      
        # put windgets into layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Linearization"), 0, 0)
        layout.addWidget(QLabel("Step"), 1, 0)
        layout.addWidget(self.data_step, 1, 1)
      
        self.setLayout(layout)
    
    def validate_data_step_range(self) -> None:

        step = float(self.data_step.text())
        if step < self.data_step_range[0]:
            self.data_step.setText(str(self.data_step_range[0]))
        elif step > self.data_step_range[1]:
            self.data_step.setText(str(self.data_step_range[1]))

    def get_params(self) -> tuple[float]:

        parameters = (float(self.data_step.text()), )
        return parameters

    def params_to_text(self) -> str:
        return f"step size: {float(self.data_step.text())}"

    def reset(self) -> None:
        """
        The function to reset all widgets to initial state.
        """

        self.data_step.setText(str(self.init_data_step))

    def function_name(self) -> str:
        return Data.auto_linearize.__name__

    def get_string_name(self):
        return "Linearization"
