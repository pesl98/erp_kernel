from fastapi import APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/system", tags=["system"])

class ToolSchema(BaseModel):
    name: str
    description: str
    schema_def: Dict[str, str]

class SystemCapabilities(BaseModel):
    modules: List[str]
    tools: List[ToolSchema]

@router.get("/capabilities", response_model=SystemCapabilities)
async def get_capabilities():
    """
    Reflective endpoint allowing AI Agents to learn the system's current capabilities.
    """
    return SystemCapabilities(
        modules=["inventory"],
        tools=[
            ToolSchema(
                name="receive_goods",
                description="Increases stock quantity based on a physical receipt.",
                schema_def={"sku": "str", "qty": "int", "bin_location": "str", "tenant_id": "str"}
            )
        ]
    )
