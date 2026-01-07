from typing import Any, Dict, Optional
from datetime import datetime, timezone
from uuid import uuid4, UUID
from pydantic import BaseModel, Field

class BaseEvent(BaseModel):
    """
    The atom of truth.
    All business actions MUST be captured as immutable events.
    """
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str = Field(..., description="Multi-tenancy isolation is mandatory")
    version: int = 1
    
    class Config:
        frozen = True  # Immutability

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return self.model_dump_json()
