# app/models/notification_model.py

from pydantic import BaseModel, Field


class courseNotificationAddRequest(BaseModel):
    course_code: str
    sender_id: str
    title: str
    message: str

class oneRecipientNotificationAddRequest(BaseModel):
    course_code: str
    recipient_id: str
    sender_id: str
    title: str
    message: str
