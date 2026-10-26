from mychecklist.ui.main_window import ROUTES
from mychecklist.theme import WINDOW


def test_main_window_contract_defines_all_documented_routes_and_dimensions() -> None:
    assert [route for route, _ in ROUTES] == [
        "today", "upcoming", "overdue", "all", "completed", "statistics", "settings"
    ]
    assert WINDOW["default_width"] == 1100
    assert WINDOW["default_height"] == 720
    assert WINDOW["minimum_width"] == 850
    assert WINDOW["minimum_height"] == 580
    assert WINDOW["sidebar_width"] == 210
