from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
)
from PySide6.QtCore import Qt


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
        self.setMinimumSize(420, 220)
        self.resize(480, 250)

        # Explicit styling is important because the main OsdagBridge
        # stylesheet can otherwise affect the dialog's text visibility.
        self.setStyleSheet(
            """
            QDialog {
                background-color: #ffffff;
                color: #000000;
            }

            QLabel {
                color: #000000;
                background-color: #ffffff;
                font-size: 14px;
                padding: 4px;
            }

            QDoubleSpinBox {
                color: #000000;
                background-color: #ffffff;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 6px;
                min-height: 32px;
                font-size: 14px;
            }

            QDoubleSpinBox:focus {
                border: 2px solid #90AF13;
            }

            QPushButton {
                color: #000000;
                background-color: #ffffff;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 7px 20px;
                min-height: 30px;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton:pressed {
                background-color: #dddddd;
            }
            """
        )

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # ---------------------------------------------------------
        # Dimension label
        # ---------------------------------------------------------

        self.dimension_label = QLabel("Dimension")
        self.dimension_label.setWordWrap(True)
        self.dimension_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.dimension_label.setMinimumHeight(35)

        self.main_layout.addWidget(self.dimension_label)

        # ---------------------------------------------------------
        # Value editor
        # ---------------------------------------------------------

        self.value_spinbox = QDoubleSpinBox()

        self.value_spinbox.setRange(
            self.min_value,
            self.max_value,
        )

        self.value_spinbox.setDecimals(
            self.decimals
        )

        # Prevent the value from changing while the user is typing.
        self.value_spinbox.setKeyboardTracking(False)

        self.value_spinbox.setMinimumHeight(40)

        self.main_layout.addWidget(
            self.value_spinbox
        )

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)

        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("OK")

        self.cancel_button.setMinimumWidth(110)
        self.ok_button.setMinimumWidth(110)

        self.button_layout.addStretch()
        self.button_layout.addWidget(
            self.cancel_button
        )
        self.button_layout.addWidget(
            self.ok_button
        )

        self.main_layout.addLayout(
            self.button_layout
        )

        # ---------------------------------------------------------
        # Signals
        # ---------------------------------------------------------

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.ok_button.clicked.connect(
            self.accept
        )

        self.value_spinbox.editingFinished.connect(
            self._on_editing_finished
        )

    # =============================================================
    # Editing
    # =============================================================

    def _on_editing_finished(self):
        """Keep the current value synchronized after manual editing."""

        try:
            self.current_value = (
                self.value_spinbox.value()
            )
        except Exception:
            pass

    # =============================================================
    # Context
    # =============================================================

    def set_context(self, payload):
        """Load dimension metadata from a CAD edit request."""

        payload = payload or {}

        self.label_id = payload.get(
            "label_id"
        )

        self.source_key = payload.get(
            "source_key"
        )

        self.side = payload.get(
            "side"
        )

        self.current_value = payload.get(
            "value"
        )

        self.unit = payload.get(
            "unit",
            ""
        )

        self.display_text = payload.get(
            "display_text",
            payload.get(
                "label_text",
                ""
            ),
        )

        # Prefer the human-readable CAD text.
        label_text = (
            self.display_text
            or self.label_id
            or self.source_key
            or "Dimension"
        )

        if self.unit:
            label_text = (
                f"{label_text} ({self.unit})"
            )

        self.dimension_label.setText(
            str(label_text)
        )

        # ---------------------------------------------------------
        # Set current value
        # ---------------------------------------------------------

        if self.current_value is not None:
            try:
                value = float(
                    self.current_value
                )

                value = max(
                    self.min_value,
                    min(
                        value,
                        self.max_value
                    ),
                )

                self.value_spinbox.setValue(
                    value
                )

            except (
                TypeError,
                ValueError
            ):
                self.value_spinbox.setValue(
                    self.min_value
                )

        else:
            self.value_spinbox.setValue(
                self.min_value
            )

    # =============================================================
    # Limits
    # =============================================================

    def set_limits(
        self,
        minimum,
        maximum,
        decimals
    ):
        """Set the allowed numeric range and precision."""

        self.min_value = float(
            minimum
        )

        self.max_value = float(
            maximum
        )

        self.decimals = int(
            decimals
        )

        if self.min_value > self.max_value:
            (
                self.min_value,
                self.max_value,
            ) = (
                self.max_value,
                self.min_value,
            )

        self.value_spinbox.setRange(
            self.min_value,
            self.max_value,
        )

        self.value_spinbox.setDecimals(
            self.decimals
        )

        # Clamp current value to the new range.
        current = (
            self.value_spinbox.value()
        )

        current = max(
            self.min_value,
            min(
                current,
                self.max_value
            ),
        )

        self.value_spinbox.setValue(
            current
        )

    # =============================================================
    # Value
    # =============================================================

    def value(self):
        """Return the edited numeric value."""

        return self.value_spinbox.value()

    # =============================================================
    # Accept
    # =============================================================

    def accept(self):
        """Accept the dialog with the current value."""

        self.current_value = (
            self.value()
        )

        super().accept()