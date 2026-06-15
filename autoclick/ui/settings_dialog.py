from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QDoubleSpinBox, QPushButton, QSpinBox, QWidget,
)
from PySide6.QtCore import Qt
from ..config import Config


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self.setWindowTitle("Configurações")
        self.setFixedSize(420, 380)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Configurações")
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        self._tray_cb = QCheckBox("Minimizar para a bandeja")
        self._tray_cb.setChecked(self._config.get("minimize_to_tray", True))
        layout.addWidget(self._tray_cb)

        self._start_min_cb = QCheckBox("Iniciar minimizado")
        self._start_min_cb.setChecked(self._config.get("start_minimized", False))
        layout.addWidget(self._start_min_cb)

        self._restore_cb = QCheckBox("Restaurar última macro")
        self._restore_cb.setChecked(self._config.get("restore_last_macro", False))
        layout.addWidget(self._restore_cb)

        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Atraso antes da reprodução (s):"))
        self._delay_spin = QDoubleSpinBox()
        self._delay_spin.setRange(0.0, 30.0)
        self._delay_spin.setSingleStep(0.1)
        self._delay_spin.setValue(self._config.get("playback_delay", 0.5))
        delay_layout.addWidget(self._delay_spin)
        delay_layout.addStretch()
        layout.addLayout(delay_layout)

        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Tolerância de movimento (px):"))
        self._threshold_spin = QSpinBox()
        self._threshold_spin.setRange(0, 100)
        self._threshold_spin.setValue(self._config.get("mouse_move_threshold", 5))
        threshold_layout.addWidget(self._threshold_spin)
        threshold_layout.addStretch()
        layout.addWidget(QLabel("Ignorar movimentos menores que:"))
        layout.addLayout(threshold_layout)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("Salvar")
        save_btn.setObjectName("accentButton")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("flatButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _save(self):
        self._config.set("minimize_to_tray", self._tray_cb.isChecked())
        self._config.set("start_minimized", self._start_min_cb.isChecked())
        self._config.set("restore_last_macro", self._restore_cb.isChecked())
        self._config.set("playback_delay", self._delay_spin.value())
        self._config.set("mouse_move_threshold", self._threshold_spin.value())
        self.accept()
