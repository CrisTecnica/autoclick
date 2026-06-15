import os
import time
from datetime import timedelta

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFrame, QFileDialog,
    QMessageBox, QSystemTrayIcon, QMenu, QDialog,
    QSpinBox, QDoubleSpinBox, QLineEdit,
)
from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont

from ..capture import Capture
from ..playback import PlaybackThread
from ..hotkeys import HotkeyManager
from ..persistence import MacroPersistence
from ..config import Config
from ..models import Macro, MacroEvent, EventType
from .settings_dialog import SettingsDialog
from .editor_dialog import EditorDialog


STYLESHEET = """
QMainWindow, QDialog {
    background-color: #1e1e1e;
    color: #e0e0e0;
}
QLabel {
    color: #e0e0e0;
    font-size: 13px;
}
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #555;
}
QPushButton:pressed {
    background-color: #1a1a1a;
}
QPushButton#recordButton {
    background-color: #4a1515;
    border: 1px solid #8b2020;
}
QPushButton#recordButton:hover {
    background-color: #6b1f1f;
}
QPushButton#recordButton:checked {
    background-color: #8b2020;
    border: 1px solid #cc3333;
}
QPushButton#playButton {
    background-color: #154a2a;
    border: 1px solid #208b3a;
}
QPushButton#playButton:hover {
    background-color: #1f6b3a;
}
QPushButton#repeatButton {
    background-color: #1a2a4a;
    border: 1px solid #2a5a8b;
}
QPushButton#repeatButton:hover {
    background-color: #2a3a6b;
}
QPushButton#stopButton {
    background-color: #6b2020;
    border: 1px solid #cc3333;
    color: #ff6666;
}
QPushButton#accentButton {
    background-color: #3a6bff;
    border: 1px solid #5a8bff;
    color: white;
}
QPushButton#accentButton:hover {
    background-color: #4a7bff;
}
QPushButton#flatButton {
    background-color: transparent;
    border: 1px solid #3d3d3d;
}
QPushButton#flatButton:hover {
    background-color: #2d2d2d;
}
QPushButton#hotkeyButton {
    background-color: #252525;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 11px;
}
QPushButton#hotkeyButton:hover {
    background-color: #353535;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #3d3d3d;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #5a8bff;
    border: none;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover {
    background: #7aabff;
}
QSlider::sub-page:horizontal {
    background: #5a8bff;
    border-radius: 3px;
}
QFrame#statusBar {
    background-color: #252525;
    border-radius: 8px;
    padding: 8px;
}
QFrame#shortcutBar {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    padding: 8px;
}
QTableWidget {
    background-color: #252525;
    color: #e0e0e0;
    gridline-color: #3d3d3d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
}
QTableWidget::item:selected {
    background-color: #3a6bff;
    color: white;
}
QHeaderView::section {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    padding: 6px;
}
QGroupBox {
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 10px;
    font-size: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    padding: 2px 8px;
}
QCheckBox {
    color: #e0e0e0;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #555;
    background: #2d2d2d;
}
QCheckBox::indicator:checked {
    background: #3a6bff;
    border: 1px solid #5a8bff;
}
QDoubleSpinBox, QSpinBox, QLineEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px;
    font-size: 13px;
}
"""


BUTTON_KEYS = [
    ("record", "F9", "Gravar"),
    ("stop_record", "F10", "Parar Gravação"),
    ("play", "F11", "Reproduzir"),
    ("stop_all", "F12", "Tudo Parar"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoClick — Gravador de Macro")
        self.setMinimumSize(600, 520)
        self.resize(680, 560)

        self._config = Config()
        self._capture = Capture(self._config.get("mouse_move_threshold", 5))
        self._persistence = MacroPersistence()
        self._hotkeys = HotkeyManager(self)
        self._playback = None
        self._current_macro = Macro()
        self._current_file = ""
        self._recording = False
        self._playing = False
        self._looping = False
        self._repeat_count = 1
        self._repeat_delay = 0.0
        self._repeat_remaining = 0
        self._recording_timer = QElapsedTimer()
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status)

        self._setup_ui()
        self._connect_signals()
        self._app_icon = self._create_icon()
        self.setWindowIcon(self._app_icon)

        self._capture.on_event = self._on_capture_event
        self._capture.on_status_change = self._on_capture_status

        self._hotkeys.start()

        self._init_tray()

        if self._config.get("restore_last_macro", False):
            last = self._config.get("last_macro_file", "")
            if last and os.path.exists(last):
                self._load_macro_file(last)

        self.setStyleSheet(STYLESHEET)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("AutoClick — Gravador de Macro")
        title.setObjectName("appTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        platform_label = QLabel("Pop!_OS / Linux")
        platform_label.setStyleSheet("""
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 12px;
            padding: 4px 14px;
            font-size: 11px;
            color: #aaa;
        """)
        header.addWidget(platform_label)
        layout.addLayout(header)

        btn_frame = QFrame()
        btn_frame.setObjectName("actionFrame")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(16)

        self._record_btn = QPushButton("🔴  Gravar")
        self._record_btn.setObjectName("recordButton")
        self._record_btn.setCheckable(True)
        self._record_btn.setMinimumHeight(80)
        self._record_btn.setMinimumWidth(160)
        self._record_btn.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: 600; border-radius: 12px; }
        """)
        btn_layout.addWidget(self._record_btn)

        self._play_btn = QPushButton("▶️  Reproduzir")
        self._play_btn.setObjectName("playButton")
        self._play_btn.setMinimumHeight(80)
        self._play_btn.setMinimumWidth(160)
        self._play_btn.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: 600; border-radius: 12px; }
        """)
        btn_layout.addWidget(self._play_btn)

        self._repeat_btn = QPushButton("🔄  Loop")
        self._repeat_btn.setObjectName("repeatButton")
        self._repeat_btn.setCheckable(True)
        self._repeat_btn.setMinimumHeight(80)
        self._repeat_btn.setMinimumWidth(160)
        self._repeat_btn.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: 600; border-radius: 12px; }
            QPushButton:checked {
                background-color: #2a5a8b;
                border: 2px solid #4a8bff;
                color: white;
            }
        """)
        btn_layout.addWidget(self._repeat_btn)

        layout.addWidget(btn_frame)

        speed_layout = QVBoxLayout()
        speed_layout.setSpacing(4)

        speed_header = QHBoxLayout()
        speed_label = QLabel("Velocidade de reprodução")
        speed_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        speed_header.addWidget(speed_label)
        speed_header.addStretch()
        self._speed_value_label = QLabel("1,0x")
        self._speed_value_label.setStyleSheet("""
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            padding: 2px 10px;
            font-size: 14px;
            font-weight: 600;
            color: #5a8bff;
        """)
        speed_header.addWidget(self._speed_value_label)
        speed_layout.addLayout(speed_header)

        slider_row = QHBoxLayout()
        min_label = QLabel("0,1x")
        min_label.setStyleSheet("color: #888; font-size: 11px;")
        slider_row.addWidget(min_label)
        self._speed_slider = QSlider(Qt.Horizontal)
        self._speed_slider.setRange(1, 100)
        self._speed_slider.setValue(10)
        self._speed_slider.setTickPosition(QSlider.NoTicks)
        slider_row.addWidget(self._speed_slider)
        max_label = QLabel("10x")
        max_label.setStyleSheet("color: #888; font-size: 11px;")
        slider_row.addWidget(max_label)
        speed_layout.addLayout(slider_row)
        layout.addLayout(speed_layout)

        self._status_frame = QFrame()
        self._status_frame.setObjectName("statusBar")
        status_layout = QHBoxLayout(self._status_frame)
        status_layout.setContentsMargins(12, 8, 12, 8)

        self._status_label = QLabel("✅ Pronto")
        status_layout.addWidget(self._status_label)
        status_layout.addStretch()

        self._events_label = QLabel("Eventos: 0")
        self._events_label.setStyleSheet("color: #aaa; font-size: 12px;")
        status_layout.addWidget(self._events_label)

        self._timer_label = QLabel("⏱ 00:00")
        self._timer_label.setStyleSheet("color: #aaa; font-size: 12px;")
        status_layout.addWidget(self._timer_label)

        layout.addWidget(self._status_frame)

        layout.addStretch()

        shortcuts_frame = QFrame()
        shortcuts_frame.setObjectName("shortcutBar")
        sc_layout = QHBoxLayout(shortcuts_frame)
        sc_layout.setContentsMargins(8, 6, 8, 6)
        sc_layout.setSpacing(4)

        self._shortcut_buttons = []
        for action_name, key, label in BUTTON_KEYS:
            btn = QPushButton(f"{key}  →  {label}")
            btn.setObjectName("hotkeyButton")
            self._shortcut_buttons.append(btn)
            sc_layout.addWidget(btn)
        sc_layout.addStretch()

        self._emergency_btn = QPushButton("🛑  Esc → Emergência")
        self._emergency_btn.setObjectName("hotkeyButton")
        self._emergency_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a1515;
                border: 1px solid #8b2020;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                color: #ff8888;
            }
            QPushButton:hover {
                background-color: #6b1f1f;
            }
        """)
        sc_layout.addWidget(self._emergency_btn)

        layout.addWidget(shortcuts_frame)

        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar { background: #1e1e1e; color: #e0e0e0; border: none; }
            QMenuBar::item:selected { background: #3d3d3d; }
            QMenu { background: #2d2d2d; color: #e0e0e0; border: 1px solid #3d3d3d; }
            QMenu::item:selected { background: #3a6bff; }
        """)

        file_menu = menu_bar.addMenu("Arquivo")
        file_menu.addAction("Nova Macro", self._new_macro)
        file_menu.addAction("Abrir Macro...", self._open_macro)
        file_menu.addAction("Salvar", self._save_macro)
        file_menu.addAction("Salvar Como...", self._save_macro_as)
        file_menu.addSeparator()
        file_menu.addAction("Sair", self.close)

        edit_menu = menu_bar.addMenu("Editar")
        edit_menu.addAction("Editor de Eventos...", self._open_editor)

        tools_menu = menu_bar.addMenu("Ferramentas")
        tools_menu.addAction("Configurações...", self._open_settings)

        tools_menu.addSeparator()
        self._all_keys_action = tools_menu.addAction("Ativar Teclas em Todos os Eventos")
        self._all_keys_action.setCheckable(True)
        self._all_keys_action.setChecked(False)

    def _connect_signals(self):
        self._record_btn.clicked.connect(self._toggle_record)

        self._play_btn.clicked.connect(self._start_playback)
        self._repeat_btn.clicked.connect(self._toggle_repeat)

        self._speed_slider.valueChanged.connect(self._on_speed_change)

        self._hotkeys.hotkey_triggered.connect(self._on_hotkey)

    def _create_icon(self):
        pix = QPixmap(64, 64)
        pix.fill(Qt.transparent)
        with QPainter(pix) as p:
            p.setRenderHint(QPainter.Antialiasing)
            p.setBrush(QColor("#3a6bff"))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(4, 4, 56, 56, 12, 12)
            p.setPen(QColor("white"))
            p.setFont(QFont("monospace", 28, QFont.Bold))
            p.drawText(pix.rect(), Qt.AlignCenter, "AC")
        return QIcon(pix)

    def _init_tray(self):
        if not self._config.get("minimize_to_tray", True):
            return
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(self._app_icon)
        self._tray_icon.setToolTip("AutoClick")
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Mostrar")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Sair")
        quit_action.triggered.connect(self.close)
        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._tray_activated)
        self._tray_icon.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()

    def closeEvent(self, event):
        if self._config.get("minimize_to_tray", True) and self._tray_icon.isVisible():
            event.ignore()
            self.hide()
            self._tray_icon.showMessage(
                "AutoClick",
                "O aplicativo continua rodando na bandeja.",
                QSystemTrayIcon.Information,
                2000,
            )
            return
        self._stop_everything()
        self._hotkeys.stop()
        if self._current_file:
            self._config.set("last_macro_file", self._current_file)
        event.accept()

    def _on_speed_change(self, value):
        speed = value / 10.0
        self._speed_value_label.setText(f"{speed:.1f}x".replace(".", ","))
        if self._playback and self._playback.isRunning():
            self._playback.set_speed(speed)

    def _speed(self):
        return self._speed_slider.value() / 10.0

    def _toggle_record(self):
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if self._playing:
            self._stop_playback()
        self._current_macro = Macro()
        self._current_macro.name = "Macro sem título"
        self._capture.set_threshold(self._config.get("mouse_move_threshold", 5))
        self._capture.start()
        self._recording = True
        self._recording_timer.start()

        self._record_btn.setChecked(True)
        self._record_btn.setText("🔴  Parar Gravação")
        self._record_btn.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: 600; border-radius: 12px;
                background-color: #8b2020; border: 2px solid #cc3333; color: white; }
            QPushButton:hover { background-color: #aa3030; }
        """)
        self._play_btn.setEnabled(False)
        self._repeat_btn.setEnabled(False)
        self._status_label.setText("🔴 Gravando...")
        self._status_label.setStyleSheet("color: #ff5555; font-weight: 600;")
        self._events_label.setText("Eventos: 0")
        self._timer_label.setText("⏱ 00:00")

        self._status_timer.start(200)

    def _stop_recording(self):
        self._capture.stop()
        self._recording = False
        self._status_timer.stop()

        self._current_macro.events = list(self._capture.events)
        self._current_macro.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        if not self._current_macro.events:
            self._current_macro.name = "Macro vazia"

        self._record_btn.setChecked(False)
        self._record_btn.setText("🔴  Gravar")
        self._record_btn.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: 600; border-radius: 12px; }
        """)
        self._play_btn.setEnabled(True)
        self._repeat_btn.setEnabled(True)
        self._status_label.setText("✅ Gravação concluída")
        self._status_label.setStyleSheet("color: #5a8bff; font-weight: 600;")

        num = len(self._current_macro.events)
        self._events_label.setText(f"Eventos: {num}")

        if num > 0:
            self._open_editor()

    def _on_capture_event(self, event):
        pass

    def _on_capture_status(self, msg):
        pass

    def _update_status(self):
        if self._recording:
            elapsed = self._recording_timer.elapsed()
            secs = elapsed // 1000
            time_str = f"{secs // 60:02d}:{secs % 60:02d}"
            self._timer_label.setText(f"⏱ {time_str}")
            num = len(self._capture.events)
            self._events_label.setText(f"Eventos: {num}")

    def _start_playback(self):
        if not self._current_macro.events:
            QMessageBox.warning(self, "Aviso", "Nenhum evento gravado para reproduzir.")
            return
        if self._recording:
            self._stop_recording()
        self._do_playback(repeat=1, delay=0)

    def _toggle_repeat(self):
        if self._recording:
            self._stop_recording()
        if self._looping:
            self._looping = False
            self._repeat_btn.setChecked(False)
            self._stop_playback()
        else:
            if not self._current_macro.events:
                QMessageBox.warning(self, "Aviso", "Nenhum evento gravado para repetir.")
                self._repeat_btn.setChecked(False)
                return
            self._looping = True
            self._do_playback(repeat=999999, delay=0.5)

    def _do_playback(self, repeat=1, delay=0.0):
        if self._playback and self._playback.isRunning():
            return

        self._repeat_count = repeat if repeat > 0 else 999999
        self._repeat_delay = delay
        self._repeat_remaining = self._repeat_count
        self._playing = True

        self._play_btn.setEnabled(False)
        self._repeat_btn.setEnabled(False)
        self._record_btn.setEnabled(False)
        if self._looping:
            self._status_label.setText("🔄 Loop infinito...")
            self._status_label.setStyleSheet("color: #4a8bff; font-weight: 600;")
        else:
            self._status_label.setText("▶️ Reproduzindo...")
            self._status_label.setStyleSheet("color: #55ff55; font-weight: 600;")

        self._run_next_playback()

    def _run_next_playback(self):
        if not self._playing or self._repeat_remaining <= 0:
            self._on_playback_done()
            return

        if self._repeat_remaining < self._repeat_count and self._repeat_delay > 0:
            QTimer.singleShot(int(self._repeat_delay * 1000), self._start_single_playback)
            return

        self._start_single_playback()

    def _start_single_playback(self):
        if not self._playing or self._repeat_remaining <= 0:
            self._on_playback_done()
            return

        self._repeat_remaining -= 1
        events = self._current_macro.events
        speed = self._speed()

        self._playback = PlaybackThread(events, speed, self)
        self._playback.set_delay_before(self._config.get("playback_delay", 0.5))
        self._playback.finished.connect(self._on_playback_finished, Qt.SingleShotConnection)
        self._playback.stopped.connect(self._on_playback_stopped, Qt.SingleShotConnection)
        self._playback.event_played.connect(self._on_event_played)
        self._playback.start()
        self._playback.start()

    def _on_playback_finished(self):
        if self._playing and self._repeat_remaining > 0:
            self._run_next_playback()
        else:
            self._on_playback_done()

    def _on_playback_stopped(self):
        self._on_playback_done()

    def _on_event_played(self, index, event):
        total = len(self._current_macro.events)
        self._events_label.setText(f"Evento: {index + 1}/{total}")
        if self._looping:
            remaining = max(0, self._repeat_remaining)
            self._status_label.setText(f"🔄 Loop... ({index + 1}/{total}) reps restantes: {remaining}")
        else:
            self._status_label.setText(f"▶️ Reproduzindo... ({index + 1}/{total})")
        self._status_label.setText(f"▶️ Reproduzindo... ({index + 1}/{total})")

    def _on_playback_done(self):
        self._playing = False
        self._playback = None
        if self._looping:
            self._run_next_playback()
            return
        self._play_btn.setEnabled(True)
        self._repeat_btn.setEnabled(True)
        self._record_btn.setEnabled(True)
        self._status_label.setText("✅ Reprodução concluída")
        self._status_label.setStyleSheet("color: #5a8bff; font-weight: 600;")
        self._events_label.setText(f"Eventos: {len(self._current_macro.events)}")

    def _stop_playback(self):
        self._playing = False
        self._looping = False
        self._repeat_remaining = 0
        if self._playback and self._playback.isRunning():
            self._playback.cancel()
            self._playback.wait(2000)
        self._playback = None
        self._play_btn.setEnabled(True)
        self._repeat_btn.setEnabled(True)
        self._repeat_btn.setChecked(False)
        self._record_btn.setEnabled(True)

    def _stop_everything(self):
        self._looping = False
        self._repeat_btn.setChecked(False)
        if self._recording:
            self._stop_recording()
        self._stop_playback()

    def _on_hotkey(self, action):
        if action == "record":
            if not self._recording:
                self._start_recording()
        elif action == "stop_record":
            if self._recording:
                self._stop_recording()
        elif action == "play":
            self._start_playback()
        elif action == "stop_all":
            self._stop_everything()
        elif action == "emergency_stop":
            self._stop_everything()

    def _new_macro(self):
        if self._recording or self._playing:
            self._stop_everything()
        self._current_macro = Macro()
        self._current_file = ""
        self._status_label.setText("✅ Nova macro criada")
        self._status_label.setStyleSheet("color: #5a8bff; font-weight: 600;")
        self._events_label.setText("Eventos: 0")
        self._timer_label.setText("⏱ 00:00")
        self.setWindowTitle("AutoClick — Gravador de Macro")

    def _open_macro(self):
        if self._recording or self._playing:
            self._stop_everything()
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Macro", "", "Macro Files (*.json);;All Files (*)"
        )
        if path:
            self._load_macro_file(path)

    def _load_macro_file(self, path):
        try:
            self._current_macro = self._persistence.load(path)
            self._current_file = path
            name = os.path.splitext(os.path.basename(path))[0]
            self.setWindowTitle(f"AutoClick — {name}")
            self._status_label.setText(f"✅ Macro carregada: {len(self._current_macro.events)} eventos")
            self._status_label.setStyleSheet("color: #5a8bff; font-weight: 600;")
            self._events_label.setText(f"Eventos: {len(self._current_macro.events)}")
            self._config.set("last_macro_file", path)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar macro:\n{e}")

    def _save_macro(self):
        if self._current_file:
            try:
                self._persistence.save(self._current_macro, self._current_file)
                self._status_label.setText("✅ Macro salva")
                self._status_label.setStyleSheet("color: #5a8bff; font-weight: 600;")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{e}")
        else:
            self._save_macro_as()

    def _save_macro_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Macro Como", "minha_macro.json",
            "Macro Files (*.json);;All Files (*)"
        )
        if path:
            if not path.endswith(".json"):
                path += ".json"
            self._current_file = path
            self._save_macro()
            name = os.path.splitext(os.path.basename(path))[0]
            self.setWindowTitle(f"AutoClick — {name}")

    def _open_editor(self):
        if not self._current_macro.events:
            QMessageBox.warning(self, "Aviso", "Nenhum evento para editar.")
            return
        dialog = EditorDialog(self._current_macro.events, self)
        if dialog.exec() == QDialog.Accepted:
            new_events = dialog.events
            if dialog.was_modified:
                self._current_macro.events = new_events
                self._events_label.setText(f"Eventos: {len(new_events)}")
                self._status_label.setText("✅ Eventos atualizados")
                self._status_label.setStyleSheet("color: #5a8bff; font-weight: 600;")

    def _open_settings(self):
        dialog = SettingsDialog(self._config, self)
        dialog.exec()
