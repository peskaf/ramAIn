from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Signal

import pyqtgraph as pg
import numpy as np

class Cropping(QFrame):
    """
    A widget for data cropping.

    Attributes: # TODO: prepsat sem vsechny atributy
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

        real_validator = QRegularExpressionValidator("-?[0-9]+(\.[0-9]+)?")

        # inputs
        self.input_plot_start = QLineEdit("0", validator=real_validator)
        self.input_plot_end = QLineEdit("0", validator=real_validator)

        self.input_map_left = QLineEdit("0", validator=real_validator)
        self.input_map_top = QLineEdit("0", validator=real_validator)
        self.input_map_right = QLineEdit("0", validator=real_validator)
        self.input_map_bottom = QLineEdit("0", validator=real_validator)

        # emit signal on button click (mainly for encapsulation purposes)
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_clicked.emit) 

        # put widgets into layout
        layout = QGridLayout()

        # Spectral map cropping parameters
        layout.addWidget(QLabel("Spectral Map Cropping"), 0, 0)

        layout.addWidget(QLabel("Upper Left Corner"), 2, 0)
        layout.addWidget(QLabel("Lower Right Corner"), 3, 0)
        layout.addWidget(QLabel("X"), 1, 1)
        layout.addWidget(QLabel("Y"), 1, 2)

        layout.addWidget(self.input_map_left, 2, 1)
        layout.addWidget(self.input_map_top, 2, 2)
        layout.addWidget(self.input_map_right, 3, 1)
        layout.addWidget(self.input_map_bottom, 3, 2)

        # Spectral plot cropping parameters
        layout.addWidget(QLabel("Spectral Plot Cropping"), 4, 0)

        layout.addWidget(QLabel("Start Position"), 5, 0)
        layout.addWidget(QLabel("End Position"), 6, 0)

        layout.addWidget(self.input_plot_start, 5, 1)
        layout.addWidget(self.input_plot_end, 6, 1)

        layout.addWidget(self.apply_button, 6, 2)

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
        """

        parameters = (float(self.input_plot_start.text()), float(self.input_plot_end.text()), \
            int(np.floor(float(self.input_map_left.text()))), int(np.floor(float(self.input_map_top.text()))), \
            int(np.ceil(float(self.input_map_right.text()))), int(np.ceil(float(self.input_map_bottom.text()))))
        return parameters

    def reset(self) -> None:
        ...

    def get_string_name(self):
        return "Cropping"
