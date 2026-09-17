from __future__ import annotations

import sys
from pathlib import Path

from skyrim_wayfinder.data import load_canonical_content
from skyrim_wayfinder.persistence import StateRepository, default_database_path
from skyrim_wayfinder.services import WayfinderService


def build_service(database_path: str | Path | None = None) -> WayfinderService:
    content = load_canonical_content()
    repository = StateRepository(database_path or default_database_path(), content.fingerprint)
    return WayfinderService(content, repository)


def main() -> int:
    from PySide6.QtWidgets import QApplication
    from skyrim_wayfinder.ui import MainWindow
    from skyrim_wayfinder.ui.theme import APP_STYLESHEET

    application = QApplication(sys.argv)
    application.setApplicationName("Skyrim Wayfinder")
    application.setStyle("Fusion")
    application.setStyleSheet(APP_STYLESHEET)
    service = build_service()
    window = MainWindow(service)
    window.show()
    result = application.exec()
    service.state.close()
    return result
