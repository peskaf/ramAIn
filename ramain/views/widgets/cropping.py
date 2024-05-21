from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QGridLayout,
    QLabel,
    QLineEdit,
    QWidget,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal

import pyqtgraph as pg
import numpy as np

from ramain.utils import validators


class Cropping(QFrame):
    """
    A widget for cropping parameters selection in manual preprocessing.
    """

    # custom signal that `apply_button` has been clicked on
    apply_clicked = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for Cropping widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("ramain/resources/icons/cut.svg")

        self.init_inputs_value = 0

        # inputs
        self.input_plot_start = QLineEdit(
            str(self.init_inputs_value), validator=validators.REAL_VALIDATOR
        )
        self.input_plot_end = QLineEdit(
            str(self.init_inputs_value), validator=validators.REAL_VALIDATOR
        )

        self.input_map_left = QLineEdit(
            str(self.init_inputs_value), validator=validators.REAL_VALIDATOR
        )
        self.input_map_top = QLineEdit(
            str(self.init_inputs_value), validator=validators.REAL_VALIDATOR
        )
        self.input_map_right = QLineEdit(
            str(self.init_inputs_value), validator=validators.REAL_VALIDATOR
        )
        self.input_map_bottom = QLineEdit(
            str(self.init_inputs_value), validator=validators.REAL_VALIDATOR
        )

        # emit signal on button click (mainly for encapsulation purposes)
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit)

        # put widgets into layout
        layout = QGridLayout()

        # Spectral map cropping parameters
        layout.addWidget(QLabel("Spectral Map Cropping"), 0, 0)

        layout.addWidget(QLabel("X"), 1, 1)
        layout.addWidget(QLabel("Y"), 1, 2)

        layout.addWidget(QLabel("Upper Left Corner"), 2, 0)
        layout.addWidget(self.input_map_left, 2, 1)
        layout.addWidget(self.input_map_top, 2, 2)

        layout.addWidget(QLabel("Lower Right Corner"), 3, 0)
        layout.addWidget(self.input_map_right, 3, 1)
        layout.addWidget(self.input_map_bottom, 3, 2)

        # Spectral plot cropping parameters
        layout.addWidget(QLabel("Spectral Plot Cropping"), 4, 0)

        layout.addWidget(QLabel("Start Position"), 5, 0)
        layout.addWidget(self.input_plot_start, 5, 1)

        layout.addWidget(QLabel("End Position"), 6, 0)
        layout.addWidget(self.input_plot_end, 6, 1)

        layout.addWidget(self.apply_button, 6, 4)

        layout.setColumnStretch(3, 1)

        self.setLayout(layout)

    def update_crop_plot_inputs(self, new_region: pg.LinearRegionItem) -> None:
        """
        The function to update inputs on spectral plots crop parameters based on passed region.

        Parameters:
            new_region (pg.LinearRegionItem): Linear region to get its bounds from.
        """

        region_start, region_end = new_region.getRegion()
        self.input_plot_start.setText(f"{region_start:.2f}")
        self.input_plot_end.setText(f"{region_end:.2f}")

    def update_crop_pic_inputs(self, new_region: pg.RectROI) -> None:
        """
        The function to update inputs on spectral map crop parameters based on passed region.

        Parameters:
            new_region (pg.RectROI): Linear region to get its bounds from.
        """

        # floor upper left corner -> both coordinates decrease in the top-left direction; prevents cutting more than intended
        left, top = np.floor(new_region.pos())

        # ceil lower right corner -> both coordinates increase in the bottom-right direction
        right, bottom = np.ceil(new_region.pos() + new_region.size())

        # set inputs texts
        self.input_map_left.setText(str(left))
        self.input_map_top.setText(str(top))
        self.input_map_right.setText(str(right))
        self.input_map_bottom.setText(str(bottom))

    def get_params(self) -> tuple[float, float, int, int, int, int]:
        """
        The function to get parameters from all inputs.

        Returns:
            parameters (tuple): Tuple of cropping method parameters converted to correct types.
                                Order: plot start, plot end, map left, map top, map right, map bottom
        """

        parameters = (
            float(self.input_plot_start.text()),
            float(self.input_plot_end.text()),
            int(np.floor(float(self.input_map_left.text()))),
            int(np.floor(float(self.input_map_top.text()))),
            int(np.ceil(float(self.input_map_right.text()))),
            int(np.ceil(float(self.input_map_bottom.text()))),
        )

        return parameters

    def reset(self) -> None:
        """
        The function to reset all widgets to initial state.
        """

        inputs = [
            self.input_plot_start,
            self.input_plot_end,
            self.input_map_left,
            self.input_map_top,
            self.input_map_right,
            self.input_map_bottom,
        ]

        for input in inputs:
            input.setText(str(self.init_inputs_value))

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Cropping"
