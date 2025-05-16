from crud.assignment_crud import (
    create_assignment,
    get_assignment_by_id,
    get_all_assignments,
    update_assignment,
    delete_assignment,
    serialize_assignment_data,
)

from crud.exam_crud import (
    check_exam_clash,
    update_check_exam_clash,
    create_exam,
    get_exam_by_id,
    get_all_exams,
    update_exam,
    delete_exam,
    serialize_exam_data,
)


async def handle_schedule_message(action: str, payload: dict):
    print(f"📨 Received action: {action}, payload: {payload}")

    if action == "scheduleAssignment":
        created = create_assignment(payload)
        if not created:
            return {"error": "Assignment creation failed."}
        return {"message": "Assignment created successfully."}

    elif action == "getAssignment":
        assignment_id = payload.get("assignment_id")
        assignment = get_assignment_by_id(assignment_id)
        if not assignment:
            return {"error": "Assignment not found."}
        return serialize_assignment_data(assignment)

    elif action == "getAllAssignments":
        assignments = get_all_assignments()
        return [serialize_assignment_data(a) for a in assignments]

    elif action == "updateAssignment":
        assignment_id = payload.get("assignment_id")
        updated_data = payload.get("assignment", {})
        updated = update_assignment(assignment_id, updated_data)
        if not updated:
            return {"error": "Assignment not found or update failed."}
        return {"message": "Assignment updated successfully."}

    elif action == "deleteAssignment":
        assignment_id = payload.get("assignment_id")
        deleted = delete_assignment(assignment_id)
        if not deleted:
            return {"error": "Assignment not found or delete failed."}
        return {"message": "Assignment deleted successfully."}

    elif action == "scheduleExam":
        exam = payload.get("exam")
        clash = check_exam_clash(
            course_code=exam["course_code"],
            exam_date=exam["exam_date"],
            start_time=exam["start_time"],
            end_time=exam["end_time"]
        )
        if clash:
            return {"error": "Exam clash detected! Group already has an exam at that time."}

        created = create_exam(exam)
        if not created:
            return {"error": "Exam creation failed."}
        return {"message": "Exam scheduled successfully."}

    elif action == "getExam":
        exam_id = payload.get("exam_id")
        exam = get_exam_by_id(exam_id)
        if not exam:
            return {"error": "Exam not found."}
        return serialize_exam_data(exam)

    elif action == "getAllExams":
        exams = get_all_exams()
        return [serialize_exam_data(e) for e in exams]

    elif action == "updateExam":
        exam_id = payload.get("exam_id")
        update_data = payload.get("exam", {})
        existing_exam = get_exam_by_id(exam_id)
        if not existing_exam:
            return {"error": "Exam not found."}

        # Fill missing required fields
        course_code = update_data.get("course_code", existing_exam["course_code"])
        exam_date = update_data.get("exam_date", existing_exam["exam_date"])
        start_time = update_data.get("start_time", existing_exam["start_time"])
        end_time = update_data.get("end_time", existing_exam["end_time"])

        clash = update_check_exam_clash(
            exam_id=exam_id,
            course_code=course_code,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
        )
        if clash:
            return {"error": "Exam clash detected during update!"}

        updated = update_exam(exam_id, update_data)
        if not updated:
            return {"error": "Exam update failed."}
        return {"message": "Exam updated successfully."}

    elif action == "deleteExam":
        exam_id = payload.get("exam_id")
        deleted = delete_exam(exam_id)
        if not deleted:
            return {"error": "Exam not found or delete failed."}
        return {"message": "Exam deleted successfully."}

    else:
        print(f"❌ Unknown action received. action: {action}")
        return {"error": f"Unknown action: {action}"}
