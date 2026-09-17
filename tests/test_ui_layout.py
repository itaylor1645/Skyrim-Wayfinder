from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QTreeWidgetItem

from skyrim_wayfinder.app import build_service
from skyrim_wayfinder.domain import TaskStatus
from skyrim_wayfinder.ui import MainWindow


def test_preparation_sidebar_collapses_before_planner_becomes_too_narrow(tmp_path):
    application = QApplication.instance() or QApplication([])
    service = build_service(tmp_path / "ui.sqlite3")
    window = MainWindow(service)
    window.resize(920, 700)
    window.show()
    application.processEvents()
    assert not window.planner.sidebar.isVisible()
    assert window.planner.left_scroll.width() >= window.planner.MIN_PLANNER_WIDTH

    window.resize(1200, 700)
    application.processEvents()
    assert window.planner.sidebar.isVisible()
    assert window.planner.left_scroll.width() >= window.planner.MIN_PLANNER_WIDTH
    window.close()
    service.state.close()


def test_task_explorer_uses_approved_columns(tmp_path):
    application = QApplication.instance() or QApplication([])
    service = build_service(tmp_path / "explorer.sqlite3")
    window = MainWindow(service)
    headers = [window.explorer.tree.headerItem().text(index) for index in range(4)]
    assert headers == ["Objective", "Status", "Region", "Location"]
    window.close()
    service.state.close()


def _task_ids(item: QTreeWidgetItem) -> set[str]:
    result = set()
    task_id = item.data(0, Qt.ItemDataRole.UserRole)
    if task_id:
        result.add(task_id)
    for index in range(item.childCount()):
        result.update(_task_ids(item.child(index)))
    return result


def _visible_task_ids(window: MainWindow) -> set[str]:
    return {
        task_id
        for index in range(window.explorer.tree.topLevelItemCount())
        for task_id in _task_ids(window.explorer.tree.topLevelItem(index))
    }


def test_explorer_hides_completed_memberships_and_persists_filter(tmp_path):
    application = QApplication.instance() or QApplication([])
    service = build_service(tmp_path / "explorer-filter.sqlite3")
    service.set_task_state("mask_morokei", TaskStatus.COMPLETE)
    window = MainWindow(service)
    assert window.explorer.hide_completed.isChecked()
    assert "mask_morokei" not in _visible_task_ids(window)
    window.explorer.hide_completed.setChecked(False)
    application.processEvents()
    assert "mask_morokei" in _visible_task_ids(window)
    assert service.state.get_setting("hide_completed_objectives") == "0"
    window.close()
    service.state.close()


def test_region_selector_groups_and_gates_special_destinations(tmp_path):
    application = QApplication.instance() or QApplication([])
    service = build_service(tmp_path / "regions.sqlite3")
    window = MainWindow(service)
    labels = [window.planner.region.itemText(index).strip() for index in range(window.planner.region.count())]
    assert "City Regions" in labels
    assert "Expeditions" not in labels
    assert "Skuldafn" not in labels
    service.set_task_state("hold_whiterun_thane", TaskStatus.COMPLETE)
    window.planner.refresh()
    labels = [window.planner.region.itemText(index).strip() for index in range(window.planner.region.count())]
    assert "Expeditions" in labels
    assert "High Hrothgar / Throat of the World" in labels
    service.set_task_state("mq_the_fallen_milestone", TaskStatus.COMPLETE)
    window.planner.refresh()
    labels = [window.planner.region.itemText(index).strip() for index in range(window.planner.region.count())]
    assert "Special Destinations" in labels
    assert "Skuldafn" in labels
    assert service.content.regions["skuldafn"].departure_location_id == "dragonsreach"
    window.close()
    service.state.close()


def test_planner_cards_use_dominant_domain_tint(tmp_path):
    application = QApplication.instance() or QApplication([])
    service = build_service(tmp_path / "tint.sqlite3")
    service.state.current_region = "whiterun"
    window = MainWindow(service)
    cards = [frame for frame in window.planner.findChildren(QFrame) if frame.objectName() == "card"]
    assert cards
    assert all("background-color" in card.styleSheet() for card in cards)
    window.close()
    service.state.close()
