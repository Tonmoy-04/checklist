from mychecklist.theme import DARK_COLORS, FONTS, LIGHT_COLORS, SPACING, WINDOW, colors, configure_customtkinter


def test_dark_theme_tokens_match_ui_spec() -> None:
    assert DARK_COLORS["bg.canvas"] == "#111318"
    assert DARK_COLORS["accent.primary"] == "#6D8DFF"
    assert DARK_COLORS["priority.high"] == "#F16C75"
    assert SPACING == {
        "space.1": 4, "space.2": 8, "space.3": 12, "space.4": 16,
        "space.5": 24, "space.6": 32, "space.7": 40,
    }
    assert WINDOW["default_width"] == 1100
    assert WINDOW["default_height"] == 720
    assert WINDOW["minimum_width"] == 850
    assert WINDOW["minimum_height"] == 580
    assert FONTS["display"] == ("Segoe UI", 28, "bold")


def test_theme_selection_returns_copies_and_rejects_unknown_theme() -> None:
    selected = colors()
    selected["bg.canvas"] = "changed"
    assert DARK_COLORS["bg.canvas"] == "#111318"
    assert colors("light")["bg.canvas"] == "#F5F7FA"
    try:
        colors("unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown theme was accepted")


def test_configure_customtkinter_uses_dark_defaults() -> None:
    class FakeCustomTkinter:
        def __init__(self) -> None:
            self.calls = []

        def set_appearance_mode(self, value: str) -> None:
            self.calls.append(("appearance", value))

        def set_default_color_theme(self, value: str) -> None:
            self.calls.append(("color", value))

    fake = FakeCustomTkinter()
    assert configure_customtkinter(fake) is fake
    assert fake.calls == [("appearance", "dark"), ("color", "dark-blue")]
