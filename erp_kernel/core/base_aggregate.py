from typing import List, Type
from uuid import UUID
from .base_event import BaseEvent

class AggregateRoot:
    """
    Base class for Event-Sourced Aggregates.
    State is modified ONLY by applying events.
    """
    def __init__(self, id: UUID):
        self.id = id
        self._version = 0
        self._changes: List[BaseEvent] = []

    def load_from_history(self, events: List[BaseEvent]):
        """Rehydrates the aggregate from a stream of past events."""
        for event in events:
            self.apply(event, is_new=False)

    def apply(self, event: BaseEvent, is_new: bool = True):
        """
        Applies a state change.
        1. Routes the event to the appropriate handlers (e.g., _on_stock_moved).
        2. If is_new=True, adds it to pending changes to be saved/published.
        """
        method_name = f"_on_{event.event_type.lower()}"
        handler = getattr(self, method_name, None)
        
        if handler:
            handler(event)
        
        if is_new:
            self._changes.append(event)
        
        self._version += 1

    @property
    def unsaved_events(self) -> List[BaseEvent]:
        """Events that occurred in this transaction but haven't been persisted."""
        return list(self._changes)

    def clear_changes(self):
        """Called after successful persistence."""
        self._changes.clear()
