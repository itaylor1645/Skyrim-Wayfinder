from skyrim_wayfinder.domain import TaskStatus


def test_completed_preparation_unlocks_target(service):
    assert service.evaluate("riften_deliver_fire_salts").status is TaskStatus.LOCKED
    service.set_task_state("prep_riften_fire_salts", TaskStatus.COMPLETE)
    assert service.evaluate("riften_deliver_fire_salts").status is TaskStatus.LOCKED
    service.set_task_state("riften_stoking_flames_start", TaskStatus.COMPLETE)
    assert service.evaluate("riften_deliver_fire_salts").status is TaskStatus.AVAILABLE


def test_completed_target_hides_obsolete_preparation(service):
    service.set_task_state("prep_riften_fire_salts", TaskStatus.COMPLETE)
    service.set_task_state("riften_deliver_fire_salts", TaskStatus.COMPLETE)
    assert "prep_riften_fire_salts" not in {
        evaluation.task.id for evaluation in service.outstanding_preparations()
    }


def test_invalidated_target_hides_obsolete_preparation(service):
    service.set_task_state("riften_deliver_fire_salts", TaskStatus.NOT_APPLICABLE)
    assert "prep_riften_fire_salts" not in {
        evaluation.task.id for evaluation in service.outstanding_preparations()
    }
