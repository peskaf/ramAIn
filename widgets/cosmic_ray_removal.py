from PySide6.QtWidgets import QFrame, QPushButton, QGridLayout, QLabel, QLineEdit, QRadioButton, QComboBox, QWidget, QStackedWidget, QFormLayout, QCheckBox, QSlider
from PySide6.QtCore import Signal, Qt

class CosmicRayRemoval(QFrame):
    # custom signal that user selected manual removal
    manual_removal_toggled = Signal(bool)
    show_maxima_sig = Signal(bool)
    slider_slided = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()

        self.auto_removal_btn = QRadioButton("Automatic removal")
        self.auto_removal_btn.setChecked(True)
        layout.addWidget(self.auto_removal_btn, 0, 0)

        self.init_slider_value = 10
        self.slider = QSlider(Qt.Horizontal)
        #TODO: minimum 0 is too slow; change is too slow with large maps
        self.slider.setRange(10, 100)
        self.slider.setValue(self.init_slider_value) # init value
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setPageStep(5)

        self.slider.valueChanged.connect(self.update_label)
        self.slider.valueChanged.connect(self.fire_slider_change)

        self.label = QLabel(str(self.init_slider_value))
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        # self.label.setMinimumWidth(80)
        layout.addWidget(self.slider)
        layout.addWidget(self.label)

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

    def update_label(self, value):
        self.label.setText(str(value))

    def change_params(self, item_number):
        self.auto_methods_params.setCurrentIndex(item_number)

    # TODO: rename
    def fire_manual_removal_toggled(self):
        is_checked = self.manual_removal_btn.isChecked()
        self.input_man_end.setEnabled(is_checked)
        self.input_man_start.setEnabled(is_checked)
        self.show_maxima.setEnabled(is_checked)
        self.slider.setEnabled(not is_checked)
        self.manual_removal_toggled.emit(is_checked)
        
    def update_manual_input_region(self, new_region):
        lo, hi = new_region.getRegion()
        self.input_man_start.setText(f"{lo:.2f}")
        self.input_man_end.setText(f"{hi:.2f}")

    def fire_show_maxima(self):
        self.show_maxima_sig.emit(self.show_maxima.isChecked())
    
    def fire_slider_change(self, value):
        self.slider_slided.emit(value)
    
    def reset(self):
        self.auto_removal_btn.setChecked(True)
        self.manual_removal_btn.setChecked(False)
        
        self.slider.setValue(self.init_slider_value)

        # make sure "show maxima" is false and maxima are not being displayed
        self.show_maxima.setChecked(False)
        self.fire_show_maxima()



