from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class CheckpointAdvanceRequest(BaseModel):
    watchlist_id: str
    device_id: str = "default"
    trigger_event: str = "manual_ack"


class CheckpointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    watchlist_id: str
    device_id: str
    checkpoint_time: datetime
    snapshot_data: Dict[str, Any]
    trigger_event: str
    created_at: datetime
    elapsed_seconds: Optional[int] = None
    human_elapsed: Optional[str] = None
