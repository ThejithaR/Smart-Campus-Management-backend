from fastapi import APIRouter, HTTPException
from models.assignment import AssignmentCreateRequest, AssignmentUpdateRequest
from crud.assignment_crud import (
    create_assignment,
    get_assignment_by_id,
    get_all_assignments,
    update_assignment,
    delete_assignment
)

router = APIRouter()

@router.post("/assignments/schedule")
def create_assignment_route(assignment: AssignmentCreateRequest):
    data = assignment.dict()
    created = create_assignment(data)

    if not created:
        raise HTTPException(status_code=400, detail="Assignment creation failed.")

    return {"message": "Assignment created successfully."}

@router.get("/assignments/{assignment_id}")
def get_assignment(assignment_id: str):
    assignment = get_assignment_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    return assignment

@router.get("/assignments")
def list_assignments():
    assignments = get_all_assignments()
    return assignments

@router.put("/assignments/{assignment_id}")
def update_assignment_route(assignment_id: str, assignment: AssignmentUpdateRequest):
    updated_data = assignment.dict(exclude_unset=True)
    updated_assignment = update_assignment(assignment_id, updated_data)
    if not updated_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    return {"message": "Assignment updated successfully."}

@router.delete("/assignments/{assignment_id}")
def delete_assignment_route(assignment_id: str):
    deleted = delete_assignment(assignment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Assignment not found or delete failed.")
    return {"message": "Assignment deleted successfully."}
