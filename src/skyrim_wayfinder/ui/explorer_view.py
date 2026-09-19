from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QInputDialog, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from skyrim_wayfinder.domain import TaskStatus
from skyrim_wayfinder.services import WayfinderService
from .detail_dialog import DetailDialog
from .theme import domain_color


class ExplorerView(QWidget):
    state_changed = Signal()

    def __init__(self, service: WayfinderService, parent=None) -> None:
        super().__init__(parent)
        self.service = service
        layout = QVBoxLayout(self)
        heading = QLabel("Completion ledger")
        heading.setObjectName("heading")
        layout.addWidget(heading)
        hint = QLabel("Double-click an objective to inspect it or correct its state. A task may appear in multiple branches but has one state.")
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.hide_completed = QCheckBox("Hide completed objectives")
        self.hide_completed.setChecked(
            service.state.get_setting("hide_completed_objectives", "1") == "1"
        )
        self.hide_completed.toggled.connect(self._filter_changed)
        layout.addWidget(self.hide_completed)
        self.guild_status = QLabel()
        self.guild_status.setWordWrap(True)
        layout.addWidget(self.guild_status)
        self.guild_counters: dict[str, QLabel] = {}
        if "thieves_guild" in service.content.collections:
            for city in ("whiterun", "markarth", "solitude", "windhelm"):
                progress_id = f"guild_influence_{city}"
                row = QHBoxLayout()
                label = QLabel()
                self.guild_counters[progress_id] = label
                row.addWidget(label, 1)
                for text, delta in (("−", -1), ("+", 1)):
                    button = QPushButton(text)
                    button.setFixedWidth(32)
                    button.clicked.connect(lambda _checked=False, key=progress_id, change=delta: self._adjust_progress(key, change))
                    row.addWidget(button)
                reset = QPushButton("Reset")
                reset.clicked.connect(lambda _checked=False, key=progress_id: self._reset_progress(key))
                row.addWidget(reset)
                correct = QPushButton("Correct…")
                correct.clicked.connect(lambda _checked=False, key=progress_id: self._correct_progress(key))
                row.addWidget(correct)
                layout.addLayout(row)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Objective", "Status", "Region", "Location"])
        self.tree.setAlternatingRowColors(True)
        self.tree.itemDoubleClicked.connect(self._open_item)
        layout.addWidget(self.tree, 1)
        self.refresh()

    def refresh(self) -> None:
        if "thieves_guild" in self.service.content.collections:
            narrative, restored = self.service.thieves_guild_landmarks()
            self.guild_status.setText(
                "Thieves Guild — Mercer/Nightingale narrative: "
                + ("Complete" if narrative else "Incomplete")
                + "  ·  Guild restoration: "
                + ("Complete" if restored else "Incomplete")
                + "\nOnly successfully completed Whiterun, Markarth, Solitude, or Windhelm Delvin/Vex jobs count."
            )
            for key, label in self.guild_counters.items():
                current, required = self.service.finite_progress(key)
                label.setText(f"{self.service.content.finite_progress[key].display_name}: {current} / {required}")
        self.tree.clear()
        tree = self.service.explorer_tree()
        hide_completed = self.hide_completed.isChecked()
        for domain in sorted(self.service.content.domains.values(), key=lambda item: item.sort_order):
            collections = tree.get(domain.id)
            if not collections:
                continue
            domain_entries = [
                entry
                for stories in collections.values()
                for entries in stories.values()
                for entry in entries
            ]
            visible_domain_entries = self._visible_entries(domain_entries, hide_completed)
            if not visible_domain_entries:
                continue
            domain_done, domain_total = self.service.domain_progress(domain.id)
            domain_item = QTreeWidgetItem([f"{domain.display_name}  {domain_done} / {domain_total}"])
            domain_item.setForeground(
                0, QBrush(QColor(domain_color(domain.id, self.service.content.theme)))
            )
            self.tree.addTopLevelItem(domain_item)
            for collection in sorted(
                (self.service.content.collections[item] for item in collections),
                key=lambda item: item.sort_order,
            ):
                stories = collections[collection.id]
                collection_entries = [entry for entries in stories.values() for entry in entries]
                if not self._visible_entries(collection_entries, hide_completed):
                    continue
                collection_done, collection_total = self.service.collection_progress(collection.id)
                catalog_total = self.service.collection_catalog_total(collection.id)
                progress_text = f"{collection_done} / {collection_total}"
                if catalog_total != collection_total or collection.id == "daedric_artifacts":
                    progress_text += f" achievable Â· {catalog_total} catalog"
                collection_item = QTreeWidgetItem([
                    f"{collection.display_name}  {progress_text}"
                ])
                domain_item.addChild(collection_item)
                for story in sorted(
                    (self.service.content.stories[item] for item in stories),
                    key=lambda item: item.sort_order,
                ):
                    entries = sorted(stories[story.id], key=lambda pair: (pair[0].sort_order, pair[1].task.title))
                    visible_entries = self._visible_entries(entries, hide_completed)
                    if not visible_entries:
                        continue
                    story_done, story_total = self.service.story_progress(story.id)
                    story_item = QTreeWidgetItem([
                        f"{story.display_name}  {story_done} / {story_total}"
                    ])
                    collection_item.addChild(story_item)
                    for _membership, evaluation in visible_entries:
                        task = evaluation.task
                        location = self.service.content.locations.get(task.location_id or "")
                        if location:
                            region_name = self.service.content.regions[location.region_id].display_name
                            location_name = location.display_name
                        else:
                            region_name = "—"
                            location_name = "No fixed location"
                        item = QTreeWidgetItem([
                            task.title,
                            evaluation.status.value.replace("_", " ").title(),
                            region_name,
                            location_name,
                        ])
                        item.setData(0, Qt.ItemDataRole.UserRole, task.id)
                        if evaluation.status is TaskStatus.COMPLETE:
                            item.setForeground(0, QBrush(QColor("#83b98b")))
                        elif evaluation.status in {TaskStatus.LOCKED, TaskStatus.NOT_APPLICABLE}:
                            for column in range(4):
                                item.setForeground(column, QBrush(QColor("#7f8790")))
                        story_item.addChild(item)
        self.tree.setColumnWidth(0, 430)
        self.tree.setColumnWidth(1, 110)
        self.tree.setColumnWidth(2, 220)
        self.tree.setColumnWidth(3, 220)

    @staticmethod
    def _visible_entries(entries, hide_completed: bool):
        if not hide_completed:
            return entries
        return [entry for entry in entries if entry[1].status is not TaskStatus.COMPLETE]

    @staticmethod
    def _progress(entries) -> tuple[int, int]:
        evaluations = {entry[1].task.id: entry[1] for entry in entries}
        done = sum(item.status is TaskStatus.COMPLETE for item in evaluations.values())
        return done, len(evaluations)

    def _filter_changed(self, checked: bool) -> None:
        self.service.state.set_setting("hide_completed_objectives", "1" if checked else "0")
        self.refresh()

    def _adjust_progress(self, progress_id: str, delta: int) -> None:
        current, _required = self.service.finite_progress(progress_id)
        self.service.set_finite_progress(progress_id, current + delta)
        self._changed()

    def _reset_progress(self, progress_id: str) -> None:
        self.service.set_finite_progress(progress_id, 0)
        self._changed()

    def _correct_progress(self, progress_id: str) -> None:
        current, required = self.service.finite_progress(progress_id)
        label = self.service.content.finite_progress[progress_id].display_name
        value, accepted = QInputDialog.getInt(
            self, "Correct Guild influence", f"Successfully completed jobs toward {label}:",
            current, 0, required,
        )
        if accepted:
            self.service.set_finite_progress(progress_id, value)
            self._changed()

    def _open_item(self, item: QTreeWidgetItem) -> None:
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not task_id:
            item.setExpanded(not item.isExpanded())
            return
        dialog = DetailDialog(self.service, task_id, False, self)
        dialog.state_changed.connect(self._changed)
        dialog.exec()

    def _changed(self) -> None:
        self.refresh()
        self.state_changed.emit()
