from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QStackedLayout, QHBoxLayout, QListWidget

from widgets.color import Color
from widgets.plot_mode import PlotMode
from widgets.cropping import Cropping

class Methods(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("methods")

        layout = QHBoxLayout()


        methods = ["View", "Cropping", "Cosmic Ray Removal", "Background Removal"]

        self.list = QListWidget()
        self.list.setObjectName("methods_list") # nastavit velikost pevnou
        self.list.addItems(methods)
        self.list.setCurrentItem(self.list.item(0))
        self.list.setSortingEnabled(False) # do not sort list items (methods)

        self.cropping = Cropping()
        
        self.methods_layout = QStackedLayout()
        self.methods_layout.addWidget(Color(QColor(240,240,240)))
        self.methods_layout.addWidget(self.cropping)
        self.methods_layout.setCurrentIndex(0)

        layout.addWidget(self.list)
        layout.addLayout(self.methods_layout)

        self.setLayout(layout)
    
    def set_current_widget(self, mode):
        if mode == PlotMode.CROPPING:
            self.methods_layout.setCurrentIndex(1)
        elif mode == PlotMode.VIEW:
            self.methods_layout.setCurrentIndex(0)
        # TODO: dopsat lepe
    
    # resets to init mode - view
    def reset(self):
        self.list.setCurrentItem(self.list.item(0))