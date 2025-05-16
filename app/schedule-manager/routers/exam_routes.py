from fastapi import APIRouter, HTTPException
from models.exam import ExamCreateRequest, ExamUpdateRequest
from crud.exam_crud import (
    check_exam_clash,
    update_check_exam_clash,
    create_exam,
    get_exam_by_id,
    get_all_exams,
    update_exam,
    delete_exam
)

router = APIRouter()

@router.post("/exams/schedule")
def schedule_exam(exam: ExamCreateRequest):
    clash = check_exam_clash(
        course_code=exam.course_code,
        exam_date=exam.exam_date,
        start_time=exam.start_time,
        end_time=exam.end_time
    )
    print(clash)
    if clash:
        raise HTTPException(status_code=400, detail="Exam clash detected! Group already has an exam at that time.")
    
    data = exam.dict()
    print(data)
    create_exam(data)

    return {"message": "Exam scheduled successfully."}

@router.get("/exams/{exam_id}")
def get_exam(exam_id: str):
    exam = get_exam_by_id(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")
    return exam


@router.get("/exams")
def list_exams():
    exams = get_all_exams()
    return exams

@router.put("/exams/{exam_id}")
def update_exam_route(exam_id: str, exam: ExamUpdateRequest):
    updated_data = exam.dict(exclude_unset=True)

    # Fetch the existing exam to get any missing required fields
    existing_exam = get_exam_by_id(exam_id)
    if not existing_exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    # Merge existing values with the updated ones
    course_code = updated_data.get("course_code", existing_exam["course_code"])
    exam_date = updated_data.get("exam_date", existing_exam["exam_date"])
    start_time = updated_data.get("start_time", existing_exam["start_time"])
    end_time = updated_data.get("end_time", existing_exam["end_time"])

    # Check for clashes
    clash = update_check_exam_clash(
        exam_id=exam_id,
        course_code=course_code,
        exam_date=exam_date,
        start_time=start_time,
        end_time=end_time
    )
    if clash:
        raise HTTPException(status_code=400, detail="Exam clash detected during update!")

    # Proceed with the update
    updated_exam = update_exam(exam_id, updated_data)
    if not updated_exam:
        raise HTTPException(status_code=404, detail="Exam not found after attempting update.")

    return {"message": "Exam updated successfully."}


@router.delete("/exams/{exam_id}")
def delete_exam_route(exam_id: str):
    deleted = delete_exam(exam_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exam not found or delete failed.")
    return {"message": "Exam deleted successfully."}