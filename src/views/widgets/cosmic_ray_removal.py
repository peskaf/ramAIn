from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit, QRadioButton, QWidget, QCheckBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal

import pyqtgraph as pg

from utils import validators


class CosmicRayRemoval(QFrame):
    """
    A widget for cosmic ray removal parameters selection in manual preprocessing.
    """

    # custom signals
    manual_removal_toggled = Signal(bool)
    show_maxima_toggled = Signal(bool)
    apply_clicked = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for CosmicRayRemoval widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/signal.svg")

        self.auto_removal_btn = QRadioButton("Automatic Removal")
        self.auto_removal_btn.setChecked(True)

        self.manual_removal_btn = QRadioButton("Manual Removal")
        self.manual_removal_btn.toggled.connect(self.emit_manual_removal_toggled)

        # inputs for manual ray removal
        self.input_manual_start = QLineEdit("0", validator=validators.REAL_VALIDATOR)
        self.input_manual_start.setEnabled(False)

        self.input_manual_end = QLineEdit("0", validator=validators.REAL_VALIDATOR)
        self.input_manual_end.setEnabled(False)

        self.show_maxima = QCheckBox()
        self.show_maxima.toggled.connect(self.emit_show_maxima)
        self.show_maxima.setEnabled(False)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put windgets into layout
        layout = QGridLayout()

        layout.addWidget(self.auto_removal_btn, 0, 0)

        layout.addWidget(self.manual_removal_btn, 2, 0)

        layout.addWidget(QLabel("Start Position"), 3, 0)
        layout.addWidget(self.input_manual_start, 3, 1)

        layout.addWidget(QLabel("End Position"), 4, 0)
        layout.addWidget(self.input_manual_end, 4, 1)

        layout.addWidget(QLabel("Show Maxima"), 5, 0)
        layout.addWidget(self.show_maxima, 5, 1)
        
        layout.addWidget(self.apply_button, 6, 3)

        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

    def emit_manual_removal_toggled(self) -> None:
        """
        Handler for `self.manual_removal_toggled` signal emitting.
        """

        is_checked = self.manual_removal_btn.isChecked()

        # manual removal editable widgets
        self.input_manual_end.setEnabled(is_checked)
        self.input_manual_start.setEnabled(is_checked)
        self.show_maxima.setEnabled(is_checked)

        self.manual_removal_toggled.emit(is_checked)

    def emit_show_maxima(self) -> None:
        """
        Handler for `self.show_maxima_toggled` signal emitting.
        """

        self.show_maxima_toggled.emit(self.show_maxima.isChecked())
     
    def update_manual_input_region(self, new_region: pg.LinearRegionItem) -> None:
        """
        The function to update inputs on manual removal based on passed region.

        Parameters:
            new_region (pg.LinearRegionItem): Linear region to get its bounds from.  
        """

        region_start, region_end = new_region.getRegion()
        self.input_manual_start.setText(f"{region_start:.2f}")
        self.input_manual_end.setText(f"{region_end:.2f}")

    def reset(self) -> None:
        """
        The function to reset all widgets to initial state.
        """

        self.auto_removal_btn.setChecked(True)
        self.manual_removal_btn.setChecked(False)

        # make sure "show maxima" is false and maxima are not being displayed
        self.show_maxima.setChecked(False)
        # will emit False as it was set on prev line -> info for spectral map visualizers
        self.emit_show_maxima()

    def get_params(self) -> tuple[float, float]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of CRR method parameters converted to correct types.
        """

        parameters = (float(self.input_manual_start.text()), float(self.input_manual_end.text()),)
        return parameters

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Cosmic Ray Removal"
