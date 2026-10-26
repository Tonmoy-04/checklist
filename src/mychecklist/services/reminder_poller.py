"""Main-thread reminder polling coordinator."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ReminderPoller:
    """Use Tk's scheduler so reminder work never touches widgets off-thread."""

    def __init__(self, scheduler: Any, process: Callable[[], int], *,
                 interval_ms: int = 20_000, on_error: Callable[[str], None] | None = None) -> None:
        self.scheduler = scheduler
        self.process = process
        self.interval_ms = interval_ms
        self.on_error = on_error or (lambda message: None)
        self._after_id: Any = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._schedule()

    def stop(self) -> None:
        self._running = False
        if self._after_id is not None:
            self.scheduler.after_cancel(self._after_id)
            self._after_id = None

    def _schedule(self) -> None:
        if self._running:
            self._after_id = self.scheduler.after(self.interval_ms, self._tick)

    def _tick(self) -> None:
        self._after_id = None
        if not self._running:
            return
        try:
            self.process()
        except Exception as error:
            self.on_error(str(error))
        finally:
            self._schedule()
