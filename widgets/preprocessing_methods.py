from PySide6.QtWidgets import QFrame, QStackedLayout, QHBoxLayout, QListWidget
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon

from widgets.cropping import Cropping
from widgets.cosmic_ray_removal import CosmicRayRemoval
from widgets.background_removal import BackgroundRemoval
from widgets.normalization import Normalization
from widgets.linearization import Linearization
from widgets.view import View

class PreprocessingMethods(QFrame):
    method_changed = Signal(QFrame)

    def __init__(self, parent=None):
        super().__init__(parent)

        # name for qss styling
        self.setObjectName("methods")

        self.view = View()
        self.cropping = Cropping()
        self.cosmic_ray_removal = CosmicRayRemoval()
        self.background_removal = BackgroundRemoval()
        self.normalization = Normalization()
        self.linearization = Linearization()

        self.methods = [
            self.view,
            self.cropping,
            self.cosmic_ray_removal,
            self.linearization,
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

        for i in range(self.list.count()):
            self.list.item(i).setIcon(self.methods[i].icon)

        self.methods_layout.setCurrentIndex(0)
        self.list.currentItemChanged.connect(self.emit_method_changed)

        layout = QHBoxLayout()
        layout.addWidget(self.list)
        layout.addLayout(self.methods_layout)
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
    
    # resets to init mode - first method (view)
    def reset(self):
        self.list.setCurrentItem(self.list.item(0))

    def emit_method_changed(self):
        curr_method_index = self.list.currentRow()
        self.methods_layout.setCurrentIndex(curr_method_index)
        self.method_changed.emit(self.methods[curr_method_index])
