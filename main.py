#!/usr/bin/env python3
import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from autoclick.ui.main_window import MainWindow


def find_icon():
    paths = [
        os.path.join(app_dir, "autoclick.svg"),
        os.path.join(app_dir, "icons", "autoclick_256.png"),
        os.path.join(app_dir, "icons", "autoclick_128.png"),
        os.path.join(app_dir, "icons", "autoclick_64.png"),
        "/usr/share/icons/hicolor/256x256/apps/autoclick.png",
        "/usr/share/icons/hicolor/128x128/apps/autoclick.png",
        "/usr/share/icons/hicolor/64x64/apps/autoclick.png",
        "/usr/share/icons/hicolor/scalable/apps/autoclick.svg",
    ]
    for p in paths:
        if os.path.exists(p):
            return p


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AutoClick")
    app.setOrganizationName("AutoClick")
    app.setStyle("Fusion")

    icon_path = find_icon()
    if icon_path:
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
