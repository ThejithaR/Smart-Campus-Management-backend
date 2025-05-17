from pydantic import BaseModel
from uuid import UUID
from datetime import date, time
from typing import Optional

class AssignmentCreateRequest(BaseModel):
    title: str
    course_code: str
    assigned_by: UUID
    description: str
    attachment_url: Optional[str] = None
    notified: bool = False
    due_date: date
    due_time: time

class AssignmentUpdateRequest(BaseModel):
    title: Optional[str] = None
    course_code: Optional[str] = None
    assigned_by: Optional[UUID] = None
    description: Optional[str] = None
    attachment_url: Optional[str] = None
    notified: Optional[bool] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
