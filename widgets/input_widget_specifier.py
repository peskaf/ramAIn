from PySide6.QtGui import QRegularExpressionValidator
from typing import Tuple, List, Union
from enum import Enum


class WidgetType(Enum):
    TEXT = 0
    COMBO_BOX = 1
    CHECKBOX = 2
    DIRECTORY_SELECTION = 3


class InputWidgetSpecifier():

    NUMERICAL_TYPES: Tuple = (float, int)

    def __init__(self,
        widget_type: WidgetType,
        output_type: type,
        init_value = None,
        range: Union[Tuple, None] = None,
        text_validator: Union[QRegularExpressionValidator, None] = None,
        choices: Union[List, None] = None,
        dir_registry_value: Union[str, None] = None,
        ) -> None:

        # TODO: make better errors types
        if output_type not in self.NUMERICAL_TYPES and range is not None:
            raise RuntimeError(f"Invalid InputWidgetSpecifier - range is set but output type is of type {output_type}.")
        
        # TODO: check both range values for output type

        if init_value is not None and not isinstance(init_value, output_type):
            if isinstance(init_value, int) and output_type is float:
                pass
            else:
                raise RuntimeError(f"Invalid InputWidgetSpecifier - init value is of type {type(init_value)} but output type is {output_type}.")

        if widget_type is not WidgetType.COMBO_BOX and choices:
            raise RuntimeError(f"Invalid InputWidgetSpecifier - choices specified for not-combo-box widget type.")
        
        if widget_type is WidgetType.COMBO_BOX and not choices:
            raise RuntimeError(f"Invalid InputWidgetSpecifier - choices not specified for combo-box widget type.")

        if widget_type is WidgetType.COMBO_BOX and init_value:
            if init_value not in choices:
                raise RuntimeError(f"Invalid InputWidgetSpecifier - init value not in choices for choice-type widget.")
            else:
                init_item_index = choices.index(init_value)
                choices[init_item_index], choices[0] = choices[0], choices[init_item_index]

        if widget_type is not WidgetType.TEXT and text_validator:
            raise RuntimeError(f"Invalid InputWidgetSpecifier - choices specified for non-combo-box widget type.")

        if widget_type is not WidgetType.DIRECTORY_SELECTION and dir_registry_value:
            raise RuntimeError(f"Invalid InputWidgetSpecifier - dir registry value specified for non-dir-selection widget type.")

        self.widget_type = widget_type
        self.init_value = init_value
        self.output_type = output_type
        self.choices = choices
        self.range = range
        self.text_validator = text_validator
        self.dir_registry_value = dir_registry_value
