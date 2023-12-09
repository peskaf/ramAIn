from PySide6.QtWidgets import (
    QFrame,
    QStackedLayout,
    QHBoxLayout,
    QListWidget,
    QSizePolicy,
    QWidget,
)
from PySide6.QtCore import Signal

from ..widgets.PCA import PCA
from ..widgets.NMF import NMF


class DecompositionMethods(QFrame):
    """
    A widget for method selection for 'manual' spectra decomposition.
    """

    method_changed = Signal(QFrame)

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for decomposition methods selection widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        # name for qss styling
        self.setObjectName("methods")

        self.PCA = PCA(self)
        self.NMF = NMF(self)

        self.methods = [
            self.NMF,
            self.PCA,
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

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setMaximumSize(5000, 100)

    def reset(self) -> None:
        """
        The function to reset all widgets to init state.
        """

        self.list.setCurrentItem(self.list.item(0))

    def emit_method_changed(self):
        curr_method_index = self.list.currentRow()
        self.methods_layout.setCurrentIndex(curr_method_index)
        self.method_changed.emit(self.methods[curr_method_index])
