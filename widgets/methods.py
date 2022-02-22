from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QStackedLayout, QHBoxLayout, QListWidget

from widgets.color import Color
from widgets.plot_mode import PlotMode
from widgets.cropping import Cropping
from widgets.cosmic_ray_removal import CosmicRayRemoval
from widgets.background_removal import BackgroundRemoval

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
        self.cosmic_ray_removal = CosmicRayRemoval()
        self.background_removal = BackgroundRemoval()
        
        self.methods_layout = QStackedLayout()
        self.methods_layout.addWidget(Color(QColor(240,240,240)))
        self.methods_layout.addWidget(self.cropping)
        self.methods_layout.addWidget(self.cosmic_ray_removal)
        self.methods_layout.addWidget(self.background_removal)
        self.methods_layout.setCurrentIndex(0)

        layout.addWidget(self.list)
        layout.addLayout(self.methods_layout)

        self.setLayout(layout)
    
    def set_current_widget(self, mode):
        if mode == PlotMode.VIEW:
            self.methods_layout.setCurrentIndex(0)
        elif mode == PlotMode.CROPPING:
            self.methods_layout.setCurrentIndex(1)
        elif mode == PlotMode.COSMIC_RAY_REMOVAL:
            self.methods_layout.setCurrentIndex(2)
        elif mode == PlotMode.BACKGROUND_REMOVAL:
            self.methods_layout.setCurrentIndex(3)


        # TODO: dopsat lepe ??
    
    # resets to init mode - view
    def reset(self):
        self.list.setCurrentItem(self.list.item(0))