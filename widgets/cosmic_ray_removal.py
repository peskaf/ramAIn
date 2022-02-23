from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit, QRadioButton, QComboBox, QWidget, QStackedWidget, QFormLayout, QCheckBox
from PySide6.QtCore import Signal

# TODO: reset everyting to init state when exiting mode CRR
class CosmicRayRemoval(QFrame):
    # custom signal that user selected manual removal
    manual_removal_toggled = Signal(bool)
    show_maxima_sig = Signal(bool)

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
        self.manual_removal_btn.toggled.connect(self.fire_manual_removal_toggled)
        layout.addWidget(self.manual_removal_btn, 3, 0)

        layout.addWidget(QLabel("Start Position"), 4, 0)
        self.input_man_start = QLineEdit("0")
        # self.input_man_start.setEnabled(False) # allow to type sth only when given radiobtn is checked -> prevents accidents
        layout.addWidget(self.input_man_start, 4, 1)

        layout.addWidget(QLabel("End Position"), 5, 0)
        self.input_man_end = QLineEdit("0")
        # self.input_man_end.setEnabled(False)
        layout.addWidget(self.input_man_end, 5, 1)

        self.show_maxima = QCheckBox()
        self.show_maxima.toggled.connect(self.fire_show_maxima)
        layout.addWidget(self.show_maxima, 6, 1)
        layout.addWidget(QLabel("Show Maxima"), 6, 0)

        self.input_man_end.setEnabled(False)
        self.input_man_start.setEnabled(False)
        self.show_maxima.setEnabled(False)

        self.button = QPushButton("Apply")
        layout.addWidget(self.button, 7, 1)

        self.setLayout(layout)

    def SG_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param SG 1", QLineEdit())
        params_layout.addRow("Param SG 2", QLineEdit())
        self.SG_params.setLayout(params_layout)

    def med_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param med 1", QLineEdit())
        params_layout.addRow("Param med 2", QLineEdit())
        self.med_params.setLayout(params_layout)

    def ave_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param ave 1", QLineEdit())
        params_layout.addRow("Param ave 2", QLineEdit())
        self.ave_params.setLayout(params_layout)

    def CRR_paramsUI(self):
        params_layout = QFormLayout()
        params_layout.addRow("Param CRR 1", QLineEdit())
        params_layout.addRow("Param CRR 2", QLineEdit())
        self.CRR_params.setLayout(params_layout)

    def change_params(self, item_number):
        print(item_number)
        self.auto_methods_params.setCurrentIndex(item_number)

    # TODO: rename
    def fire_manual_removal_toggled(self):
        is_checked = self.manual_removal_btn.isChecked()
        self.input_man_end.setEnabled(is_checked)
        self.input_man_start.setEnabled(is_checked)
        self.show_maxima.setEnabled(is_checked)
        self.manual_removal_toggled.emit(is_checked)
        
    def update_manual_input_region(self, new_region):
        lo, hi = new_region.getRegion()
        self.input_man_start.setText(f"{lo:.2f}")
        self.input_man_end.setText(f"{hi:.2f}")

    def fire_show_maxima(self):
        self.show_maxima_sig.emit(self.show_maxima.isChecked())