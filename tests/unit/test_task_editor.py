from mychecklist.ui.dialogs.task_editor import TaskEditorDialog


class Widget:
    def __init__(self, *args, **kwargs):
        self.value = ""
        self.destroyed = False

    def grid(self, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def insert(self, index, value): self.value = value
    def get(self): return self.value
    def set(self, value): self.value = value
    def focus_set(self): pass
    def configure(self, **kwargs): pass
    def grab_set(self): pass
    def grab_release(self): pass
    def destroy(self): self.destroyed = True
    def transient(self, parent): pass
    def protocol(self, name, callback): self.protocol_callback = callback
    def title(self, value): self.window_title = value
    def geometry(self, value): self.window_geometry = value
    def minsize(self, width, height): self.minimum = (width, height)


class FakeCtk:
    CTkToplevel = Widget
    CTkLabel = Widget
    CTkEntry = Widget
    CTkComboBox = Widget
    CTkButton = Widget


def test_task_editor_validates_and_saves_normalized_values():
    saved = []
    dialog = TaskEditorDialog(
        Widget(), FakeCtk, categories={1: "Personal"}, on_save=saved.append,
        initial={"title": "Task", "due_date": "2026-10-27", "category_id": 1},
    )

    assert dialog.save() is True
    assert saved[0].title == "Task"
    assert saved[0].category_id == 1
    assert dialog.dialog.destroyed


def test_task_editor_keeps_invalid_form_open_and_confirms_dirty_cancel():
    errors = []
    dialog = TaskEditorDialog(Widget(), FakeCtk, categories={1: "Personal"}, on_save=lambda value: None,
                              show_error=errors.append, confirm_discard=lambda: False)
    dialog._entries["title"].value = " "
    assert dialog.save() is False
    assert errors and not dialog.dialog.destroyed
    dialog._entries["title"].value = "Changed"
    assert dialog.cancel() is False
    assert not dialog.dialog.destroyed


def test_task_editor_keeps_form_open_when_persistence_callback_fails():
    errors = []
    dialog = TaskEditorDialog(
        Widget(), FakeCtk, categories={1: "Personal"},
        on_save=lambda value: (_ for _ in ()).throw(RuntimeError("database unavailable")),
        show_error=errors.append,
        initial={"title": "Existing task", "category_id": 1},
    )

    assert dialog.save() is False
    assert errors == ["database unavailable"]
    assert not dialog.dialog.destroyed


def test_task_editor_create_mode_can_have_a_default_category():
    saved = []
    dialog = TaskEditorDialog(
        Widget(), FakeCtk, categories={1: "Personal"}, on_save=saved.append,
        initial={"title": "New task", "category_id": 1},
    )

    assert dialog.dialog.window_title == "Add Task"
    assert dialog.save() is True
    assert saved[0].category_id == 1
