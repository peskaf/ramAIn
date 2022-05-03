from PySide6.QtGui import QRegularExpressionValidator

INT_VALIDATOR = QRegularExpressionValidator("-?[0-9]+")
POSITIVE_INT_VALIDATOR = QRegularExpressionValidator("[0-9]+")
REAL_VALIDATOR = QRegularExpressionValidator("-?[0-9]+(\.[0-9]+)?")
POSITIVE_REAL_VALIDATOR = QRegularExpressionValidator("[0-9]+(\.[0-9]+)?")