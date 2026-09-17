from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMainWindow, QTabWidget

from skyrim_wayfinder.services import WayfinderService
from .explorer_view import ExplorerView
from .planner_view import PlannerView


class MainWindow(QMainWindow):
    def __init__(self, service: WayfinderService) -> None:
        super().__init__()
        self.service = service
        self.setWindowTitle("Skyrim Wayfinder")
        self.resize(1040, 760)
        tabs = QTabWidget()
        self.planner = PlannerView(service)
        self.explorer = ExplorerView(service)
        self.planner.state_changed.connect(self.explorer.refresh)
        self.explorer.state_changed.connect(self.planner.refresh)
        tabs.addTab(self.planner, "Regional Planner")
        tabs.addTab(self.explorer, "Task Explorer")
        self.setCentralWidget(tabs)
        self.statusBar().addPermanentWidget(QLabel("Increment 1 · Local-only state"))
