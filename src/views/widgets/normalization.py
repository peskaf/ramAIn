from PySide6.QtWidgets import (
    QFrame,
    QWidget,
    QLineEdit,
    QLabel,
    QGridLayout,
    QPushButton,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt

from utils import validators


class Normalization(QFrame):
    """
    A widget for parameters selection for the normalization method.
    """

    apply_clicked = Signal()
    threshold_changed = Signal(float)

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual normalization parameters selection widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("src/resources/icons/normalize.svg")

        self.init_threshold = 0.3

        self.threshold_range = (0.1, 0.8)
        self.threshold = QLineEdit(
            str(self.init_threshold), validator=validators.REAL_VALIDATOR
        )

        self.threshold.editingFinished.connect(self.validate_threshold_range)
        self.threshold.editingFinished.connect(self.emit_threshold_changed)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Distance Threshold"), 0, 0)
        layout.addWidget(self.threshold, 0, 1)

        layout.addWidget(self.apply_button, 1, 3)

        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

    def validate_threshold_range(self) -> None:
        """
        A function to validate inputs for `self.threshold`, setting it to one of the bounds
        if it's invalid.
        """

        step = float(self.threshold.text())
        if step < self.threshold_range[0]:
            self.threshold.setText(str(self.threshold_range[0]))
        elif step > self.threshold_range[1]:
            self.threshold.setText(str(self.threshold_range[1]))

    def get_params(self) -> tuple[float]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of normalization method parameters converted to correct types.
        """

        parameters = (float(self.threshold.text()),)

        return parameters

    def emit_threshold_changed(self) -> None:
        """
        Handler for `threshold_changed` signal emitting.
        """

        threshold = self.get_params()[0]

        # emit current threshold value
        self.threshold_changed.emit(threshold)

    def reset(self) -> None:
        """
        A function to reset all widgets to init state.
        """
        self.threshold.setText(str(self.init_threshold))

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Normalization"
