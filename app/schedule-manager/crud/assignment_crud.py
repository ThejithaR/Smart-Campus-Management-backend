from datetime import datetime, date
import datetime
from fastapi import HTTPException
from uuid import UUID
from database import supabase
from postgrest.exceptions import APIError

def serialize_assignment_data(data: dict) -> dict:
    """
    Convert datetime, date, and UUID objects to serializable formats.
    """
    for key, value in data.items():
        if isinstance(value, datetime.time):
            data[key] = value.isoformat()
        elif isinstance(value, datetime.date):
            data[key] = value.isoformat()
        elif isinstance(value, UUID):
            data[key] = str(value)
    return data

# def serialize_exam_data(data: dict) -> dict:
#     """
#     Convert time, date, and UUID objects to serializable formats.
#     """
#     for key, value in data.items():
#         # If the value is a time object
#         if isinstance(value, datetime.time):
#             # Convert time object to a string (ISO format)
#             data[key] = value.isoformat()
        
#         # If the value is a date object
#         elif isinstance(value, datetime.date):
#             # Convert date object to a string (ISO format)
#             data[key] = value.isoformat()
        
#         # If the value is a UUID object
#         elif isinstance(value, UUID):
#             data[key] = str(value)  # Convert UUID to string
    
#     return data

def create_assignment(data: dict):
    try:
        updated_data = serialize_assignment_data(data)
        print("Serialized assignment data:", updated_data)

        response = supabase.table("Assignments").insert(updated_data).execute()
        
        if response.data:
            return response.data
        return None

    except APIError as e:
        print("APIError:", e)
        print("APIError message:", e.message)

        if "assigned_by" in str(e) and "faculty_member_profiles" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: The faculty member (assigned_by) does not exist or is invalid."
            )
        elif "course_code" in str(e) and "Courses" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Invalid course_code: The provided course does not exist."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected API error: {e.message}"
            )

def get_assignment_by_id(assignment_id: str):
    response = supabase.table("Assignments").select("*").eq("assignment_id", assignment_id).single().execute()
    return response.data

def get_all_assignments():
    response = supabase.table("Assignments").select("*").execute()
    return response.data

def update_assignment(assignment_id: str, update_data: dict):
    try:
        print("Update data:", update_data)
        updated_data = serialize_assignment_data(update_data)
        print("Serialized update data:", updated_data)

        response = supabase.table("Assignments").update(updated_data).eq("assignment_id", assignment_id).execute()
        
        if response.data:
            return response.data
        return None

    except APIError as e:
        if "assigned_by" in str(e) and "faculty_member_profiles" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: The faculty member (assigned_by) does not exist or is invalid."
            )
        elif "course_code" in str(e) and "Courses" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Invalid course_code: The provided course does not exist."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Database constraint error: {e.message}"
            )

def delete_assignment(assignment_id: str):
    try:
        response = supabase.table("Assignments").delete().eq("assignment_id", assignment_id).execute()
        if response.data:
            return response.data
        return None

    except APIError as e:
        print("APIError:", e)
        if 'invalid input syntax for type uuid' in str(e):
            raise HTTPException(
                status_code=400,
                detail="Invalid UUID format for assignment_id."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected API error: {e.message}"
            )
