from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import QCheckBox, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

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
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Objective", "Status", "Region", "Location"])
        self.tree.setAlternatingRowColors(True)
        self.tree.itemDoubleClicked.connect(self._open_item)
        layout.addWidget(self.tree, 1)
        self.refresh()

    def refresh(self) -> None:
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
                collection_item = QTreeWidgetItem([
                    f"{collection.display_name}  {collection_done} / {collection_total}"
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
