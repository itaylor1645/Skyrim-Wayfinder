from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from skyrim_wayfinder.domain import TaskEvaluation, TaskStatus
from skyrim_wayfinder.services import ChoiceConfirmationRequired, TaskOutcomeRequired, WayfinderService
from .theme import domain_badges_html, tinted_card_style


class DetailDialog(QDialog):
    state_changed = Signal()

    def __init__(self, service: WayfinderService, item_id: str, is_location: bool, parent=None) -> None:
        super().__init__(parent)
        self.service = service
        self.item_id = item_id
        self.is_location = is_location
        self.setMinimumSize(680, 520)
        self.setWindowTitle("Objective details")
        self._root = QVBoxLayout(self)
        self._render()

    def _clear(self) -> None:
        while self._root.count():
            item = self._root.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render(self) -> None:
        self._clear()
        if self.is_location:
            location = self.service.content.locations[self.item_id]
            heading = location.display_name
            region = self.service.content.regions[location.region_id]
            subtitle = f"Region: {region.display_name}  •  Location: {location.display_name}"
            evaluations = self.service.location_evaluations(location.id)
            warning = location.warning_text
            source_urls = location.source_urls
        else:
            task = self.service.content.tasks[self.item_id]
            heading = task.title
            location = self.service.content.locations.get(task.location_id or "")
            region = self.service.content.regions[location.region_id] if location else None
            subtitle = (
                f"Region: {region.display_name}  •  Location: {location.display_name}"
                if location and region else "Region: None  •  Location: No fixed location"
            )
            evaluations = [self.service.evaluate(task.id)]
            warning = task.warning_text
            source_urls = (task.source_url,) if task.source_url else ()
        title = QLabel(heading.upper())
        title.setObjectName("heading")
        self._root.addWidget(title)
        sub = QLabel(subtitle)
        sub.setObjectName("muted")
        self._root.addWidget(sub)
        if region and region.departure_location_id:
            departure = self.service.content.locations[region.departure_location_id]
            departure_region = self.service.content.regions[departure.region_id]
            access = QLabel(
                f"Access / departure: {departure.display_name}, {departure_region.display_name}"
            )
            access.setObjectName("warning")
            self._root.addWidget(access)
        if warning:
            label = QLabel(f"⚠ {warning}")
            label.setObjectName("warning")
            label.setWordWrap(True)
            self._root.addWidget(label)
        for source_index, source_url in enumerate(source_urls, start=1):
            label = "Canonical source" if len(source_urls) == 1 else f"Canonical source {source_index}"
            source = QLabel(f'<a style="color:#8fc7e8" href="{source_url}">{label}</a>')
            source.setOpenExternalLinks(True)
            self._root.addWidget(source)
        self._root.addSpacing(8)
        section = QLabel("DO HERE")
        section.setObjectName("section")
        self._root.addWidget(section)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        for evaluation in evaluations:
            layout.addWidget(self._task_panel(evaluation))
        layout.addStretch()
        scroll.setWidget(body)
        self._root.addWidget(scroll, 1)
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        self._root.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)

    def _task_panel(self, evaluation: TaskEvaluation) -> QFrame:
        task = evaluation.task
        panel = QFrame()
        panel.setObjectName("card")
        domain_ids = self.service.domain_ids_for_task(task.id)
        if domain_ids:
            panel.setStyleSheet(tinted_card_style(domain_ids[0], self.service.content.theme))
        layout = QVBoxLayout(panel)
        top = QHBoxLayout()
        title = QLabel(f"{task.title}  ·  {evaluation.status.value.replace('_', ' ').title()}")
        title.setStyleSheet("font-weight:600")
        top.addWidget(title, 1)
        badge = QLabel(domain_badges_html(domain_ids, self.service.content.theme))
        badge.setObjectName("muted")
        top.addWidget(badge)
        layout.addLayout(top)
        objective = QLabel(task.objective)
        objective.setWordWrap(True)
        layout.addWidget(objective)
        if evaluation.reasons:
            reason = QLabel("\n".join(f"Locked: {item}" for item in evaluation.reasons))
            reason.setObjectName("warning" if evaluation.status is TaskStatus.LOCKED else "muted")
            reason.setWordWrap(True)
            layout.addWidget(reason)
        for condition_id in task.access_condition_ids:
            condition = self.service.content.access_conditions[condition_id]
            manual_satisfied = self.service.state.is_access_condition_satisfied(condition_id)
            satisfied = self.service.is_access_condition_satisfied(condition_id)
            access = QHBoxLayout()
            note = QLabel(f"Access condition: {condition.label}\n{condition.description}")
            note.setWordWrap(True)
            access.addWidget(note, 1)
            if manual_satisfied:
                button = QPushButton("Reset manual access")
                button.clicked.connect(
                    lambda _checked=False, item=condition_id: self._set_access(item, False)
                )
            elif satisfied:
                button = QPushButton("Progression satisfied")
                button.setEnabled(False)
            else:
                button = QPushButton("Mark access satisfied")
                button.clicked.connect(
                    lambda _checked=False, item=condition_id: self._set_access(item, True)
                )
            access.addWidget(button)
            layout.addLayout(access)
        if task.review_note:
            note = QLabel(f"Dataset note: {task.review_note}")
            note.setObjectName("muted")
            note.setWordWrap(True)
            layout.addWidget(note)
        buttons = QHBoxLayout()
        for label, status in (
            ("Mark Done", TaskStatus.COMPLETE),
            ("Defer", TaskStatus.DEFERRED),
            ("Block", TaskStatus.BLOCKED),
            ("Start", TaskStatus.ACTIVE),
        ):
            button = QPushButton(label)
            button.setEnabled(evaluation.status not in {TaskStatus.LOCKED, TaskStatus.NOT_APPLICABLE})
            button.clicked.connect(lambda _checked=False, task_id=task.id, value=status: self._change(task_id, value))
            buttons.addWidget(button)
        correction = QComboBox()
        correction.addItems([
            "Correct State…", "Complete", "Deferred", "Blocked", "Not Applicable", "Reset to Automatic"
        ])
        correction.activated.connect(lambda index, task_id=task.id, combo=correction: self._correct(task_id, combo, index))
        buttons.addWidget(correction)
        layout.addLayout(buttons)
        if not self.is_location:
            for membership in self.service.memberships_for_task(task.id):
                story = self.service.content.stories[membership.story_id]
                if not story.resolution_choice_id:
                    continue
                choice = self.service.content.choices[story.resolution_choice_id]
                resolution = QHBoxLayout()
                for option in choice.options.values():
                    if not option.manual_resolution:
                        continue
                    button = QPushButton(f"Resolve as {option.label}")
                    button.clicked.connect(
                        lambda _checked=False, choice_id=choice.id, option_id=option.id:
                        self._resolve_choice(choice_id, option_id)
                    )
                    resolution.addWidget(button)
                if self.service.state.get_choice(choice.id):
                    reset = QPushButton("Reset resolution")
                    reset.clicked.connect(
                        lambda _checked=False, choice_id=choice.id: self._resolve_choice(choice_id, None)
                    )
                    resolution.addWidget(reset)
                layout.addLayout(resolution)
        return panel

    def _resolve_choice(self, choice_id: str, option_id: str | None) -> None:
        self.service.set_manual_choice(choice_id, option_id)
        self.state_changed.emit()
        self._render()

    def _set_access(self, condition_id: str, satisfied: bool) -> None:
        self.service.set_access_condition(condition_id, satisfied)
        self.state_changed.emit()
        self._render()

    def _correct(self, task_id: str, combo: QComboBox, index: int) -> None:
        combo.setCurrentIndex(0)
        mapping = {
            1: TaskStatus.COMPLETE,
            2: TaskStatus.DEFERRED,
            3: TaskStatus.BLOCKED,
            4: TaskStatus.NOT_APPLICABLE,
            5: None,
        }
        if index in mapping:
            self._change(task_id, mapping[index])

    def _change(self, task_id: str, status: TaskStatus | None) -> None:
        try:
            self.service.set_task_state(task_id, status)
        except TaskOutcomeRequired as required:
            options = list(required.task.outcome_options.items())
            labels = [label for _option_id, label in options]
            label, accepted = QInputDialog.getItem(
                self, "Record observed Skyrim outcome",
                "What happened in Skyrim?", labels, 0, False,
            )
            if not accepted:
                return
            outcome_id = options[labels.index(label)][0]
            self.service.set_task_state(task_id, status, outcome_id=outcome_id)
        except ChoiceConfirmationRequired as choice:
            opposing = "\n".join(f"• {title}" for title in choice.excluded_titles)
            answer = QMessageBox.warning(
                self,
                "This choice will close another path",
                f"Completing {choice.task.title} will make these objectives unavailable:\n\n{opposing}\n\n"
                "Their stored Deferred or Blocked state will be preserved. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            self.service.set_task_state(task_id, status, confirm_choice=True)
        self.state_changed.emit()
        self._render()
