from mychecklist.ui.views.task_list import TaskListView


class Widget:
    def __init__(self, *args, **kwargs):
        self.children = []
        self.kwargs = kwargs
        self.value = ""
        self.commands = []
        self.grid_calls = []

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)

    def grid_columnconfigure(self, *args, **kwargs):
        pass

    def grid_rowconfigure(self, *args, **kwargs):
        pass

    def winfo_children(self):
        return self.children

    def destroy(self):
        pass

    def bind(self, event, command):
        self.commands.append((event, command))

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def delete(self, *args):
        self.value = ""


class FakeCtk:
    CTkFrame = Widget
    CTkScrollableFrame = Widget
    CTkLabel = Widget
    CTkEntry = Widget
    CTkComboBox = Widget
    CTkButton = Widget


class Repository:
    def list_for_view(self, view, today, now):
        return []


def test_task_list_exposes_add_task_and_keyboard_callback():
    refresh_callbacks = []
    view = TaskListView(
        Widget(), FakeCtk, view="today", repository=Repository(),
        task_service=object(), category_names={1: "Personal"},
        today=lambda: __import__("datetime").date(2026, 10, 27),
        on_edit=lambda row: None, confirm_delete=lambda: True,
        on_error=lambda message: None,
        on_add_task=refresh_callbacks.append,
    )

    assert view.add_button.kwargs["text"] == "+ Add Task"
    view.add_button.kwargs["command"]()
    assert refresh_callbacks == [view.refresh]
    assert ("<Control-n>", view.container.commands[0][1]) in view.container.commands
    assert view.search_entry.grid_calls[0]["row"] == 0
    assert view.category_combo.grid_calls[0]["row"] == 1
    assert view.priority_combo.grid_calls[0]["row"] == 1
    assert view.sort_combo.grid_calls[0]["row"] == 1
    assert view.clear_button.grid_calls[0]["row"] == 1
