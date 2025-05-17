from pydantic import BaseModel, Field, validator
from typing import Literal
import datetime

# Allowed departments (full names only)
ALLOWED_DEPARTMENTS = [
    "Computer Science and Engineering",
    "Electronics and Telecommunication Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Materials Science and Engineering",
    "Chemical and process engineering",
    "Biomedical Engineering",
    "Information Technology",
    "Artificial Intelligence",
    "Medicine",
    "Architecture",
]

# Allowed days
DAYS_OF_WEEK = Literal[
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]

class AddCourseRequestModel(BaseModel):
    course_code: str
    course_name: str
    course_description: str
    year: int = Field(..., ge=1, le=5)
    semester: int = Field(..., ge=1, le=2)
    department: str
    credits: float
    day_of_week: DAYS_OF_WEEK
    start_time: datetime.time
    lecturer_reg_numbers: list[str]

    @validator('department')
    def validate_department(cls, v):
        if v not in ALLOWED_DEPARTMENTS:
            raise ValueError(f"Department '{v}' is not valid. Must be one of {ALLOWED_DEPARTMENTS}")
        return v

    @validator('credits')
    def validate_credits(cls, v):
        if (v * 10) % 5 != 0:
            raise ValueError("Credits must be a multiple of 0.5")
        return v
