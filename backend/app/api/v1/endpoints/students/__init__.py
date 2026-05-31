from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.core.security import get_current_user, require_admin
from app.services.student_service import (
    get_all_students,
    get_student_by_id,
    create_student,
    update_student,
    delete_student,
    get_students_by_route,
    get_student_with_details,
)
from app.schemas.schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    route_id: Optional[int] = Query(None),
    class_name: Optional[str] = Query(None),
    current_user=Depends(get_current_user)
):
    return get_all_students(route_id, class_name)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, current_user=Depends(get_current_user)):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/{student_id}/details")
async def get_student_full_details(student_id: int, current_user=Depends(get_current_user)):
    details = get_student_with_details(student_id)
    if not details:
        raise HTTPException(status_code=404, detail="Student not found")
    return details


@router.get("/route/{route_id}", response_model=List[StudentResponse])
async def get_students_on_route(
    route_id: int,
    current_user=Depends(get_current_user)
):
    return get_students_by_route(route_id)


@router.post("/", response_model=StudentResponse)
async def create_new_student(
    student_data: StudentCreate,
    current_user=Depends(require_admin)
):
    return create_student(student_data)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_existing_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user=Depends(require_admin)
):
    student = update_student(student_id, student_data)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{student_id}")
async def delete_existing_student(
    student_id: int,
    current_user=Depends(require_admin)
):
    if not delete_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
