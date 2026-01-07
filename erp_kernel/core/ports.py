from abc import ABC, abstractmethod
from typing import List, Callable, Awaitable
from uuid import UUID
from .base_event import BaseEvent

class EventStore(ABC):
    """
    Port for persisting events.
    """
    @abstractmethod
    async def save(self, events: List[BaseEvent]) -> None:
        """Append events to the log."""
        pass

    @abstractmethod
    async def load_stream(self, stream_id: UUID) -> List[BaseEvent]:
        """Load all events for a specific aggregate ID."""
        pass

class EventBus(ABC):
    """
    Port for publishing events to subscribers.
    """
    @abstractmethod
    async def publish(self, events: List[BaseEvent]) -> None:
        """Broadcast events to all listeners."""
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> None:
        """Register a handler for a specific event type."""
        pass
