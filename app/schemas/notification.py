from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class NotificationData(BaseModel):
    subject: Optional[str] = "Notification"
    content: str

class NotificationRequest(BaseModel):
    notification: NotificationData
    user_ids: Optional[List[UUID]] = None
