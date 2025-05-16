import pandas as pd
from datetime import datetime, time
import datetime
from fastapi import HTTPException
import json
import time
from uuid import UUID
from database import supabase
from postgrest.exceptions import APIError
from dateutil.parser import parse

def serialize_exam_data(data: dict) -> dict:
    """
    Convert time, date, and UUID objects to serializable formats.
    """
    for key, value in data.items():
        # If the value is a time object
        if isinstance(value, datetime.time):
            # Convert time object to a string (ISO format)
            data[key] = value.isoformat()
        
        # If the value is a date object
        elif isinstance(value, datetime.date):
            # Convert date object to a string (ISO format)
            data[key] = value.isoformat()
        
        # If the value is a UUID object
        elif isinstance(value, UUID):
            data[key] = str(value)  # Convert UUID to string
    
    return data

def to_timestamp(value):
    print("Value type:", type(value))

    # If it's already a pandas Timestamp, return the time portion, removing any timezone info
    if isinstance(value, pd.Timestamp):
        return value.tz_localize(None).time()  # Strip timezone and return only the time part

    # If it's a string
    if isinstance(value, str):
        if len(value) <= 8:  # Just a time like "06:08:42"
            value = f"1970-01-01T{value}"
        # Convert to datetime, remove timezone info, then return the time part
        return pd.to_datetime(value.replace("Z", "+00:00")).tz_localize(None).time()

    # If it's a datetime.time object, just return it (naive)
    if isinstance(value, datetime.time):
        return value

    # If it's a datetime.datetime object, remove the timezone and return the time portion
    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=None).time()

    return None


def check_exam_clash(course_code: str, exam_date: str, start_time: str, end_time: str):
    print("Checking clashes for:", exam_date)
    
    # Fetch all exams on the given exam_date
    response = supabase.table("Exams").select("*").eq("exam_date", exam_date).execute()
    exams = response.data
    print("Exams on same day:", exams)

    if not exams:
        return False

    input_start = to_timestamp(start_time)
    input_end = to_timestamp(end_time)

    # Ensure naive datetimes
    if input_start.tzinfo is not None:
        input_start = input_start.replace(tzinfo=None)
    if input_end.tzinfo is not None:
        input_end = input_end.replace(tzinfo=None)

    for exam in exams:
        exam_start = to_timestamp(exam["start_time"])
        exam_end = to_timestamp(exam["end_time"])
       
        if exam_start.tzinfo is not None:
            exam_start = exam_start.replace(tzinfo=None)
        if exam_end.tzinfo is not None:
            exam_end = exam_end.replace(tzinfo=None)

        # Check for overlapping times
        if input_start <= exam_end and exam_start <= input_end:
            print("Found overlapping exam:", exam)
            
            if exam["course_code"] == course_code:
                # Same course, same time = direct clash
                print("Clash: Same course")
                return True

            # Get students for the existing exam course
            existing_students_resp = supabase.table("Enrollments").select("reg_number").eq("course_code", exam["course_code"]).execute()
            existing_students = {s["reg_number"] for s in existing_students_resp.data}

            # Get students for the new exam course
            new_course_students_resp = supabase.table("Enrollments").select("reg_number").eq("course_code", course_code).execute()
            new_students = {s["reg_number"] for s in new_course_students_resp.data}

            # Check for intersection
            if existing_students & new_students:
                print("Clash: Students enrolled in both courses")
                return True

    return False

def update_check_exam_clash(exam_id: str, course_code: str, exam_date: str, start_time: str, end_time: str):
    print("Checking update clashes for:", exam_date)

    # Fetch all exams on the given exam_date, excluding the one being updated
    response = (
        supabase.table("Exams")
        .select("*")
        .eq("exam_date", exam_date)
        .neq("exam_id", exam_id)
        .execute()
    )
    exams = response.data
    print("Exams on same day (excluding self):", exams)

    if not exams:
        return False

    input_start = to_timestamp(start_time)
    input_end = to_timestamp(end_time)

    # Ensure naive datetimes
    if input_start.tzinfo is not None:
        input_start = input_start.replace(tzinfo=None)
    if input_end.tzinfo is not None:
        input_end = input_end.replace(tzinfo=None)

    for exam in exams:
        exam_start = to_timestamp(exam["start_time"])
        exam_end = to_timestamp(exam["end_time"])

        if exam_start.tzinfo is not None:
            exam_start = exam_start.replace(tzinfo=None)
        if exam_end.tzinfo is not None:
            exam_end = exam_end.replace(tzinfo=None)

        # Check for overlapping times
        if input_start <= exam_end and exam_start <= input_end:
            print("Found overlapping exam:", exam)

            if exam["course_code"] == course_code:
                print("Clash: Same course")
                return True

            # Get students for the existing exam course
            existing_students_resp = (
                supabase.table("Enrollments")
                .select("reg_number")
                .eq("course_code", exam["course_code"])
                .execute()
            )
            existing_students = {s["reg_number"] for s in existing_students_resp.data}

            # Get students for the new exam course
            new_course_students_resp = (
                supabase.table("Enrollments")
                .select("reg_number")
                .eq("course_code", course_code)
                .execute()
            )
            new_students = {s["reg_number"] for s in new_course_students_resp.data}

            # Check for intersection
            if existing_students & new_students:
                print("Clash: Students enrolled in both courses")
                return True

    return False



def create_exam(data: dict):
    try:
        updated_data = serialize_exam_data(data)
        print("Serialized data:", updated_data)
        response = supabase.table("Exams").insert(updated_data).execute()
        
        if response.data:
            return response.data
        
        return None

    except APIError as e:
        print("APIError:", e)
        print("APIError message:", e.message)
        
        # Foreign key violation for 'scheduled_by'
        if "scheduled_by" in str(e) and "faculty_member_profiles" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: The faculty member (scheduled_by) does not exist or is invalid."
            )
        
        # Foreign key violation for 'course_code'
        elif "course_code" in str(e) and "Courses" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Invalid course_code: The provided course does not exist."
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Database constraint error: {e.message}"
            )
        


def get_exam_by_id(exam_id: str):
    response = supabase.table("Exams").select("*").eq("exam_id", exam_id).single().execute()
    return response.data

def get_all_exams():
    response = supabase.table("Exams").select("*").execute()
    return response.data

def update_exam(exam_id: str, update_data: dict):
    try:
        print("Update data:", update_data)
        updated_data = serialize_exam_data(update_data)
        print("Serialized update data:", updated_data)

        response = supabase.table("Exams").update(updated_data).eq("exam_id", exam_id).execute()
        
        if response.data:
            return response.data
        return None
    
    except APIError as e:
        print("APIError during update:", e)
        # Check if the foreign key error is due to 'scheduled_by'
        if "scheduled_by" in str(e) and "faculty_member_profiles" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: The faculty member (scheduled_by) does not exist or is invalid."
            )
        elif "course_code" in str(e) and "Courses" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Invalid course_code: The provided course does not exist."
            )
        
        else:
            # Generic 400 for other constraint violations
            raise HTTPException(
                status_code=400,
                detail=f"Database constraint error: {e.message}"
            )
        
def delete_exam(exam_id: str):
    response = supabase.table("Exams").delete().eq("exam_id", exam_id).execute()
    if response.data:
        return response.data
    return None
