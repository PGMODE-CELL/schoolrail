from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Student
from app.schemas.schemas import StudentCreate, StudentResponse, StudentUpdate


def _student_to_dict(student: Student) -> dict:
    return {
        "id": student.id,
        "uuid": student.uuid,
        "school_id": student.school_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "full_name": student.full_name or f"{student.first_name} {student.last_name}" if student.first_name else student.last_name,
        "student_id": student.student_id,
        "roll_number": student.roll_number,
        "class_name": student.class_name,
        "section": student.section,
        "email": student.email,
        "phone": student.phone,
        "date_of_birth": student.date_of_birth,
        "gender": student.gender,
        "blood_group": student.blood_group,
        "address": student.address,
        "father_name": student.father_name,
        "father_phone": student.father_phone,
        "mother_name": student.mother_name,
        "guardian_name": student.guardian_name,
        "guardian_phone": student.guardian_phone,
        "route_id": student.route_id,
        "pickup_stop_id": student.pickup_stop_id,
        "drop_stop_id": student.drop_stop_id,
        "transport_fees": student.transport_fees,
        "status": student.status,
        "is_transport_applicable": student.is_transport_applicable,
        "created_at": student.created_at,
        "updated_at": student.updated_at,
    }


def get_all_students(route_id: Optional[int] = None, class_name: Optional[str] = None) -> List[StudentResponse]:
    db = SessionLocal()
    try:
        query = db.query(Student)
        if route_id:
            query = query.filter(Student.route_id == route_id)
        if class_name:
            query = query.filter(Student.class_name == class_name)
        students = query.all()
        return [StudentResponse(**_student_to_dict(s)) for s in students]
    except Exception:
        return []
    finally:
        db.close()


def get_student_by_id(student_id: int) -> Optional[StudentResponse]:
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None
        return StudentResponse(**_student_to_dict(student))
    except Exception:
        return None
    finally:
        db.close()


def create_student(student_data: StudentCreate) -> StudentResponse:
    db = SessionLocal()
    try:
        data = student_data.model_dump()
        student = Student(**data)
        if not student.full_name:
            student.full_name = f"{student.first_name} {student.last_name}" if student.first_name else student.last_name
        db.add(student)
        db.commit()
        db.refresh(student)
        return StudentResponse(**_student_to_dict(student))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_student(student_id: int, student_data: StudentUpdate) -> Optional[StudentResponse]:
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None
        update_data = student_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(student, key, value)
        if not student.full_name:
            student.full_name = f"{student.first_name} {student.last_name}" if student.first_name else student.last_name
        student.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(student)
        return StudentResponse(**_student_to_dict(student))
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def delete_student(student_id: int) -> bool:
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False
        db.delete(student)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def get_students_by_route(route_id: int) -> List[StudentResponse]:
    db = SessionLocal()
    try:
        students = db.query(Student).filter(Student.route_id == route_id).all()
        return [StudentResponse(**_student_to_dict(s)) for s in students]
    except Exception:
        return []
    finally:
        db.close()


def get_student_with_details(student_id: int) -> Optional[dict]:
    student = get_student_by_id(student_id)
    if not student:
        return None

    from app.services.attendance_service import get_attendance_statistics
    from app.services.fee_service import get_student_fees

    attendance_stats = get_attendance_statistics(student_id, 30)
    fees = get_student_fees(student_id)

    return {
        "student": student,
        "attendance": attendance_stats,
        "fees": fees,
    }
