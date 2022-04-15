from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QStackedLayout, QHBoxLayout, QListWidget
from PySide6.QtCore import Signal

from widgets.color import Color
from widgets.plot_mode import PlotMode
from widgets.cropping import Cropping
from widgets.cosmic_ray_removal import CosmicRayRemoval
from widgets.background_removal import BackgroundRemoval
from widgets.normalization import Normalization
from widgets.equidistantification import Equidistantification
from widgets.view import View

class Methods(QFrame):
    method_changed = Signal(QFrame) # TODO: vsechny metody budou dedit od mnou vytvoreneho widgetu nejakeho, tak sem ten jejich rodic!

    def __init__(self, parent=None):
        super().__init__(parent)

        # name for qss styling
        self.setObjectName("methods")

        self.view = View()
        self.cropping = Cropping()
        self.cosmic_ray_removal = CosmicRayRemoval()
        self.background_removal = BackgroundRemoval()
        self.normalization = Normalization()
        self.equidistantification = Equidistantification()

        self.methods = [
            self.view,
            self.cropping,
            self.cosmic_ray_removal,
            self.equidistantification,
            self.normalization,
            self.background_removal,
        ]

        self.list = QListWidget()
        self.list.setObjectName("methods_list") # TODO: set fixed size ?
        self.list.addItems([method.get_string_name() for method in self.methods])
        
        self.list.setCurrentItem(self.list.item(0))
        # do not sort list items (methods) as they are in specific ored
        self.list.setSortingEnabled(False) 

        self.methods_layout = QStackedLayout()

        for method in self.methods:
            self.methods_layout.addWidget(method)

        self.methods_layout.setCurrentIndex(0)
        self.list.currentItemChanged.connect(self.emit_method_changed)

        layout = QHBoxLayout()
        layout.addWidget(self.list)
        layout.addLayout(self.methods_layout)
        self.setLayout(layout)
    
    # resets to init mode - first method (view)
    def reset(self):
        self.list.setCurrentItem(self.list.item(0))

    def emit_method_changed(self):
        curr_method_index = self.list.currentRow()
        self.methods_layout.setCurrentIndex(curr_method_index)
        self.method_changed.emit(self.methods[curr_method_index])
