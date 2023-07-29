from PySide6.QtWidgets import QFrame, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal

# NOTE: widget currently not used, will be used in the future

class Normalization(QFrame):
    """
    A widget for parameters selection for the normalization method.
    """

    apply_clicked = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for manual normalization parameters selection widget.
  
        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("icons/normalize.svg")
        ...

    def reset(self) -> None:
        """
        A function to reset all widgets to init state.
        """
        ...

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Normalization"
