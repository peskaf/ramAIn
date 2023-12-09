from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QCheckBox,
    QPushButton,
    QWidget,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from utils import validators


class BackgroundRemoval(QFrame):
    """
    A widget for parameters selection for manual background removal.
    """

    # custom signals
    math_morpho_toggled = Signal(bool)
    bubblefill_toggled = Signal(bool)
    poly_deg_changed = Signal(int)
    water_bubble_size_changed = Signal(int)
    bubble_size_changed = Signal(int)
    ignore_water_band_toggled = Signal(bool)
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

        self.poly_fit_btn = QRadioButton("Poly-fit (I-ModPoly)")
        self.poly_fit_btn.setChecked(True)

        self.bubblefill_btn = QRadioButton("BubbleFill")
        self.bubblefill_btn.toggled.connect(self.emit_bubblefill_toggled)

        self.math_morpho_btn = QRadioButton("Mathematical Morphology")
        self.math_morpho_btn.toggled.connect(self.emit_math_morpho_toggled)

        self.init_water_bubble_size = 700
        self.init_bubble_size = 100

        self.bubble_range = (1, 1000)

        self.water_bubble_size = QLineEdit(
            str(self.init_water_bubble_size), validator=validators.INT_VALIDATOR
        )
        self.water_bubble_size.editingFinished.connect(self.validate_bubble_size_range)
        self.water_bubble_size.editingFinished.connect(
            self.emit_water_bubble_size_changed
        )

        self.bubble_size = QLineEdit(
            str(self.init_bubble_size), validator=validators.INT_VALIDATOR
        )
        self.bubble_size.editingFinished.connect(self.validate_bubble_size_range)
        self.bubble_size.editingFinished.connect(self.emit_bubble_size_changed)

        self.init_poly_deg = 5
        # NOTE: range is inclusive on both sides
        self.poly_deg_range = (1, 15)
        self.poly_deg = QLineEdit(
            str(self.init_poly_deg), validator=validators.INT_VALIDATOR
        )
        self.poly_deg.editingFinished.connect(self.validate_poly_deg_range)
        self.poly_deg.editingFinished.connect(self.emit_poly_deg_changed)

        self.ignore_water_band = QCheckBox()
        self.ignore_water_band.toggled.connect(self.emit_ignore_water_band)
        self.ignore_water_band.setChecked(True)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put widgets into layout
        layout = QGridLayout()

        layout.addWidget(QLabel("Ignore Water Band"), 0, 0)
        layout.addWidget(self.ignore_water_band, 0, 1)

        layout.addWidget(self.poly_fit_btn, 1, 0)

        layout.addWidget(QLabel("Polynom Degree"), 2, 0)
        layout.addWidget(self.poly_deg, 2, 1)

        layout.addWidget(self.math_morpho_btn, 3, 0)

        layout.addWidget(self.bubblefill_btn, 4, 0)
        layout.addWidget(QLabel("Bubble Sizes (non-water | water)"), 5, 0)
        layout.addWidget(self.water_bubble_size, 5, 1)
        layout.addWidget(self.bubble_size, 5, 2)

        layout.addWidget(self.apply_button, 6, 3)

        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

    def emit_math_morpho_toggled(self) -> None:
        """
        Handler for `math_morpho_toggled` signal emitting.
        """

        is_checked = self.math_morpho_btn.isChecked()

        # disable input into `poly_deg`
        self.poly_deg.setEnabled(not is_checked)
        self.water_bubble_size.setEnabled(not is_checked)
        self.bubble_size.setEnabled(not is_checked)

        # emit whether math_morpho button is checked
        self.math_morpho_toggled.emit(is_checked)

    def emit_bubblefill_toggled(self) -> None:
        """
        Handler for `bubblefill_toggled` signal emitting.
        """

        is_checked = self.bubblefill_btn.isChecked()

        # disable input into `poly_deg`
        self.poly_deg.setEnabled(not is_checked)
        self.water_bubble_size.setEnabled(is_checked)
        self.bubble_size.setEnabled(is_checked)

        # emit whether bubblefill button is checked
        self.bubblefill_toggled.emit(is_checked)

    def validate_poly_deg_range(self) -> None:
        """
        The function to validate range of `poly_deg` input, setting it to one of the bounds
        if it's invalid.
        """

        poly_deg = int(self.poly_deg.text())
        if poly_deg < self.poly_deg_range[0]:
            self.poly_deg.setText(str(self.poly_deg_range[0]))
        elif poly_deg > self.poly_deg_range[1]:
            self.poly_deg.setText(str(self.poly_deg_range[1]))

    def emit_poly_deg_changed(self) -> None:
        """
        Handler for `poly_deg_changed` signal emitting.
        """

        poly_deg_value = int(self.poly_deg.text())

        # emit current value of `self.poly_deg`
        self.poly_deg_changed.emit(poly_deg_value)

    def emit_ignore_water_band(self) -> None:
        """
        Handler for `ignore_water_band_toggled` signal emitting.
        """

        # emit whether `self.ignore_water_band` is checked right now
        self.ignore_water_band_toggled.emit(self.ignore_water_band.isChecked())

    def validate_bubble_size_range(self) -> None:
        bubbles = [self.bubble_size, self.water_bubble_size]

        for bubble in bubbles:
            bubble_size = int(bubble.text())
            if bubble_size < self.bubble_range[0]:
                bubble.setText(str(self.bubble_range[0]))
            elif bubble_size > self.bubble_range[1]:
                bubble.setText(str(self.bubble_range[1]))

    def emit_water_bubble_size_changed(self) -> None:
        """
        Handler for `water_bubble_size_changed` signal emitting.
        """

        bubble_size = int(self.water_bubble_size.text())
        self.water_bubble_size_changed.emit(bubble_size)

    def emit_bubble_size_changed(self) -> None:
        """
        Handler for `bubble_size_changed` signal emitting.
        """
        bubble_size = int(self.bubble_size.text())
        self.bubble_size_changed.emit(bubble_size)

    def get_params(self) -> tuple[int, bool]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of background removal method parameters converted to correct types.
        """

        parameters = (
            int(self.poly_deg.text()),
            self.ignore_water_band.isChecked(),
            int(self.bubble_size.text()),
            int(self.water_bubble_size.text()),
        )
        return parameters

    def reset(self) -> None:
        """
        The function to reset all widgets to initial state.
        """

        self.poly_fit_btn.setChecked(True)
        self.ignore_water_band.setChecked(True)
        self.poly_deg.setText(str(self.init_poly_deg))
        self.water_bubble_size.setText(str(self.init_water_bubble_size))
        self.bubble_size.setText(str(self.init_bubble_size))

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Background Removal"
