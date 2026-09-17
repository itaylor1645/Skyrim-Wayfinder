from skyrim_wayfinder.domain import TaskStatus


def planner_task_ids(service, region_id):
    return {evaluation.task.id for item in service.regional_plan(region_id) for evaluation in item.tasks}


def test_locked_task_not_in_regional_recommendations(service):
    assert service.evaluate("college_staff_magnus").status is TaskStatus.LOCKED
    assert "college_staff_magnus" not in planner_task_ids(service, "labyrinthian")


def test_completing_prerequisite_makes_dependent_available(service):
    assert service.evaluate("mq_before_storm_reach_riverwood").status is TaskStatus.LOCKED
    service.set_task_state("mq_unbound_escape_helgen", TaskStatus.COMPLETE)
    assert service.evaluate("mq_before_storm_reach_riverwood").status is TaskStatus.AVAILABLE


def test_deferred_task_not_recommended(service):
    task_id = "collectible_golden_claw_recover"
    assert task_id in planner_task_ids(service, "whiterun")
    service.set_task_state(task_id, TaskStatus.DEFERRED)
    assert task_id not in planner_task_ids(service, "whiterun")


def test_blocked_task_not_recommended(service):
    task_id = "college_first_lessons"
    service.set_task_state("college_gain_admission", TaskStatus.COMPLETE)
    assert task_id in planner_task_ids(service, "winterhold")
    service.set_task_state(task_id, TaskStatus.BLOCKED)
    assert task_id not in planner_task_ids(service, "winterhold")


def test_minimum_level_rule(service):
    task_id = "daedric_break_of_dawn_beacon"
    assert service.evaluate(task_id).status is TaskStatus.LOCKED
    service.state.player_level = 12
    assert service.evaluate(task_id).status is TaskStatus.AVAILABLE


def test_available_and_locked_cannot_be_assigned(service):
    for status in (TaskStatus.AVAILABLE, TaskStatus.LOCKED):
        try:
            service.set_task_state("college_first_lessons", status)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected {status} assignment to fail")


def test_corrected_representative_prerequisites(service):
    assert service.evaluate("db_innocence_lost_kill_grelod").status is TaskStatus.LOCKED
    service.set_task_state("db_innocence_lost_speak_aventus", TaskStatus.COMPLETE)
    assert service.evaluate("db_innocence_lost_kill_grelod").status is TaskStatus.AVAILABLE

    assert service.evaluate("college_first_lessons").status is TaskStatus.LOCKED
    service.set_task_state("college_gain_admission", TaskStatus.COMPLETE)
    assert service.evaluate("college_first_lessons").status is TaskStatus.AVAILABLE


def test_dragon_rising_report_gates_follow_on_work(service):
    service.set_task_state("mq_dragon_rising_watchtower", TaskStatus.COMPLETE)
    assert service.evaluate("house_breezehome_purchase").status is TaskStatus.LOCKED
    assert service.evaluate("mq_way_voice_high_hrothgar").status is TaskStatus.LOCKED
    service.set_task_state("hold_whiterun_thane", TaskStatus.COMPLETE)
    assert service.evaluate("house_breezehome_purchase").status is TaskStatus.AVAILABLE
    assert service.evaluate("mq_way_voice_high_hrothgar").status is TaskStatus.AVAILABLE
