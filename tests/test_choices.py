import pytest

from skyrim_wayfinder.domain import TaskStatus
from skyrim_wayfinder.services import ChoiceConfirmationRequired


def unlock_shack(service):
    service.set_task_state("db_innocence_lost_speak_aventus", TaskStatus.COMPLETE)
    service.set_task_state("db_innocence_lost_kill_grelod", TaskStatus.COMPLETE)
    service.set_task_state("db_innocence_lost_report_aventus", TaskStatus.COMPLETE)
    service.set_task_state("db_trigger_abduction_sleep", TaskStatus.COMPLETE)


def test_choice_requires_confirmation_and_excludes_opposing_path(service):
    unlock_shack(service)
    with pytest.raises(ChoiceConfirmationRequired):
        service.set_task_state("db_join_at_shack", TaskStatus.COMPLETE)
    service.set_task_state("db_join_at_shack", TaskStatus.COMPLETE, confirm_choice=True)
    opposing = service.evaluate("db_destroy_at_shack")
    assert opposing.status is TaskStatus.NOT_APPLICABLE
    assert opposing.derived_exclusion


def test_choice_reversal_restores_prior_manual_state(service):
    unlock_shack(service)
    service.set_task_state("db_destroy_at_shack", TaskStatus.DEFERRED)
    service.set_task_state("db_join_at_shack", TaskStatus.COMPLETE, confirm_choice=True)
    masked = service.evaluate("db_destroy_at_shack")
    assert masked.status is TaskStatus.NOT_APPLICABLE
    assert masked.stored_state is TaskStatus.DEFERRED
    service.set_task_state("db_join_at_shack", None)
    restored = service.evaluate("db_destroy_at_shack")
    assert restored.status is TaskStatus.DEFERRED


def test_correcting_completed_choice_to_noncomplete_reopens_path(service):
    unlock_shack(service)
    service.set_task_state("db_join_at_shack", TaskStatus.COMPLETE, confirm_choice=True)
    service.set_task_state("db_join_at_shack", TaskStatus.BLOCKED)
    assert service.state.get_choice("dark_brotherhood_path") is None
    assert service.evaluate("db_destroy_at_shack").status is TaskStatus.AVAILABLE


def test_manual_not_applicable_is_independent_escape_hatch(service):
    service.set_task_state("college_gain_admission", TaskStatus.COMPLETE)
    service.set_task_state("college_first_lessons", TaskStatus.NOT_APPLICABLE)
    assert service.evaluate("college_first_lessons").status is TaskStatus.NOT_APPLICABLE
    service.set_task_state("college_first_lessons", None)
    assert service.evaluate("college_first_lessons").status is TaskStatus.AVAILABLE
