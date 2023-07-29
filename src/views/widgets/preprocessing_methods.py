from PySide6.QtWidgets import QFrame, QStackedLayout, QHBoxLayout, QListWidget, QWidget
from PySide6.QtCore import Signal

from widgets.cropping import Cropping
from widgets.cosmic_ray_removal import CosmicRayRemoval
from widgets.background_removal import BackgroundRemoval
from widgets.normalization import Normalization
from widgets.linearization import Linearization
from widgets.view import View


class PreprocessingMethods(QFrame):
    """
    A widget for method selection for 'manual' spectra preprocessing.
    """

    method_changed = Signal(QFrame)

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual preprocessing methods selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        # name for qss styling
        self.setObjectName("methods")

        # individual methods instances
        self.view = View(self)
        self.cropping = Cropping(self)
        self.cosmic_ray_removal = CosmicRayRemoval(self)
        self.background_removal = BackgroundRemoval(self)
        # self.normalization = Normalization(self) # TODO: Add in version 1.2
        self.linearization = Linearization(self)

        self.methods = [
            self.view,
            self.cosmic_ray_removal,
            self.cropping,
            self.linearization,
            # self.normalization, # TODO: Add in version 1.2
            self.background_removal,
        ]

        self.list = QListWidget(self)

        self.list.setObjectName("methods_list")
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
        layout.setSpacing(0)
        self.setLayout(layout)
    
    def reset(self) -> None:
        """
        A function to reset the widgets to init state.
        """

        # init method is the first one
        self.list.setCurrentItem(self.list.item(0))

    def emit_method_changed(self) -> None:
        """
        A function to emit that current method has changed so that corresponding
        params selection is displayed.
        """

        curr_method_index = self.list.currentRow()
        self.methods_layout.setCurrentIndex(curr_method_index)
        self.method_changed.emit(self.methods[curr_method_index])
