from sqlalchemy.orm import Session
from erp_kernel.core.base_event import BaseEvent
from erp_kernel.infrastructure.persistence.database import ExpectedInboundModel, SessionLocal

# Note: Handlers often need access to the DB.
# In a rigorous architecture, this would go through a Port/Service.
# For pragmatism in this phase, we write directly to the Projection Model (Infrastructure concern).

async def handle_po_issued(event: BaseEvent):
    """
    Reacts to POIssued. 
    Notes expected inbound stock so the warehouse can accept it.
    """
    # Defensive programming: ensure we only handle what we expect
    if event.event_type != "POIssued":
        return

    # In a real app, payload might differ from direct event attributes 
    # depending on serialization. BaseEvent in this codebase is Pydantic, 
    # so we access attrs directly if it was passed as object, or dict if loaded.
    # Assuming the EventBus passes the Pydantic model.
    
    # However, POIssued specific fields are on the child class. 
    # We rely on the fact that the object passed has these fields.
    
    # If the bus rehydrates events, they are objects.
    
    db = SessionLocal()
    try:
        # Event is usually passed as Pydantic model by internal bus, 
        # or dict if from external key. Based on our architecture, it's the Pydantic obj.
        
        # We access fields directly assuming it matches POIssued schema
        # Since BaseEvent annotation is generic, we might need casting or dynamic access.
        
        # NOTE: In a strict event bus, we'd deserialize to POIssued. 
        # Here we trust the 'lines' attr exists because we just added it.
        
        lines = getattr(event, 'lines', [])
        po_id = str(getattr(event, 'po_id'))
        tenant_id = event.tenant_id
        
        for line in lines:
            # Create Expectation
            expectation = ExpectedInboundModel(
                po_id=po_id,
                sku=line['sku'],
                qty_ordered=line['qty'],
                qty_received=0,
                tenant_id=tenant_id
            )
            db.add(expectation)
        
        db.commit()
    except Exception as e:
        db.rollback()
        # In strict sys, we'd log this error or dead-letter queue it.
        print(f"ERROR handling POIssued: {e}")
    finally:
        db.close()
