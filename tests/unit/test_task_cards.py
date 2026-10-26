from mychecklist.ui.widgets.task_cards import TaskCard


class Widget:
    def __init__(self, *args, **kwargs):
        self.value = 0
        self.destroyed = False
        self.kwargs = kwargs

    def grid(self, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def select(self): self.value = 1
    def deselect(self): self.value = 0
    def destroy(self): self.destroyed = True


class FakeCtk:
    CTkFrame = Widget
    CTkCheckBox = Widget
    CTkLabel = Widget
    CTkButton = Widget


class Service:
    def __init__(self): self.calls = []
    def complete(self, occurrence_id): self.calls.append(("complete", occurrence_id))
    def reopen(self, occurrence_id): self.calls.append(("reopen", occurrence_id))
    def cancel_occurrence(self, occurrence_id): self.calls.append(("cancel", occurrence_id))


def row(status="open"):
    return {
        "id": 9, "title": "Study", "category_id": 1, "priority": "high",
        "due_date": "2026-10-27", "due_time": "09:00", "status": status,
    }


def test_task_card_completes_and_refreshes():
    service = Service()
    refreshed = []
    card = TaskCard(
        Widget(), FakeCtk, row(), service, category_names={1: "University"},
        on_edit=lambda value: None, confirm_delete=lambda: True,
        on_refresh=lambda: refreshed.append(True), on_error=lambda value: None,
    )
    card.toggle_completion()
    assert service.calls == [("complete", 9)]
    assert refreshed == [True]


def test_task_card_reopens_and_delete_requires_confirmation():
    service = Service()
    refreshed = []
    confirmations = []
    card = TaskCard(
        Widget(), FakeCtk, row("completed"), service, category_names={1: "University"},
        on_edit=lambda value: None, confirm_delete=lambda: confirmations.append(True) or False,
        on_refresh=lambda: refreshed.append(True), on_error=lambda value: None,
    )
    card.toggle_completion()
    card.delete()
    assert service.calls == [("reopen", 9)]
    assert confirmations == [True]
    assert refreshed == [True]


def test_task_card_list_refresh_callback_can_reload_the_owner_view():
    from mychecklist.ui.widgets.task_cards import TaskCardList

    refreshed = []
    rows = [row()]
    cards = TaskCardList(
        Widget(), FakeCtk, row_loader=lambda: rows, task_service=Service(),
        category_names={1: "University"}, on_edit=lambda value: None,
        confirm_delete=lambda: True, on_error=lambda value: None,
        on_refresh=lambda: refreshed.append(True),
    )
    cards.refresh()
    cards.cards[0].on_refresh()
    assert refreshed == [True]
