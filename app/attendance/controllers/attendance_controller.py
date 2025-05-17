from fastapi import HTTPException, status
from services.face_service import register_face, recognize_faces
from services.attendace_logic import can_mark_attendance
from db.supabase import (
    log_attendance, 
    get_student_profile, 
    get_student_attendance_report,
    get_course_attendance_report,
    get_attendance_today
)

from models.schemas import (
    AttendanceResponse, 
    AttendanceMethod, 
    AttendanceRecord, 
    FaceRecognitionResponse,
    AttendanceResult, 
    ApiResponse, 
    AttendanceStatus,
    StudentAttendanceReport
)

async def handle_attendance_message(action: str, payload: dict):
    # action = payload.get("action")
    # data = payload.get("payload")

    print(f"📨 Received action: {action}, payload: {payload}")

    if action == "manualAttendance":
        return await handle_manual_attendance(payload)
    elif action == "recognizeFace":
        return await handle_face_recognition(payload)
    elif action == "registerFace":
        return await handle_face_registration(payload)
    elif action == "getTodayAttendance":
        return await handle_today_attendance(payload)
    elif action == "getStudentReport":
        return await handle_student_report(payload)
    elif action == "getCourseReport":
        return await handle_course_report(payload)
    else:
        return {"error": f"Unknown action: {action}"}

# Handlers

async def handle_manual_attendance(data):
    student = get_student_profile(data["reg_number"])
    if not student["success"]:
        raise HTTPException(status_code=404, detail=student["message"])

    attendance_check = can_mark_attendance(data["reg_number"])
    if not attendance_check["can_mark"]:
        return AttendanceResponse(success=False, message=attendance_check["message"])

    result = log_attendance(
        reg_number=data["reg_number"],
        method=AttendanceMethod.MANUAL,
        status=data["status"],
        location=data["location"],
        course_code=data["course_code"]
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return AttendanceResponse(
        success=True,
        message=f"Attendance marked as {data['status']} for student {data['reg_number']}",
        data=AttendanceRecord(**result["data"])
    )


async def handle_face_recognition(data):
    result = recognize_faces(data["image_base64"], data["location"])
    attendance_results = [
        AttendanceResult(
            reg_number=ar["reg_number"],
            name=ar["name"],
            attendance_result=ar["attendance_result"]
        ) for ar in result.get("attendance_results", [])
    ]

    return FaceRecognitionResponse(
        success=result["success"],
        message=result["message"],
        total_faces_detected=result.get("total_faces_detected", 0),
        recognized_count=result.get("recognized_count", 0),
        unknown_count=result.get("unknown_count", 0),
        students=result.get("students", []),
        unknown_faces=result.get("unknown_faces", []),
        attendance_results=attendance_results
    )


async def handle_face_registration(data):
    result = register_face(data["reg_number"], data["image_base64"])

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return ApiResponse(success=True, message=result["message"])


async def handle_today_attendance(data):
    student = get_student_profile(data["reg_number"])
    if not student["success"]:
        raise HTTPException(status_code=404, detail=student["message"])

    result = get_attendance_today(data["reg_number"])
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return ApiResponse(
        success=True,
        message=f"Retrieved today's attendance for student {data['reg_number']}",
        data=result["data"]
    )


async def handle_student_report(data):
    reg_number = data.get("reg_number")
    if not reg_number:
        raise HTTPException(status_code=400, detail="Registration number is required")

    student = get_student_profile(reg_number)
    if not student["success"]:
        raise HTTPException(status_code=404, detail=student["message"])

    result = get_student_attendance_report(
        reg_number=reg_number,
        start_date=data["start_date"],
        end_date=data["end_date"]
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    attendance_records = [AttendanceRecord(**record) for record in result["data"]]
    summary = {
        "present": sum(1 for r in attendance_records if r.status == AttendanceStatus.PRESENT),
        "absent": sum(1 for r in attendance_records if r.status == AttendanceStatus.ABSENT),
        "late": sum(1 for r in attendance_records if r.status == AttendanceStatus.LATE),
        "total": len(attendance_records)
    }

    report = StudentAttendanceReport(
        reg_number=reg_number,
        name=student["data"].get("name"),
        records=attendance_records,
        summary=summary
    )

    return ApiResponse(
        success=True,
        message=f"Retrieved attendance report for student {reg_number}",
        data=report
    )


async def handle_course_report(data):
    """
    Handle generating attendance report for a specific course on a specific date.
    :param data: AttendanceReportRequest object or dict-like with course_code and start_date
    :return: ApiResponse object
    """
    course_code = data.course_code if hasattr(data, "course_code") else data.get("course_code")
    date_value = data.start_date if hasattr(data, "start_date") else data.get("start_date")

    if not course_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code is required"
        )

    result = get_course_attendance_report(
        course_code=course_code,
        date_value=date_value
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )

    return ApiResponse(
        success=True,
        message=f"Retrieved attendance report for course {course_code}",
        data=result["data"]
    )