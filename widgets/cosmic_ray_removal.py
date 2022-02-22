from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit, QRadioButton, QComboBox, QWidget, QStackedWidget, QFormLayout, QCheckBox

# TODO: show maxima -> change spectral map to display maximal values from data; if manual removal -> show linear region in plot and connect it to the inputs
class CosmicRayRemoval(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()

        self.auto_removal_btn = QRadioButton("Automatic removal")
        self.auto_removal_btn.setChecked(True)
        layout.addWidget(self.auto_removal_btn, 0, 0)

        self.auto_methods = QComboBox()
        self.auto_methods.addItems(["Savitzky-Golay", "Median", "Average", "CRR"])
        self.auto_methods.currentIndexChanged.connect(self.change_params)

        self.SG_params = QWidget()
        self.med_params = QWidget()
        self.ave_params = QWidget()
        self.CRR_params = QWidget()

        self.SG_paramsUI()
        self.med_paramsUI()
        self.ave_paramsUI()
        self.CRR_paramsUI()

        
        layout.addWidget(QLabel("Method Selection"), 1, 0)
        layout.addWidget(self.auto_methods, 1, 1)

        # individual methods parameters
        self.auto_methods_params = QStackedWidget(self)
        self.auto_methods_params.addWidget(self.SG_params)
        self.auto_methods_params.addWidget(self.med_params)
        self.auto_methods_params.addWidget(self.ave_params)
        self.auto_methods_params.addWidget(self.CRR_params)

        layout.addWidget(self.auto_methods_params, 2, 0, 1, 2) # span set -> position (4,0) span 1 row 2 cols
        layout.rowStretch(4)


        self.manual_removal_btn = QRadioButton("Manual removal")
        layout.addWidget(self.manual_removal_btn, 3, 0)

        layout.addWidget(QLabel("Start Position"), 4, 0)
        self.input_man_start = QLineEdit("0")
        layout.addWidget(self.input_man_start, 4, 1)
        layout.addWidget(QLabel("End Position"), 5, 0)
        self.input_man_end = QLineEdit("0")
        layout.addWidget(self.input_man_end, 5, 1)

        self.show_maxima = QCheckBox()
        layout.addWidget(self.show_maxima, 6, 1)
        layout.addWidget(QLabel("Show Maxima"), 6, 0)

        self.button = QPushButton("Apply")
        layout.addWidget(self.button, 7, 1)

        self.setLayout(layout)

    def SG_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param SG 1",QLineEdit())
        params_layout.addRow("Param SG 2",QLineEdit())
        self.SG_params.setLayout(params_layout)

    def med_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param med 1",QLineEdit())
        params_layout.addRow("Param med 2",QLineEdit())
        self.med_params.setLayout(params_layout)

    def ave_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param ave 1",QLineEdit())
        params_layout.addRow("Param ave 2",QLineEdit())
        self.ave_params.setLayout(params_layout)

    def CRR_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param CRR 1",QLineEdit())
        params_layout.addRow("Param CRR 2",QLineEdit())
        self.CRR_params.setLayout(params_layout)

    def change_params(self, item_number):
        print(item_number)
        self.auto_methods_params.setCurrentIndex(item_number)
        

"""
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

"""