from app.services.courses import get_enrolled_courses, get_eligible_courses, get_assigned_courses, get_all_courses, add_new_course, get_all_courses_yet_to_assign, get_eligible_courses_yet_to_enroll
from app.services.enrollments import enroll, unenroll
from app.services.lecturers import get_lecturers

async def handle_message(payload: dict):

    action = payload.get("action")
    data = payload.get("payload", {})

    print(f"Received action: {action}")
    print(f"Received data: {data}")

    if action == "getEnrolledCourses":
        result = await get_enrolled_courses(data)
        return result
    elif action == "getEligibleCourses":
        result = await get_eligible_courses(data)
        return result
    elif action == "getEligibleCoursesYetToEnroll":
        result = await get_eligible_courses_yet_to_enroll(data)
        return result
    elif action == "getAssignedCourses":
        result = await get_assigned_courses(data)
        return result
    elif action == "getAllCourses":
        result = await get_all_courses()
        return result
    elif action == "getAllCoursesYetToAssign":
        result = await get_all_courses_yet_to_assign(data)
        return result
    elif action == "enrollInCourse":
        result = await enroll(data)
        return result
    elif action == "unenrollFromCourse":
        result = await unenroll(data)
        return result
    elif action == "getLecturers":
        result = await get_lecturers()
        return result
    elif action == "addNewCourse":
        result = await add_new_course(data)
        return result
    else:
        return {"error": "Invalid action"}