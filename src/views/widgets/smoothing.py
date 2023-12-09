from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QPushButton,
    QWidget,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from utils import validators


class Smoothing(QFrame):
    """
    A widget for parameters selection for manual smoothing.
    """

    # custom signals
    savgol_toggled = Signal(bool)
    window_length_changed = Signal(int)
    diff_changed = Signal(int)
    poly_order_changed = Signal(int)
    lambda_changed = Signal(int)
    apply_clicked = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual bg subtraction parameters selection widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("src/resources/icons/background.svg")

        self.whittaker_btn = QRadioButton("Whittaker")
        self.whittaker_btn.setChecked(True)

        self.init_lambda = 1600
        self.init_diff = 2

        self.savgol_btn = QRadioButton("Savgol")
        self.savgol_btn.toggled.connect(self.emit_savgol_toggled)

        self.init_poly_order = 2
        self.init_window_length = 5

        # NOTE: range is inclusive on both sides
        self.poly_order_range = (1, 6)
        self.poly_order = QLineEdit(
            str(self.init_poly_order), validator=validators.INT_VALIDATOR
        )

        self.poly_order.editingFinished.connect(self.validate_poly_order_range)
        self.poly_order.editingFinished.connect(self.emit_poly_order_changed)

        self.lambda_range = (1, 2000)
        self.lam = QLineEdit(str(self.init_lambda), validator=validators.INT_VALIDATOR)

        self.lam.editingFinished.connect(self.validate_lambda_range)
        self.lam.editingFinished.connect(self.emit_lambda_changed)

        self.diff_range = (1, 5)
        self.diff = QLineEdit(str(self.init_diff), validator=validators.INT_VALIDATOR)

        self.diff.editingFinished.connect(self.validate_diff_range)
        self.diff.editingFinished.connect(self.emit_diff_changed)

        self.wl_range = (3, 9)
        self.wl = QLineEdit(
            str(self.init_window_length), validator=validators.INT_VALIDATOR
        )

        self.wl.editingFinished.connect(self.validate_wl_range)
        self.wl.editingFinished.connect(self.emit_wl_changed)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put widgets into layout
        layout = QGridLayout()

        layout.addWidget(self.whittaker_btn, 0, 0)

        layout.addWidget(QLabel("Lambda"), 1, 0)
        layout.addWidget(self.lam, 1, 1)

        layout.addWidget(QLabel("Diff"), 2, 0)
        layout.addWidget(self.diff, 2, 1)

        layout.addWidget(self.savgol_btn, 3, 0)

        layout.addWidget(QLabel("Window Length"), 4, 0)
        layout.addWidget(self.wl, 4, 1)

        layout.addWidget(QLabel("Poly Order"), 5, 0)
        layout.addWidget(self.poly_order, 5, 1)

        layout.addWidget(self.apply_button, 6, 3)

        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

    def emit_savgol_toggled(self) -> None:
        """
        Handler for `savgol_toggled` signal emitting.
        """

        is_checked = self.savgol_btn.isChecked()

        # disable input into whittaker params
        self.lam.setEnabled(not is_checked)
        self.diff.setEnabled(not is_checked)
        self.poly_order.setEnabled(is_checked)
        self.wl.setEnabled(is_checked)

        # emit whether savgol button is checked
        self.savgol_toggled.emit(is_checked)

    def validate_poly_order_range(self) -> None:
        """
        The function to validate range of `poly_order` input, setting it to one of the bounds
        if it's invalid.
        """

        poly_order = int(self.poly_order.text())
        if poly_order < self.poly_order_range[0]:
            self.poly_order.setText(str(self.poly_order_range[0]))
        elif poly_order > self.poly_order_range[1]:
            self.poly_order.setText(str(self.poly_order_range[1]))

    def validate_lambda_range(self) -> None:
        """
        The function to validate range of `lam(bda)` input, setting it to one of the bounds
        if it's invalid.
        """

        lam = int(self.lam.text())
        if lam < self.lambda_range[0]:
            self.lam.setText(str(self.lambda_range[0]))
        elif lam > self.lambda_range[1]:
            self.lam.setText(str(self.lambda_range[1]))

    def validate_diff_range(self) -> None:
        """
        The function to validate range of `diff` input, setting it to one of the bounds
        if it's invalid.
        """

        diff = int(self.diff.text())
        if diff < self.diff_range[0]:
            self.diff.setText(str(self.diff_range[0]))
        elif diff > self.lambda_range[1]:
            self.diff.setText(str(self.diff_range[1]))

    def validate_wl_range(self) -> None:
        """
        The function to validate range of `wl (window_length)` input, setting it to one of the bounds
        if it's invalid.
        """

        wl = int(self.wl.text())
        if wl < self.wl_range[0]:
            self.wl.setText(str(self.wl_range[0]))
        elif wl > self.wl_range[1]:
            self.wl.setText(str(self.wl_range[1]))

    def emit_poly_order_changed(self) -> None:
        """
        Handler for `poly_deg_changed` signal emitting.
        """

        poly_order_value = int(self.poly_order.text())

        # emit current value of `self.poly_order`
        self.poly_order_changed.emit(poly_order_value)

    def emit_lambda_changed(self) -> None:
        """
        Handler for `lambda_changed` signal emitting.
        """

        lam_value = int(self.lam.text())

        # emit current value of `self.lam`
        self.lambda_changed.emit(lam_value)

    def emit_wl_changed(self) -> None:
        """
        Handler for `wl_changed` signal emitting.
        """

        wl_value = int(self.wl.text())

        # emit current value of `self.wl`
        self.window_length_changed.emit(wl_value)

    def emit_diff_changed(self) -> None:
        """
        Handler for `diff_changed` signal emitting.
        """

        diff_value = int(self.diff.text())

        # emit current value of `self.diff`
        self.diff_changed.emit(diff_value)

    def get_params(self) -> tuple[int, bool]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of smoothing method parameters converted to correct types.
        """

        parameters = (
            int(self.lam.text()),
            int(self.diff.text()),
            int(self.wl.text()),
            int(self.poly_order.text()),
        )
        return parameters

    def reset(self) -> None:
        """
        The function to reset all widgets to initial state.
        """

        self.whittaker_btn.setChecked(True)
        self.poly_order.setText(str(self.init_poly_order))
        self.diff.setText(str(self.init_diff))
        self.wl.setText(str(self.init_window_length))
        self.lam.setText(str(self.init_lambda))

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Smoothing"
