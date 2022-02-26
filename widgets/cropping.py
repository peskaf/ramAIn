from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit
from PySide6.QtGui import QRegularExpressionValidator

import numpy as np

class Cropping(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()

        # Spectral map cropping parameters
        layout.addWidget(QLabel("Spectral Map Cropping"), 0, 0)
        layout.addWidget(QLabel("Upper Left Corner"), 2, 0)
        layout.addWidget(QLabel("Lower Right Corner"), 3, 0)
        layout.addWidget(QLabel("X"), 1, 1)
        layout.addWidget(QLabel("Y"), 1, 2)

        real = "-?[0-9]+(.[0-9]+)?"

        self.input_map_ULX = QLineEdit("0", validator=QRegularExpressionValidator(real))
        self.input_map_ULY = QLineEdit("0", validator=QRegularExpressionValidator(real))
        self.input_map_LRX = QLineEdit("0", validator=QRegularExpressionValidator(real))
        self.input_map_LRY = QLineEdit("0", validator=QRegularExpressionValidator(real))

        layout.addWidget(self.input_map_ULX, 2, 1)
        layout.addWidget(self.input_map_ULY, 2, 2)
        layout.addWidget(self.input_map_LRX, 3, 1)
        layout.addWidget(self.input_map_LRY, 3, 2)

        # Spectral plot cropping parameters
        layout.addWidget(QLabel("Spectral Plot Cropping"), 4, 0)

        layout.addWidget(QLabel("Start Position"), 5, 0)
        layout.addWidget(QLabel("End Position"), 6, 0)

        
        self.input_plot_start = QLineEdit("0", validator=QRegularExpressionValidator(real))
        self.input_plot_end = QLineEdit("0", validator=QRegularExpressionValidator(real))

        layout.addWidget(self.input_plot_start, 5, 1)
        layout.addWidget(self.input_plot_end, 6, 1)

        self.button = QPushButton("Apply")
        layout.addWidget(self.button, 6, 2)

        self.setLayout(layout)

    # set changed values to given QLineEdit objects
    def update_crop_plot_region(self, new_region):
        lo, hi = new_region.getRegion()
        self.input_plot_start.setText(f"{lo:.2f}")
        self.input_plot_end.setText(f"{hi:.2f}")
    
    def update_crop_pic_region(self, new_roi):
        upper_left_corner = new_roi.pos()
        lower_right_corner = new_roi.pos() + new_roi.size()

        # floor upper left corner -> both coordinates decrease in the top-left direction; prevents cutting more than intended 
        self.input_map_ULX.setText(f"{np.floor(upper_left_corner[0])}")
        self.input_map_ULY.setText(f"{np.floor(upper_left_corner[1])}")
        # ceil lower right corner -> both coordinates increase in the bottom-right direction
        self.input_map_LRX.setText(f"{np.ceil(lower_right_corner[0])}")
        self.input_map_LRY.setText(f"{np.ceil(lower_right_corner[1])}")

    def get_params(self):
        return float(self.input_plot_start.text()), float(self.input_plot_end.text()), int(np.floor(float(self.input_map_ULX.text()))), \
         int(np.floor(float(self.input_map_ULY.text()))), int(np.ceil(float(self.input_map_LRX.text()))), int(np.ceil(float(self.input_map_LRY.text())))