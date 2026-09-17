from skyrim_wayfinder.domain import PlannerBehavior, RegionType, TaskStatus


def test_location_card_aggregates_multiple_domains(service):
    item = next(item for item in service.regional_plan("whiterun") if item.id == "bleak_falls_barrow")
    task_ids = {evaluation.task.id for evaluation in item.tasks}
    assert "collectible_golden_claw_recover" in task_ids
    assert "shout_unrelenting_force_bleak_falls" in task_ids
    assert {"artifacts_collectibles", "shouts"} <= set(item.domain_ids)


def test_tasks_at_different_locations_do_not_group_by_story(service):
    items = service.regional_plan("whiterun")
    by_id = {item.id: {entry.task.id for entry in item.tasks} for item in items}
    assert "mq_bleak_falls_accept" not in by_id.get("dragonsreach", set())  # locked initially
    assert "mq_bleak_falls_dragonstone" not in by_id.get("dragonsreach", set())
    assert "collectible_golden_claw_recover" in by_id["bleak_falls_barrow"]


def test_multi_membership_task_is_one_canonical_object_and_state(service):
    task_id = "mask_morokei"
    assert len(service.memberships_for_task(task_id)) == 2
    assert set(service.domain_ids_for_task(task_id)) == {"artifacts_collectibles", "factions_major"}
    service.set_task_state(task_id, TaskStatus.COMPLETE)
    appearances = [
        evaluation for collections in service.explorer_tree().values()
        for stories in collections.values() for entries in stories.values()
        for _membership, evaluation in entries if evaluation.task.id == task_id
    ]
    assert len(appearances) == 2
    assert all(item.status is TaskStatus.COMPLETE for item in appearances)
    assert service.state.all_task_states() == {task_id: TaskStatus.COMPLETE}


def test_missable_metadata_reaches_service_layer(service):
    for task_id in (
        "mq_unbound_escape_helgen", "mq_before_storm_reach_riverwood",
        "mq_before_storm_go_whiterun", "mq_bleak_falls_accept",
        "mq_bleak_falls_dragonstone", "mq_bleak_falls_return_dragonstone",
        "mq_dragon_rising_watchtower", "mq_way_voice_high_hrothgar",
        "mq_the_fallen_milestone",
    ):
        service.set_task_state(task_id, TaskStatus.COMPLETE)
    skuldafn = next(item for item in service.regional_plan("skuldafn") if item.id == "skuldafn")
    assert skuldafn.location.one_way
    assert "MISSABLE" in skuldafn.warning_text
    assert any(evaluation.task.missable for evaluation in skuldafn.tasks)


def test_explorer_keeps_all_behavior_types(service):
    service.set_task_state("college_first_lessons", TaskStatus.COMPLETE)
    evaluations = [
        evaluation for collections in service.explorer_tree().values()
        for stories in collections.values() for entries in stories.values()
        for _membership, evaluation in entries
    ]
    by_id = {evaluation.task.id: evaluation for evaluation in evaluations}
    assert by_id["college_first_lessons"].status is TaskStatus.COMPLETE
    assert by_id["college_staff_magnus"].status is TaskStatus.LOCKED
    assert by_id["daedric_break_of_dawn_beacon"].task.planner_behavior is PlannerBehavior.OPPORTUNISTIC
    assert by_id["mq_the_fallen_milestone"].task.planner_behavior is PlannerBehavior.MILESTONE


def test_opportunistic_and_milestone_tasks_are_not_planner_actions(service):
    service.state.player_level = 12
    assert service.global_actions() == []
    all_regional = {
        entry.task.id for region in service.content.regions
        for item in service.regional_plan(region) for entry in item.tasks
    }
    assert "daedric_break_of_dawn_beacon" not in all_regional
    assert "mq_the_fallen_milestone" not in all_regional


def test_overall_completion_deduplicates_memberships(service):
    service.set_task_state("mask_morokei", TaskStatus.COMPLETE)
    complete, total = service.overall_completion()
    assert complete == 1
    assert total == len(service.content.tasks)


def test_expanded_catalog_does_not_expand_operational_selector(service):
    operational = service.operational_regions()
    visible_ids = {region.id for regions in operational.values() for region in regions}
    assert "markarth" not in visible_ids  # catalog Locations alone do not make a selector entry
    assert "blackreach" not in visible_ids
    assert "solstheim_raven_rock" not in visible_ids
    assert "whiterun" in {region.id for region in operational[RegionType.CITY]}
