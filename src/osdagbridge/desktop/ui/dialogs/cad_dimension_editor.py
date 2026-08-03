"""Reusable modal dialog for editing a single CAD dimension value."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class CadDimensionEditorDialog(QDialog):
    """Lightweight modal dialog for editing a single dimension value."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Dimension")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumWidth(320)

        self.label_id = None
        self.source_key = None
        self.side = None
        self.current_value = 0.0
        self.unit = ""
        self.display_text = ""

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)

        self.dimension_name_label = QLabel("")
        self.dimension_name_label.setWordWrap(True)
        self.dimension_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.unit_label = QLabel("")
        self.unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.value_spinbox = QDoubleSpinBox()
        self.value_spinbox.setDecimals(3)
        self.value_spinbox.setRange(-1_000_000_000.0, 1_000_000_000.0)
        self.value_spinbox.setSingleStep(0.1)

        form_layout.addRow("Dimension:", self.dimension_name_label)
        form_layout.addRow("Unit:", self.unit_label)
        form_layout.addRow("Value:", self.value_spinbox)
        root_layout.addLayout(form_layout)

        button_row = QHBoxLayout()
        button_row.addStretch(1)

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_row.addWidget(self.ok_button)
        button_row.addWidget(self.cancel_button)
        root_layout.addLayout(button_row)

    def set_context(self, payload):
        """Populate the dialog from a dimension payload."""
        payload = payload or {}

        self.label_id = payload.get("label_id")
        self.source_key = payload.get("source_key")
        self.side = payload.get("side")
        self.current_value = payload.get("value", payload.get("current_value", 0.0))
        self.unit = payload.get("unit", "")
        self.display_text = payload.get("display_text", payload.get("label_text", self.label_id or ""))

        self.dimension_name_label.setText(self.display_text)
        self.unit_label.setText(self.unit)

        if self.current_value is None:
            self.current_value = 0.0
        self.value_spinbox.setValue(float(self.current_value))

    def set_limits(self, minimum, maximum, decimals):
        """Configure numeric limits and precision for the editor."""
        self.value_spinbox.setRange(float(minimum), float(maximum))
        self.value_spinbox.setDecimals(int(decimals))

    def value(self):
        """Return the edited numeric value."""
        return self.value_spinbox.value()