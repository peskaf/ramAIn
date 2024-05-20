from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal

from utils import validators


class Linearization(QFrame):
    """
    A widget for parameters selection for linarization method in manual preprocessing section.
    """

    # singal that apply button was clicked
    apply_clicked = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual linearization parameters selection widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("src/resources/icons/equal.svg")

        self.init_data_step = 1

        # range is inclusive on both sides
        self.data_step_range = (0.1, 5)
        self.data_step = QLineEdit(
            str(self.init_data_step), validator=validators.REAL_VALIDATOR
        )

        self.data_step.editingFinished.connect(self.validate_data_step_range)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Step (1/cm)"), 0, 0)
        layout.addWidget(self.data_step, 0, 1)

        layout.addWidget(self.apply_button, 1, 3)

        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

    def validate_data_step_range(self) -> None:
        """
        A function to validate inputs for `self.data_step`, setting it to one of the bounds
        if it's invalid.
        """

        step = float(self.data_step.text())
        if step < self.data_step_range[0]:
            self.data_step.setText(str(self.data_step_range[0]))
        elif step > self.data_step_range[1]:
            self.data_step.setText(str(self.data_step_range[1]))

    def get_params(self) -> tuple[float]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of linearization method parameters converted to correct types.
        """

        parameters = (float(self.data_step.text()),)

        return parameters

    def reset(self) -> None:
        """
        The function to reset all widgets to initial state.
        """

        self.data_step.setText(str(self.init_data_step))

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "X-axis Linearization"
