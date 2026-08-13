from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
)


class CadDimensionEditorDialog(QDialog):
    """Small modal dialog for editing a CAD dimension value."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.label_id = None
        self.source_key = None
        self.side = None
        self.current_value = None
        self.unit = ""
        self.min_value = 0.0
        self.max_value = 1_000_000.0
        self.decimals = 3
        self.display_text = ""

        self.setModal(True)
        self.setWindowTitle("Edit Dimension")

        self.main_layout = QVBoxLayout(self)

        self.dimension_label = QLabel()
        self.main_layout.addWidget(self.dimension_label)

        self.value_spinbox = QDoubleSpinBox()
        self.value_spinbox.setRange(
            self.min_value,
            self.max_value,
        )
        self.value_spinbox.setDecimals(self.decimals)
        self.main_layout.addWidget(self.value_spinbox)

        self.button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("OK")

        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)

        self.main_layout.addLayout(self.button_layout)

        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.accept)

    def set_context(self, payload):
        """Load dimension metadata from a CAD edit request."""

        payload = payload or {}

        self.label_id = payload.get("label_id")
        self.source_key = payload.get("source_key")
        self.side = payload.get("side")
        self.current_value = payload.get("value")
        self.unit = payload.get("unit", "")
        self.display_text = payload.get(
            "display_text",
            payload.get("label_text", ""),
        )

        label_text = self.display_text or self.label_id or "Dimension"

        if self.unit:
            label_text = f"{label_text} ({self.unit})"

        self.dimension_label.setText(label_text)

        if self.current_value is not None:
            try:
                self.value_spinbox.setValue(float(self.current_value))
            except (TypeError, ValueError):
                self.value_spinbox.setValue(0.0)

    def set_limits(self, minimum, maximum, decimals):
        """Set the allowed numeric range and precision."""

        self.min_value = float(minimum)
        self.max_value = float(maximum)
        self.decimals = int(decimals)

        self.value_spinbox.setRange(
            self.min_value,
            self.max_value,
        )
        self.value_spinbox.setDecimals(self.decimals)

    def value(self):
        """Return the edited numeric value."""

        return self.value_spinbox.value()

    def accept(self):
        """Accept the dialog with the current value."""

        self.current_value = self.value()
        super().accept()