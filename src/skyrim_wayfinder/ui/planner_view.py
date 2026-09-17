from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from skyrim_wayfinder.domain import PlannerItem, RegionType, TaskEvaluation, TaskStatus
from skyrim_wayfinder.services import WayfinderService
from .detail_dialog import DetailDialog
from .theme import domain_badges_html, objective_row_style, tinted_card_style


class PlannerView(QWidget):
    state_changed = Signal()
    MIN_PLANNER_WIDTH = 680
    SIDEBAR_WIDTH = 290

    def __init__(self, service: WayfinderService, parent=None) -> None:
        super().__init__(parent)
        self.service = service
        self._user_wants_preparation = service.state.get_setting("preparation_expanded", "1") == "1"
        root = QVBoxLayout(self)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Current region"))
        self.region = QComboBox()
        self.region.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.region.setMinimumContentsLength(18)
        self._populate_regions()
        self.region.currentIndexChanged.connect(self._region_changed)
        controls.addWidget(self.region, 1)
        controls.addWidget(QLabel("Player level"))
        self.level = QSpinBox()
        self.level.setRange(1, 100)
        self.level.setValue(service.state.player_level)
        self.level.valueChanged.connect(self._level_changed)
        controls.addWidget(self.level)
        self.preparation_toggle = QPushButton()
        self.preparation_toggle.clicked.connect(self._toggle_preparation)
        controls.addWidget(self.preparation_toggle)
        root.addLayout(controls)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.splitter.addWidget(self.left_scroll)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_header = QHBoxLayout()
        heading = QLabel("PREPARATION")
        heading.setObjectName("section")
        sidebar_header.addWidget(heading, 1)
        collapse = QPushButton("Collapse")
        collapse.clicked.connect(self._toggle_preparation)
        sidebar_header.addWidget(collapse)
        sidebar_layout.addLayout(sidebar_header)
        self.preparation_scroll = QScrollArea()
        self.preparation_scroll.setWidgetResizable(True)
        sidebar_layout.addWidget(self.preparation_scroll, 1)
        self.splitter.addWidget(self.sidebar)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        root.addWidget(self.splitter, 1)
        self.refresh()
        self._apply_sidebar_visibility()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._apply_sidebar_visibility()

    def _enough_room_for_sidebar(self) -> bool:
        return self.width() >= self.MIN_PLANNER_WIDTH + self.SIDEBAR_WIDTH + 50

    def _apply_sidebar_visibility(self) -> None:
        visible = self._user_wants_preparation and self._enough_room_for_sidebar()
        self.sidebar.setVisible(visible)
        if visible:
            self.splitter.setSizes([max(self.MIN_PLANNER_WIDTH, self.width() - self.SIDEBAR_WIDTH), self.SIDEBAR_WIDTH])
        self.preparation_toggle.setText("Hide Preparation" if visible else "Show Preparation")

    def _toggle_preparation(self) -> None:
        self._user_wants_preparation = not self.sidebar.isVisible()
        self.service.state.set_setting("preparation_expanded", "1" if self._user_wants_preparation else "0")
        self._apply_sidebar_visibility()

    def _region_changed(self, _index: int) -> None:
        self.service.state.current_region = self.region.currentData()
        self.refresh()
        self.state_changed.emit()

    def _level_changed(self, value: int) -> None:
        self.service.state.player_level = value
        self.refresh()
        self.state_changed.emit()

    def refresh(self) -> None:
        self._populate_regions()
        self._refresh_main()
        self._refresh_preparation()

    def _populate_regions(self) -> None:
        selected = self.service.state.current_region
        groups = self.service.operational_regions()
        blocker = QSignalBlocker(self.region)
        self.region.clear()
        self.region.addItem("Select current region…", None)
        labels = (
            (RegionType.CITY, "City Regions"),
            (RegionType.EXPEDITION, "Expeditions"),
            (RegionType.SPECIAL_DESTINATION, "Special Destinations"),
        )
        for region_type, label in labels:
            regions = groups.get(region_type, [])
            if not regions:
                continue
            self.region.addItem(label, None)
            header = self.region.model().item(self.region.count() - 1)
            if header:
                header.setEnabled(False)
            for region in regions:
                self.region.addItem(f"  {region.display_name}", region.id)
        index = self.region.findData(selected) if selected else 0
        if index < 0:
            self.service.state.current_region = None
            index = 0
        self.region.setCurrentIndex(index)
        del blocker

    def _refresh_main(self) -> None:
        body = QWidget()
        layout = QVBoxLayout(body)
        global_actions = self.service.global_actions()
        if global_actions:
            heading = QLabel("GLOBAL ACTIONS")
            heading.setObjectName("section")
            layout.addWidget(heading)
            for evaluation in global_actions:
                layout.addWidget(self._global_card(evaluation))
            layout.addSpacing(12)

        region_id = self.region.currentData()
        if not region_id:
            heading = QLabel("REGIONAL PLANNER")
            heading.setObjectName("section")
            layout.addWidget(heading)
            prompt = QLabel("Select your current region to see actionable work grouped by physical location.")
            prompt.setObjectName("muted")
            prompt.setWordWrap(True)
            layout.addWidget(prompt)
        else:
            region = self.service.content.regions[region_id]
            heading = QLabel(f"ACTIONABLE IN {region.display_name.upper()}")
            heading.setObjectName("section")
            layout.addWidget(heading)
            if region.departure_location_id:
                departure = self.service.content.locations[region.departure_location_id]
                departure_region = self.service.content.regions[departure.region_id]
                access = QLabel(
                    f"Access / departure: {departure.display_name}, {departure_region.display_name}"
                )
                access.setObjectName("warning")
                layout.addWidget(access)
            items = self.service.regional_plan(region_id)
            if not items:
                empty = QLabel(
                    "No actionable objectives in this region. Check Task Explorer for locked, deferred, completed, opportunistic, or milestone work."
                )
                empty.setWordWrap(True)
                empty.setObjectName("muted")
                layout.addWidget(empty)
            for item in items:
                layout.addWidget(self._location_card(item))
        layout.addStretch()
        self.left_scroll.setWidget(body)

    def _refresh_preparation(self) -> None:
        body = QWidget()
        layout = QVBoxLayout(body)
        preparations = self.service.outstanding_preparations()
        if not preparations:
            empty = QLabel("No outstanding preparation reminders.")
            empty.setObjectName("muted")
            empty.setWordWrap(True)
            layout.addWidget(empty)
        for evaluation in preparations:
            layout.addWidget(self._preparation_card(evaluation))
        layout.addStretch()
        self.preparation_scroll.setWidget(body)

    def _preparation_card(self, evaluation: TaskEvaluation) -> QFrame:
        frame = QFrame()
        frame.setObjectName("preparationCard")
        layout = QVBoxLayout(frame)
        text = QLabel(f"<b>{evaluation.task.title}</b><br>{evaluation.task.objective}")
        text.setWordWrap(True)
        layout.addWidget(text)
        buttons = QHBoxLayout()
        done = QPushButton("Done")
        done.clicked.connect(lambda: self._set_done(evaluation.task.id))
        buttons.addWidget(done)
        detail = QPushButton("Details")
        detail.clicked.connect(lambda: self._open(evaluation.task.id, False))
        buttons.addWidget(detail)
        layout.addLayout(buttons)
        return frame

    def _global_card(self, evaluation: TaskEvaluation) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        domain_ids = self.service.domain_ids_for_task(evaluation.task.id)
        if domain_ids:
            frame.setStyleSheet(tinted_card_style(domain_ids[0], self.service.content.theme))
        layout = QHBoxLayout(frame)
        text = QLabel(f"<b>{evaluation.task.title}</b><br>{evaluation.task.objective}")
        text.setWordWrap(True)
        layout.addWidget(text, 1)
        open_button = QPushButton("Open")
        open_button.clicked.connect(lambda: self._open(evaluation.task.id, False))
        layout.addWidget(open_button)
        return frame

    def _location_card(self, item: PlannerItem) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        if item.domain_ids:
            frame.setStyleSheet(tinted_card_style(item.domain_ids[0], self.service.content.theme))
        layout = QVBoxLayout(frame)
        top = QHBoxLayout()
        top.addWidget(QLabel(f"<b>{item.title}</b>"), 1)
        badges = QLabel(domain_badges_html(item.domain_ids, self.service.content.theme))
        badges.setWordWrap(True)
        top.addWidget(badges)
        layout.addLayout(top)
        for evaluation in item.tasks:
            domains = domain_badges_html(
                self.service.domain_ids_for_task(evaluation.task.id), self.service.content.theme
            )
            domain_ids = self.service.domain_ids_for_task(evaluation.task.id)
            objective_row = QFrame()
            objective_row.setObjectName("objectiveRow")
            if domain_ids:
                objective_row.setStyleSheet(objective_row_style(domain_ids[0], self.service.content.theme))
            objective_layout = QVBoxLayout(objective_row)
            objective_layout.setContentsMargins(10, 6, 8, 6)
            objective = QLabel(f"{evaluation.task.objective}<br><small>{domains}</small>")
            objective.setWordWrap(True)
            objective_layout.addWidget(objective)
            layout.addWidget(objective_row)
        count = QLabel(f"{len(item.tasks)} actionable objective{'s' if len(item.tasks) != 1 else ''}")
        count.setObjectName("muted")
        layout.addWidget(count)
        if item.warning_text:
            warning = QLabel(f"⚠ {item.warning_text}")
            warning.setObjectName("warning")
            warning.setWordWrap(True)
            layout.addWidget(warning)
        open_button = QPushButton("Open location")
        open_button.clicked.connect(lambda: self._open(item.id, True))
        layout.addWidget(open_button)
        return frame

    def _set_done(self, task_id: str) -> None:
        self.service.set_task_state(task_id, TaskStatus.COMPLETE)
        self.refresh()
        self.state_changed.emit()

    def _open(self, item_id: str, is_location: bool) -> None:
        dialog = DetailDialog(self.service, item_id, is_location, self)
        dialog.state_changed.connect(self._dialog_changed)
        dialog.exec()

    def _dialog_changed(self) -> None:
        self.refresh()
        self.state_changed.emit()
