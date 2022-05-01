from PySide6.QtWidgets import QFrame, QListWidget, QStackedLayout, QHBoxLayout
from PySide6.QtCore import Signal
from widgets.auto_processing import AutoProcessing

from widgets.manual_preprocessing import ManualPreprocessing
from widgets.spectra_decomposition import SpectraDecomposition
from widgets.settings import Settings

# OK
class Menu(QFrame):
    menu_item_changed = Signal(QFrame)

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO: menu styling

        self.manual_preprocessing = ManualPreprocessing()
        self.spectra_decomposition = SpectraDecomposition()
        self.settings_widget = Settings()
        self.auto_processing = AutoProcessing()


        self.menu_items = [
            self.manual_preprocessing,
            self.spectra_decomposition,
            self.settings_widget,
            self.auto_processing
        ]

        self.list = QListWidget()
        self.list.setObjectName("menu")

        self.list.addItems([menu_item.get_string_name() for menu_item in self.menu_items])
        
        self.list.setCurrentItem(self.list.item(0))
        # do not sort list items (methods) as they are in specific ored
        self.list.setSortingEnabled(False) 
        self.list.setMinimumWidth(210)

        self.main_layout = QStackedLayout()

        for menu_item in self.menu_items:
            self.main_layout.addWidget(menu_item)

        for i in range(self.list.count()):
            self.list.item(i).setIcon(self.menu_items[i].icon)

        self.main_layout.setCurrentIndex(0)
        self.list.currentItemChanged.connect(self.emit_menu_item_changed)

        layout = QHBoxLayout()
        layout.addWidget(self.list)
        layout.addLayout(self.main_layout)
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
    
    # resets to init mode - first method (view)
    def reset(self):
        self.list.setCurrentItem(self.list.item(0))

    def emit_menu_item_changed(self):
        curr_item_index = self.list.currentRow()
        self.main_layout.setCurrentIndex(curr_item_index)
        self.spectra_decomposition.update_file_list()
        self.menu_item_changed.emit(self.menu_items[curr_item_index])
