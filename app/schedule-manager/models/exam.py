from pydantic import BaseModel
from uuid import UUID
from datetime import date, time
from typing import Optional

class ExamCreateRequest(BaseModel):
    title: str
    start_time: time
    end_time: time
    course_code: str
    exam_date: date
    notified: bool = False 
    description: str
    location: str
    scheduled_by: UUID
    course_code: str


class ExamUpdateRequest(BaseModel):
    title: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    exam_date: Optional[date] = None
    notified: Optional[bool] = None
    description: Optional[str] = None
    location: Optional[str] = None
    scheduled_by: Optional[UUID] = None
    course_code: Optional[str] = None