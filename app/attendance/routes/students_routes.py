# from fastapi import APIRouter, HTTPException, status
# from typing import List, Optional

# from models.schemas import (
#     StudentProfile,
#     Course,
#     Enrollment,
#     StudentEnrollmentResponse,
#     ApiResponse
# )

# from db.supabase import (
#     get_student_profile,
#     get_student_courses
# )

# router = APIRouter(prefix="/students", tags=["students"])

# @router.get("/{reg_number}", response_model=ApiResponse)
# async def get_student(reg_number: str):
#     """
#     Get a student's profile by registration number
#     """
#     result = get_student_profile(reg_number)
    
#     if not result["success"]:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=result["message"]
#         )
    
#     return ApiResponse(
#         success=True,
#         message=f"Student profile retrieved for {reg_number}",
#         data=result["data"]
#     )

# @router.get("/{reg_number}/courses", response_model=StudentEnrollmentResponse)
# async def get_courses(reg_number: str):
#     """
#     Get all courses a student is enrolled in
#     """
#     # First verify student exists
#     student = get_student_profile(reg_number)
#     if not student["success"]:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=student["message"]
#         )
    
#     # Get student courses
#     courses_result = get_student_courses(reg_number)
    
#     if not courses_result["success"]:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=courses_result["message"]
#         )
    
#     # Format the courses data
#     formatted_courses = []
#     for enrollment in courses_result["data"]:
#         course_data = enrollment.get("Courses", {})
#         if course_data:
#             formatted_courses.append(Course(
#                 course_code=course_data.get("course_code"),
#                 course_name=course_data.get("course_name"),
#                 description=course_data.get("description")
#             ))
    
#     return StudentEnrollmentResponse(
#         success=True,
#         message=f"Retrieved courses for student {reg_number}",
#         student=StudentProfile(**student["data"]),
#         courses=formatted_courses
#     )
