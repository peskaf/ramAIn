from PySide6.QtWidgets import QFrame, QWidget
from PySide6.QtGui import QIcon


class View(QFrame):
    """
    A widget for viewing method for the manual preprocessing part of the app.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for viewing widget for manual preprocessing.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.setObjectName("method_instance")
        self.icon = QIcon("src/resources/icons/view.svg")

    def reset(self) -> None:
        """
        A function to reset all widget to init state.
        NOTE: This function does nothing on purpose as there are no widgets here.
        """

        pass

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "View"
