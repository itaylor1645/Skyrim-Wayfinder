from __future__ import annotations

from collections import defaultdict

from skyrim_wayfinder.domain import (
    CanonicalContent,
    CompletionRole,
    PlannerBehavior,
    PlannerItem,
    Prerequisite,
    RegionType,
    Task,
    TaskEvaluation,
    TaskMembership,
    TaskStatus,
    StoryClassification,
)
from skyrim_wayfinder.persistence import StateRepository


class ChoiceConfirmationRequired(RuntimeError):
    def __init__(self, task: Task, excluded_titles: list[str]) -> None:
        self.task = task
        self.excluded_titles = excluded_titles
        super().__init__(f"Completing {task.title} closes: {', '.join(excluded_titles)}")


class TaskOutcomeRequired(RuntimeError):
    def __init__(self, task: Task) -> None:
        self.task = task
        super().__init__(f"Completing {task.title} requires an observed outcome")


class WayfinderService:
    def __init__(self, content: CanonicalContent, state: StateRepository) -> None:
        self.content = content
        self.state = state
        self._memberships_by_task: dict[str, list[TaskMembership]] = defaultdict(list)
        for membership in content.memberships.values():
            self._memberships_by_task[membership.task_id].append(membership)
        self._collectible_credits_by_task = defaultdict(list)
        for credit in content.collectible_credits.values():
            self._collectible_credits_by_task[credit.task_id].append(credit)

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
        if task.applicable_outcome_task_id:
            observed = self.state.get_task_outcome(task.applicable_outcome_task_id)
            if observed != task.applicable_outcome:
                reason = (
                    "Conditional path is not active yet."
                    if observed is None
                    else "Not applicable for the observed quest outcome."
                )
                return TaskEvaluation(
                    task, TaskStatus.NOT_APPLICABLE, (reason,), stored,
                    derived_exclusion=True,
                )
        exclusion_reason = self._choice_exclusion(task)
        if exclusion_reason:
            return TaskEvaluation(
                task, TaskStatus.NOT_APPLICABLE, (exclusion_reason,), stored, derived_exclusion=True
            )
        if stored is TaskStatus.COMPLETE:
            return TaskEvaluation(task, TaskStatus.COMPLETE, stored_state=stored)
        alternative_reason = self._collectible_alternative_exclusion(task_id)
        if alternative_reason:
            return TaskEvaluation(
                task, TaskStatus.NOT_APPLICABLE, (alternative_reason,), stored,
                derived_exclusion=True,
            )
        if task_id in _stack:
            return TaskEvaluation(task, TaskStatus.LOCKED, ("Circular prerequisite detected.",), stored)
        if task.expires_after_task_id:
            expiration = self.evaluate(task.expires_after_task_id, _stack | {task_id})
            if expiration.status is TaskStatus.COMPLETE:
                return TaskEvaluation(
                    task, TaskStatus.NOT_APPLICABLE,
                    (f"Opportunity expired after: {expiration.task.title}.",), stored,
                    derived_exclusion=True,
                )
        reasons = tuple(
            reason for prerequisite in task.prerequisites
            if (reason := self._unmet_reason(prerequisite, _stack | {task_id}))
        )
        reasons += tuple(
            f"Access required: {self.content.access_conditions[item].label}."
            for item in task.access_condition_ids
            if not self.state.is_access_condition_satisfied(item)
        )
        reasons += tuple(
            f"Requires prior acquisition: {self.content.collectibles[item].display_name}."
            for item in task.required_collectible_ids
            if not self.collectible_complete(item)
        )
        if task.any_of_task_ids and not any(
            self.evaluate(item, _stack | {task_id}).status is TaskStatus.COMPLETE
            for item in task.any_of_task_ids
        ):
            alternatives = ", ".join(self.content.tasks[item].title for item in task.any_of_task_ids)
            reasons += (f"Requires any one of: {alternatives}.",)
        if reasons:
            return TaskEvaluation(task, TaskStatus.LOCKED, reasons, stored)
        if stored in {TaskStatus.ACTIVE, TaskStatus.DEFERRED, TaskStatus.BLOCKED}:
            return TaskEvaluation(task, stored, stored_state=stored)
        default = TaskStatus.ACTIVE if task.planner_behavior is PlannerBehavior.PREPARATION else TaskStatus.AVAILABLE
        return TaskEvaluation(task, default, stored_state=stored)

    def _collectible_alternative_exclusion(self, task_id: str) -> str | None:
        for credit in self._collectible_credits_by_task[task_id]:
            collectible = self.content.collectibles[credit.collectible_id]
            if collectible.completion_rule.value != "ANY":
                continue
            for other in self.content.collectible_credits.values():
                if (
                    other.collectible_id == credit.collectible_id
                    and other.task_id != task_id
                    and self.state.get_task_state(other.task_id) is TaskStatus.COMPLETE
                ):
                    return f"Already acquired via: {self.content.tasks[other.task_id].title}."
        return None

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
        if condition.when_outcome_task_id:
            observed = self.state.get_task_outcome(condition.when_outcome_task_id)
            if observed != condition.when_outcome:
                return None
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
        self, task_id: str, status: TaskStatus | None, *, confirm_choice: bool = False,
        outcome_id: str | None = None,
    ) -> None:
        if status in {TaskStatus.AVAILABLE, TaskStatus.LOCKED}:
            raise ValueError(f"{status.value} is derived and cannot be assigned")
        task = self.content.tasks[task_id]
        if status is TaskStatus.COMPLETE and task.outcome_options:
            if outcome_id is None:
                raise TaskOutcomeRequired(task)
            if outcome_id not in task.outcome_options:
                raise ValueError(f"Invalid outcome for {task_id}: {outcome_id}")
        if status is TaskStatus.COMPLETE and task.sets_choice:
            excluded = self._tasks_excluded_by(task)
            assert task.choice_id and task.choice_option
            current_option = self.state.get_choice(task.choice_id)
            conflicts_with_resolution = bool(
                current_option
                and current_option != task.choice_option
                and task.choice_option
                in self.content.choices[task.choice_id].options[current_option].excludes_options
            )
            if (excluded or conflicts_with_resolution) and not confirm_choice:
                titles = [item.title for item in excluded]
                if conflicts_with_resolution and current_option:
                    label = self.content.choices[task.choice_id].options[current_option].label
                    titles.append(f"current resolution: {label}")
                raise ChoiceConfirmationRequired(task, titles)
            self.state.set_choice(task.choice_id, task.choice_option)
        if status is TaskStatus.COMPLETE and outcome_id:
            self.state.set_task_outcome(task_id, outcome_id)
        if status is None:
            self.state.reset_task_state(task_id)
            self.state.reset_task_outcome(task_id)
            if task.sets_choice and task.choice_id and task.choice_option:
                self.state.reset_choice(task.choice_id, task.choice_option)
        else:
            if status is not TaskStatus.COMPLETE and task.sets_choice and task.choice_id and task.choice_option:
                self.state.reset_choice(task.choice_id, task.choice_option)
            self.state.set_task_state(task_id, status)

    def set_manual_choice(self, choice_id: str, option_id: str | None) -> None:
        choice = self.content.choices[choice_id]
        if option_id is None:
            self.state.reset_choice(choice_id)
            return
        option = choice.options.get(option_id)
        if not option or not option.manual_resolution:
            raise ValueError(f"Choice option is not a manual resolution: {choice_id}/{option_id}")
        self.state.set_choice(choice_id, option_id)

    def set_access_condition(self, condition_id: str, satisfied: bool) -> None:
        if condition_id not in self.content.access_conditions:
            raise KeyError(condition_id)
        self.state.set_access_condition(condition_id, satisfied)

    def shout_progress(self, shout_id: str) -> tuple[int, int]:
        acquired = sum(
            credit.credit_count
            for credit in self.content.shout_credits.values()
            if credit.shout_id == shout_id
            and self.evaluate(credit.task_id).status is TaskStatus.COMPLETE
        )
        return min(acquired, 3), 3

    def shout_domain_progress(self) -> tuple[int, int]:
        return sum(self.shout_progress(item)[0] for item in self.content.shouts), 81

    def collectible_progress(self, collectible_id: str) -> tuple[int, int]:
        collectible = self.content.collectibles[collectible_id]
        credits_by_task = {
            credit.task_id: credit.credit_count
            for credit in self.content.collectible_credits.values()
            if credit.collectible_id == collectible_id
        }
        evaluations = {task_id: self.evaluate(task_id) for task_id in credits_by_task}
        acquired = sum(
            credits_by_task[task_id] for task_id, evaluation in evaluations.items()
            if evaluation.status is TaskStatus.COMPLETE
        )
        possible = sum(
            credits_by_task[task_id] for task_id, evaluation in evaluations.items()
            if evaluation.status is not TaskStatus.NOT_APPLICABLE
        )
        if acquired < collectible.required_credit_count and possible < collectible.required_credit_count:
            return acquired, 0
        return min(acquired, collectible.required_credit_count), collectible.required_credit_count

    def collectible_complete(self, collectible_id: str) -> bool:
        complete, required = self.collectible_progress(collectible_id)
        return required > 0 and complete >= required

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
            if evaluation.status in {TaskStatus.COMPLETE, TaskStatus.NOT_APPLICABLE, TaskStatus.LOCKED}:
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

    def story_progress(self, story_id: str) -> tuple[int, int]:
        collectible = next(
            (item for item in self.content.collectibles.values() if item.story_id == story_id), None
        )
        if collectible:
            complete, required = self.collectible_progress(collectible.id)
            if required == 0:
                return 0, 0
            return (1 if complete >= required else 0), 1
        task_ids = {
            membership.task_id for membership in self.content.memberships.values()
            if membership.story_id == story_id and membership.completion_role is CompletionRole.REQUIRED
        }
        evaluations = [self.evaluate(task_id) for task_id in task_ids]
        applicable = [item for item in evaluations if item.status is not TaskStatus.NOT_APPLICABLE]
        return sum(item.status is TaskStatus.COMPLETE for item in applicable), len(applicable)

    def collection_progress(self, collection_id: str) -> tuple[int, int]:
        shout = next(
            (item for item in self.content.shouts.values() if item.collection_id == collection_id),
            None,
        )
        if shout:
            return self.shout_progress(shout.id)
        collectibles = [
            item for item in self.content.collectibles.values()
            if item.collection_id == collection_id
        ]
        if collectibles:
            progress = [self.collectible_progress(item.id) for item in collectibles]
            applicable = [item for item in progress if item[1] > 0]
            return sum(item[0] >= item[1] for item in applicable), len(applicable)
        task_ids: set[str] = set()
        for membership in self.content.memberships.values():
            story = self.content.stories[membership.story_id]
            if story.collection_id != collection_id or membership.completion_role is not CompletionRole.REQUIRED:
                continue
            if story.classification is StoryClassification.OPTIONAL:
                continue
            if story.classification is StoryClassification.CONDITIONAL and self.story_progress(story.id)[1] == 0:
                continue
            task_ids.add(membership.task_id)
        evaluations = [self.evaluate(task_id) for task_id in task_ids]
        applicable = [item for item in evaluations if item.status is not TaskStatus.NOT_APPLICABLE]
        return sum(item.status is TaskStatus.COMPLETE for item in applicable), len(applicable)

    def domain_progress(self, domain_id: str) -> tuple[int, int]:
        if domain_id == "shouts":
            return self.shout_domain_progress()
        collectible_collections = {
            item.collection_id for item in self.content.collectibles.values()
            if self.content.collections[item.collection_id].domain_id == domain_id
        }
        task_ids: set[str] = set()
        for membership in self.content.memberships.values():
            story = self.content.stories[membership.story_id]
            collection = self.content.collections[story.collection_id]
            if collection.domain_id != domain_id or membership.completion_role is not CompletionRole.REQUIRED:
                continue
            if collection.id in collectible_collections:
                continue
            if story.classification is StoryClassification.OPTIONAL:
                continue
            if story.classification is StoryClassification.CONDITIONAL and self.story_progress(story.id)[1] == 0:
                continue
            task_ids.add(membership.task_id)
        evaluations = [self.evaluate(task_id) for task_id in task_ids]
        applicable = [item for item in evaluations if item.status is not TaskStatus.NOT_APPLICABLE]
        collectible_items = [
            item for item in self.content.collectibles.values()
            if item.collection_id in collectible_collections
        ]
        collectible_progress = [self.collectible_progress(item.id) for item in collectible_items]
        applicable_collectibles = [item for item in collectible_progress if item[1] > 0]
        return (
            sum(item.status is TaskStatus.COMPLETE for item in applicable)
            + sum(item[0] >= item[1] for item in applicable_collectibles),
            len(applicable) + len(applicable_collectibles),
        )

    def overall_completion(self) -> tuple[int, int]:
        """Return unique completed Tasks and unique total Tasks, never membership counts."""
        evaluations = [self.evaluate(task_id) for task_id in self.content.tasks]
        applicable = [item for item in evaluations if item.status is not TaskStatus.NOT_APPLICABLE]
        completed = sum(item.status is TaskStatus.COMPLETE for item in applicable)
        return completed, len(applicable)
