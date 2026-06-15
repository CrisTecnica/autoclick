from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
    QDoubleSpinBox, QGroupBox,
)
from PySide6.QtCore import Qt
from ..models import MacroEvent


HEADERS = ["#", "Tempo", "Tipo", "Descrição", "Coord. X", "Coord. Y", "Tecla/ Botão"]


class EditorDialog(QDialog):
    def __init__(self, events: list, parent=None):
        super().__init__(parent)
        self._events = list(events)
        self.setWindowTitle("Editor de Eventos")
        self.resize(800, 500)
        self._modified = False
        self._build()

    @property
    def events(self):
        return list(self._events)

    @property
    def was_modified(self):
        return self._modified

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Editor de Eventos da Macro")
        title.setObjectName("editorTitle")
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._populate()
        layout.addWidget(self._table)

        controls = QGroupBox("Ações")
        clayout = QHBoxLayout(controls)

        self._delete_btn = QPushButton("Excluir")
        self._delete_btn.clicked.connect(self._delete_selected)
        clayout.addWidget(self._delete_btn)

        self._dup_btn = QPushButton("Duplicar")
        self._dup_btn.clicked.connect(self._duplicate_selected)
        clayout.addWidget(self._dup_btn)

        self._up_btn = QPushButton("Mover ↑")
        self._up_btn.clicked.connect(self._move_up)
        clayout.addWidget(self._up_btn)

        self._down_btn = QPushButton("Mover ↓")
        self._down_btn.clicked.connect(self._move_down)
        clayout.addWidget(self._down_btn)

        delay_group = QHBoxLayout()
        delay_group.addWidget(QLabel("Ajustar atraso (s):"))
        self._delay_spin = QDoubleSpinBox()
        self._delay_spin.setRange(0.0, 999.0)
        self._delay_spin.setSingleStep(0.1)
        self._delay_spin.setValue(0.0)
        delay_group.addWidget(self._delay_spin)
        self._apply_delay_btn = QPushButton("Aplicar ao selecionado")
        self._apply_delay_btn.clicked.connect(self._apply_delay)
        delay_group.addWidget(self._apply_delay_btn)
        delay_group.addStretch()

        layout.addWidget(controls)
        layout.addLayout(delay_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("accentButton")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("flatButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _populate(self):
        self._table.setRowCount(len(self._events))
        for i, ev in enumerate(self._events):
            self._table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self._table.setItem(i, 1, QTableWidgetItem(ev.time_str))
            self._table.setItem(i, 2, QTableWidgetItem(self._type_label(ev.event_type.value)))
            self._table.setItem(i, 3, QTableWidgetItem(ev.description))
            self._table.setItem(i, 4, QTableWidgetItem(str(ev.x) if ev.x is not None else ""))
            self._table.setItem(i, 5, QTableWidgetItem(str(ev.y) if ev.y is not None else ""))
            self._table.setItem(i, 6, QTableWidgetItem(str(ev.key or ev.button or "")))

    def _refresh(self):
        self._populate()

    @staticmethod
    def _type_label(t):
        labels = {
            "mouse_move": "Mouse Move",
            "mouse_press": "Clique ↓",
            "mouse_release": "Clique ↑",
            "mouse_scroll": "Scroll",
            "key_down": "Tecla ↓",
            "key_up": "Tecla ↑",
        }
        return labels.get(t, t)

    def _selected_row(self):
        rows = self._table.selectedIndexes()
        if not rows:
            return None
        return rows[0].row()

    def _delete_selected(self):
        row = self._selected_row()
        if row is None:
            return
        if QMessageBox.question(self, "Confirmar",
                                f"Excluir evento {row + 1}?") == QMessageBox.Yes:
            del self._events[row]
            self._modified = True
            self._refresh()

    def _duplicate_selected(self):
        row = self._selected_row()
        if row is None:
            return
        ev = self._events[row]
        import copy
        dup = copy.deepcopy(ev)
        self._events.insert(row + 1, dup)
        self._modified = True
        self._refresh()

    def _move_up(self):
        row = self._selected_row()
        if row is None or row == 0:
            return
        self._events[row], self._events[row - 1] = self._events[row - 1], self._events[row]
        self._modified = True
        self._refresh()
        new_row = row - 1
        self._table.selectRow(new_row)

    def _move_down(self):
        row = self._selected_row()
        if row is None or row >= len(self._events) - 1:
            return
        self._events[row], self._events[row + 1] = self._events[row + 1], self._events[row]
        self._modified = True
        self._refresh()
        self._table.selectRow(row + 1)

    def _apply_delay(self):
        row = self._selected_row()
        if row is None or row == 0:
            return
        new_delay = self._delay_spin.value()
        prev = self._events[row - 1]
        curr = self._events[row]
        curr.timestamp = prev.timestamp + new_delay
        self._modified = True
        self._refresh()
