from pydantic import BaseModel, Field
from typing import Literal

class TicketResult(BaseModel):
    category:Literal["Billing", "Technical Support", "Account Access", "Cancellation"]
    urgency:int = Field(ge=1,le=5)
    requires_human_escalation:bool