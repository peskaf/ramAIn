from types import NoneType
from PySide6.QtWidgets import QFrame, QListWidget, QStackedLayout, QHBoxLayout, QWidget
from PySide6.QtCore import Signal

from widgets.auto_processing import AutoProcessing
from widgets.manual_preprocessing import ManualPreprocessing
from widgets.spectra_decomposition import SpectraDecomposition
from widgets.settings import Settings


class Menu(QFrame):
    """
    A widget representing main menu of the application.
    """

    menu_item_changed = Signal(QFrame)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        # methods instances
        self.manual_preprocessing = ManualPreprocessing(self)
        self.spectra_decomposition = SpectraDecomposition(self)
        self.auto_processing = AutoProcessing(self)
        self.settings_widget = Settings(self)
        

        self.menu_items = [
            self.manual_preprocessing,
            self.spectra_decomposition,
            self.auto_processing,
            self.settings_widget,
            
        ]

        self.list = QListWidget(self)

        # name for qss styling
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
        layout.setSpacing(0)
        self.setLayout(layout)
    
    def reset(self) -> None:
        """
        A function to reset the widgets to init state.
        """

        # first method is the init one
        self.list.setCurrentItem(self.list.item(0))

    def emit_menu_item_changed(self) -> None:
        """
        A function to emit that current intem in the list has changed so that the method is changed.
        """

        curr_item_index = self.list.currentRow()
        self.main_layout.setCurrentIndex(curr_item_index)
        self.spectra_decomposition.update_file_list()
        self.manual_preprocessing.update_file_list()
        self.menu_item_changed.emit(self.menu_items[curr_item_index])
