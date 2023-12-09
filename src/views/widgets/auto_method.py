from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLineEdit,
    QLabel,
    QWidget,
    QCheckBox,
    QComboBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from typing import Callable, Tuple, Union, Dict, List
from functools import partial

from ..widgets.input_widget_specifier import InputWidgetSpecifier, WidgetType
from ..widgets.directory_selection import DirectorySelection


class AutoMethod(QFrame):
    """
    Parent widget for automatic processing method.
    """

    def __init__(
        self,
        name: str,
        icon: Union[QIcon, str],
        callback: Callable,
        input_widget_specifiers: Dict[str, InputWidgetSpecifier] = {},
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("method_instance")

        self.name = name
        self.input_widget_specifiers = input_widget_specifiers
        self.input_widgets: Dict[str, QWidget] = {}
        self.callback = callback

        if isinstance(icon, QIcon):
            self.icon = icon
        elif isinstance(icon, str):
            self.icon = QIcon(icon)

        self._make_widgets()

        layout = self._make_layout()
        self.setLayout(layout)

    def _make_widgets(self) -> None:
        for widget_name, specifier in self.input_widget_specifiers.items():
            if specifier.widget_type is WidgetType.TEXT:
                widget = QLineEdit(
                    str(specifier.init_value if specifier.init_value else ""),
                    validator=specifier.text_validator,
                    parent=self,
                )
                if specifier.range:
                    widget.editingFinished.connect(
                        partial(self.validate_range, widget_name, specifier.range)
                    )

            elif specifier.widget_type is WidgetType.CHECKBOX:
                widget = QCheckBox(parent=self)
                widget.setChecked(specifier.init_value)

            elif specifier.widget_type is WidgetType.COMBO_BOX:
                widget = QComboBox(parent=self)
                widget.addItems(specifier.choices)

            elif specifier.widget_type is WidgetType.DIRECTORY_SELECTION:
                widget = DirectorySelection(specifier.dir_registry_value, parent=self)

            else:
                raise NotImplementedError()

            self.input_widgets[widget_name] = widget

    def _make_layout(self) -> QGridLayout:
        layout = QGridLayout(parent=self)
        grid_row = 0
        layout.addWidget(QLabel(self.name, parent=self), grid_row, 0)

        if len(self.input_widgets) == 0:
            layout.addWidget(
                QLabel("No parameters to be set.", parent=self), grid_row + 1, 0
            )
        else:
            for widget_label, input_widget in self.input_widgets.items():
                grid_row += 1
                layout.addWidget(QLabel(widget_label, parent=self), grid_row, 0)
                layout.addWidget(input_widget, grid_row, 1)

        layout.setColumnStretch(layout.columnCount(), 1)
        layout.setAlignment(Qt.AlignVCenter)

    def validate_range(self, widget_name: str, range: Tuple) -> None:
        """
        A function to validate range of input, setting it to one of the bounds if it's invalid.
        """

        widget: QLineEdit = self.input_widgets[widget_name]
        output_type: type = self.input_widget_specifiers[widget_name].output_type
        input = output_type(widget.text())

        if input < range[0]:
            widget.setText(str(range[0]))
        elif input > range[1]:
            widget.setText(str(range[1]))

    def get_params(self) -> List:
        """
        A function to return parameters for the callback with the correct types and in the correct order.

        Returns:
            parameters (List): List of callback's parameters.
        """

        parameters = []
        for widget_name, widget in sorted(
            self.input_widgets.items(),
            key=lambda item: self.input_widget_specifiers[item[0]].parameter_order,
        ):
            output_type = self.input_widget_specifiers[widget_name].output_type
            widget_type = self.input_widget_specifiers[widget_name].widget_type

            if widget_type is WidgetType.TEXT:
                parameters.append(output_type(widget.text()))
            elif widget_type is WidgetType.CHECKBOX:
                parameters.append(widget.isChecked())
            elif widget_type is WidgetType.COMBO_BOX:
                parameters.append(widget.currentText())
            elif widget_type is WidgetType.DIRECTORY_SELECTION:
                parameters.append(widget.getCurrentDirectory())
            else:
                raise NotImplementedError()

        return parameters

    def params_to_text(self) -> str:
        """
        A function to return parameters as strings with corresponding names.

        Returns:
            str_parameters (str): String containing parameters and their names.
        """

        parameters = self.get_params()
        parameter_names = [
            name
            for name, _ in sorted(
                self.input_widgets.items(),
                key=lambda item: self.input_widget_specifiers[item[0]].parameter_order,
            )
        ]

        str_parameters = ", ".join(
            f"{name.lower().replace(' ', '_')}: {value}"
            for name, value in zip(parameter_names, parameters)
        )
        return str_parameters
