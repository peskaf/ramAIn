from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QListWidget, QStackedLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from widgets.manual_preprocessing import ManualPreprocessing
from widgets.spectra_decomposition import SpectraDecomposition

# OK
class Menu(QFrame):
    menu_item_changed = Signal(QFrame)

    def __init__(self, parent=None):
        super().__init__(parent)

        # set name for qss styling
        # self.setObjectName("menu")
        # TODO: menu styling
        """
        # TODO: add relevant icons to the menu items
        icon = QIcon("icons/icon.svg")
        buttons = [
            QPushButton("   Manual Preprocessing", icon=icon), # spaces because of spacing between icon and text
            QPushButton("   Spectra Decomposition", icon=icon),
            QPushButton("   Automatic Processing", icon=icon),
            QPushButton("   Settings", icon=QIcon("icons/settings.svg")),
            QPushButton("   Raman", icon=icon)
        ]

        layout = QVBoxLayout()

        for button in buttons:
            # self.setObjectName("nazev") # pripadne pak pro routing tlacitek
            button.setCursor(QCursor(Qt.PointingHandCursor))
            layout.addWidget(button)

        # buttons should be aligned to the top of the layout
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

        """
        self.manual_preprocessing = ManualPreprocessing()
        self.spectra_decomposition = SpectraDecomposition()


        self.menu_items = [
            self.manual_preprocessing,
            self.spectra_decomposition,
        ]

        self.list = QListWidget()
        self.list.setObjectName("menu")

        self.list.addItems([menu_item.get_string_name() for menu_item in self.menu_items])
        
        self.list.setCurrentItem(self.list.item(0))
        # do not sort list items (methods) as they are in specific ored
        self.list.setSortingEnabled(False) 

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
        self.menu_item_changed.emit(self.menu_items[curr_item_index])
