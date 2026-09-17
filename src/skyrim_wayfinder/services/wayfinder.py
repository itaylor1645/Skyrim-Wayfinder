from __future__ import annotations

from collections import defaultdict

from skyrim_wayfinder.domain import (
    CanonicalContent,
    PlannerBehavior,
    PlannerItem,
    Prerequisite,
    RegionType,
    Task,
    TaskEvaluation,
    TaskMembership,
    TaskStatus,
)
from skyrim_wayfinder.persistence import StateRepository


class ChoiceConfirmationRequired(RuntimeError):
    def __init__(self, task: Task, excluded_titles: list[str]) -> None:
        self.task = task
        self.excluded_titles = excluded_titles
        super().__init__(f"Completing {task.title} closes: {', '.join(excluded_titles)}")


class WayfinderService:
    def __init__(self, content: CanonicalContent, state: StateRepository) -> None:
        self.content = content
        self.state = state
        self._memberships_by_task: dict[str, list[TaskMembership]] = defaultdict(list)
        for membership in content.memberships.values():
            self._memberships_by_task[membership.task_id].append(membership)

    def memberships_for_task(self, task_id: str) -> tuple[TaskMembership, ...]:
        return tuple(sorted(self._memberships_by_task[task_id], key=self._membership_sort_key))

    def _membership_sort_key(self, membership: TaskMembership) -> tuple[int, int, int, int]:
        story = self.content.stories[membership.story_id]
        collection = self.content.collections[story.collection_id]
        domain = self.content.domains[collection.domain_id]
        return (domain.sort_order, collection.sort_order, story.sort_order, membership.sort_order)

    def domain_ids_for_task(self, task_id: str) -> tuple[str, ...]:
        domain_ids = {
            self.content.collections[self.content.stories[item.story_id].collection_id].domain_id
            for item in self._memberships_by_task[task_id]
        }
        return tuple(sorted(domain_ids, key=lambda item: self.content.domains[item].sort_order))

    def primary_domain_id(self, task_id: str) -> str:
        primary = next(item for item in self._memberships_by_task[task_id] if item.is_primary)
        story = self.content.stories[primary.story_id]
        return self.content.collections[story.collection_id].domain_id

    def evaluate(self, task_id: str, _stack: frozenset[str] = frozenset()) -> TaskEvaluation:
        task = self.content.tasks[task_id]
        stored = self.state.get_task_state(task_id)
        if stored is TaskStatus.NOT_APPLICABLE:
            return TaskEvaluation(task, TaskStatus.NOT_APPLICABLE, ("Manually marked Not Applicable.",), stored)
        exclusion_reason = self._choice_exclusion(task)
        if exclusion_reason:
            return TaskEvaluation(
                task, TaskStatus.NOT_APPLICABLE, (exclusion_reason,), stored, derived_exclusion=True
            )
        if stored is TaskStatus.COMPLETE:
            return TaskEvaluation(task, TaskStatus.COMPLETE, stored_state=stored)
        if task_id in _stack:
            return TaskEvaluation(task, TaskStatus.LOCKED, ("Circular prerequisite detected.",), stored)
        reasons = tuple(
            reason for prerequisite in task.prerequisites
            if (reason := self._unmet_reason(prerequisite, _stack | {task_id}))
        )
        if reasons:
            return TaskEvaluation(task, TaskStatus.LOCKED, reasons, stored)
        if stored in {TaskStatus.ACTIVE, TaskStatus.DEFERRED, TaskStatus.BLOCKED}:
            return TaskEvaluation(task, stored, stored_state=stored)
        default = TaskStatus.ACTIVE if task.planner_behavior is PlannerBehavior.PREPARATION else TaskStatus.AVAILABLE
        return TaskEvaluation(task, default, stored_state=stored)

    def _choice_exclusion(self, task: Task) -> str | None:
        if not task.choice_id or not task.choice_option:
            return None
        selected = self.state.get_choice(task.choice_id)
        if not selected or selected == task.choice_option:
            return None
        choice = self.content.choices[task.choice_id]
        selected_option = choice.options[selected]
        if task.choice_option in selected_option.excludes_options:
            return f"Unavailable because the '{selected_option.label}' path was chosen."
        return None

    def _unmet_reason(self, condition: Prerequisite, stack: frozenset[str]) -> str | None:
        if condition.type in {"task_complete", "preparation_complete"}:
            assert condition.task_id
            if self.evaluate(condition.task_id, stack).status is not TaskStatus.COMPLETE:
                title = self.content.tasks[condition.task_id].title
                prefix = "Preparation required" if condition.type == "preparation_complete" else "Requires completion"
                return condition.description or f"{prefix}: {title}."
        elif condition.type == "minimum_level":
            assert condition.minimum_level is not None
            if self.state.player_level < condition.minimum_level:
                return condition.description or f"Requires player level {condition.minimum_level}."
        elif condition.type == "choice":
            if self.state.get_choice(condition.choice_id or "") != condition.option:
                return condition.description or "Requires a different player choice."
        else:
            return f"Unsupported prerequisite type: {condition.type}."
        return None

    def set_task_state(
        self, task_id: str, status: TaskStatus | None, *, confirm_choice: bool = False
    ) -> None:
        if status in {TaskStatus.AVAILABLE, TaskStatus.LOCKED}:
            raise ValueError(f"{status.value} is derived and cannot be assigned")
        task = self.content.tasks[task_id]
        if status is TaskStatus.COMPLETE and task.sets_choice:
            excluded = self._tasks_excluded_by(task)
            if excluded and not confirm_choice:
                raise ChoiceConfirmationRequired(task, [item.title for item in excluded])
            assert task.choice_id and task.choice_option
            self.state.set_choice(task.choice_id, task.choice_option)
        if status is None:
            self.state.reset_task_state(task_id)
            if task.sets_choice and task.choice_id and task.choice_option:
                self.state.reset_choice(task.choice_id, task.choice_option)
        else:
            if status is not TaskStatus.COMPLETE and task.sets_choice and task.choice_id and task.choice_option:
                self.state.reset_choice(task.choice_id, task.choice_option)
            self.state.set_task_state(task_id, status)

    def _tasks_excluded_by(self, task: Task) -> list[Task]:
        if not task.choice_id or not task.choice_option:
            return []
        choice = self.content.choices[task.choice_id]
        excluded_options = choice.options[task.choice_option].excludes_options
        return [
            item for item in self.content.tasks.values()
            if item.choice_id == task.choice_id and item.choice_option in excluded_options
            and self.evaluate(item.id).status is not TaskStatus.NOT_APPLICABLE
        ]

    def _task_sort_key(self, evaluation: TaskEvaluation) -> tuple[int, int, str]:
        memberships = self.memberships_for_task(evaluation.task.id)
        return (
            min(self.content.domains[domain].sort_order for domain in self.domain_ids_for_task(evaluation.task.id)),
            min(item.sort_order for item in memberships),
            evaluation.task.title,
        )

    def regional_plan(self, region_id: str) -> list[PlannerItem]:
        actionable = {TaskStatus.AVAILABLE, TaskStatus.ACTIVE}
        grouped: dict[str, list[TaskEvaluation]] = defaultdict(list)
        for task in self.content.tasks.values():
            if task.planner_behavior is not PlannerBehavior.REGIONAL_ACTION or not task.location_id:
                continue
            location = self.content.locations[task.location_id]
            if location.region_id != region_id:
                continue
            evaluation = self.evaluate(task.id)
            if evaluation.status in actionable:
                grouped[location.id].append(evaluation)
        result: list[PlannerItem] = []
        for location_id, evaluations in grouped.items():
            location = self.content.locations[location_id]
            ordered = tuple(sorted(evaluations, key=self._task_sort_key))
            domains = {
                domain_id for evaluation in ordered
                for domain_id in self.domain_ids_for_task(evaluation.task.id)
            }
            domain_ids = tuple(sorted(domains, key=lambda item: self.content.domains[item].sort_order))
            result.append(PlannerItem(location.id, location.display_name, location, ordered, domain_ids))
        return sorted(
            result,
            key=lambda item: (
                min(self.content.domains[domain].sort_order for domain in item.domain_ids),
                item.location.display_name,
            ),
        )

    def global_actions(self) -> list[TaskEvaluation]:
        actionable = {TaskStatus.AVAILABLE, TaskStatus.ACTIVE}
        return sorted(
            [
                self.evaluate(task.id) for task in self.content.tasks.values()
                if task.planner_behavior is PlannerBehavior.GLOBAL_ACTION
                and self.evaluate(task.id).status in actionable
            ],
            key=self._task_sort_key,
        )

    def operational_regions(self) -> dict[RegionType, list]:
        """Return selector regions grouped according to Product-approved visibility rules."""
        tasks_by_region: dict[str, list[Task]] = defaultdict(list)
        for task in self.content.tasks.values():
            if task.location_id:
                location = self.content.locations[task.location_id]
                tasks_by_region[location.region_id].append(task)
        result: dict[RegionType, list] = {
            RegionType.CITY: [],
            RegionType.EXPEDITION: [],
            RegionType.SPECIAL_DESTINATION: [],
        }
        actionable = {TaskStatus.AVAILABLE, TaskStatus.ACTIVE}
        for region in sorted(self.content.regions.values(), key=lambda item: item.sort_order):
            tasks = tasks_by_region.get(region.id, [])
            if not tasks:
                continue
            if region.region_type is not RegionType.CITY and not any(
                task.planner_behavior is PlannerBehavior.REGIONAL_ACTION
                and self.evaluate(task.id).status in actionable
                for task in tasks
            ):
                continue
            result[region.region_type].append(region)
        return result

    def location_evaluations(self, location_id: str) -> list[TaskEvaluation]:
        return sorted(
            [
                self.evaluate(task.id) for task in self.content.tasks.values()
                if task.location_id == location_id
            ],
            key=self._task_sort_key,
        )

    def outstanding_preparations(self) -> list[TaskEvaluation]:
        result: list[TaskEvaluation] = []
        for task in self.content.tasks.values():
            if task.planner_behavior is not PlannerBehavior.PREPARATION:
                continue
            evaluation = self.evaluate(task.id)
            if evaluation.status in {TaskStatus.COMPLETE, TaskStatus.NOT_APPLICABLE}:
                continue
            targets = [self.evaluate(target) for target in task.preparation_for]
            if targets and all(target.status in {TaskStatus.COMPLETE, TaskStatus.NOT_APPLICABLE} for target in targets):
                continue
            result.append(evaluation)
        return sorted(result, key=self._task_sort_key)

    def explorer_tree(
        self,
    ) -> dict[str, dict[str, dict[str, list[tuple[TaskMembership, TaskEvaluation]]]]]:
        result: dict[str, dict[str, dict[str, list[tuple[TaskMembership, TaskEvaluation]]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )
        evaluations = {task_id: self.evaluate(task_id) for task_id in self.content.tasks}
        for membership in self.content.memberships.values():
            story = self.content.stories[membership.story_id]
            collection = self.content.collections[story.collection_id]
            result[collection.domain_id][collection.id][story.id].append(
                (membership, evaluations[membership.task_id])
            )
        return {
            domain: {
                collection: dict(stories) for collection, stories in collections.items()
            }
            for domain, collections in result.items()
        }

    def overall_completion(self) -> tuple[int, int]:
        """Return unique completed Tasks and unique total Tasks, never membership counts."""
        completed = sum(
            self.evaluate(task_id).status is TaskStatus.COMPLETE for task_id in self.content.tasks
        )
        return completed, len(self.content.tasks)
