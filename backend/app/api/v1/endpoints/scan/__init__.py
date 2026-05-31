from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from app.core.security import get_current_user

router = APIRouter(prefix="/scan", tags=["QR/RFID Scanning"])


class QRCodeScanRequest(BaseModel):
    qr_data: str
    route_id: int
    status: str = "present"


class RFIDScanRequest(BaseModel):
    rfid_uid: str
    route_id: int
    status: str = "present"


class BulkScanRequest(BaseModel):
    scans: List[dict]
    route_id: int
    status: str = "present"


@router.post("/qr")
async def scan_qr_code(request: QRCodeScanRequest, current_user=Depends(get_current_user)):
    from app.services.scan_service import scan_and_mark_attendance
    
    result = scan_and_mark_attendance(
        scan_type="qr",
        scan_data=request.qr_data,
        route_id=request.route_id,
        status=request.status
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/rfid")
async def scan_rfid_card(request: RFIDScanRequest, current_user=Depends(get_current_user)):
    from app.services.scan_service import scan_and_mark_attendance
    
    result = scan_and_mark_attendance(
        scan_type="rfid",
        scan_data=request.rfid_uid,
        route_id=request.route_id,
        status=request.status
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/bulk")
async def bulk_scan(request: BulkScanRequest, current_user=Depends(get_current_user)):
    from app.services.scan_service import bulk_scan_attendance
    
    result = bulk_scan_attendance(
        scans=request.scans,
        route_id=request.route_id,
        status=request.status
    )
    
    return result


@router.get("/student/{student_id}/attendance")
async def get_student_attendance_by_scan(student_id: int, date: str, current_user=Depends(get_current_user)):
    from app.services.scan_service import get_attendance_by_scan
    
    return get_attendance_by_scan(student_id, date)


@router.post("/register-rfid")
async def register_rfid(student_id: int, rfid_uid: str, current_user=Depends(get_current_user)):
    from app.services.scan_service import register_rfid_card
    
    result = register_rfid_card(student_id, rfid_uid)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/deactivate-rfid")
async def deactivate_rfid(rfid_uid: str, current_user=Depends(get_current_user)):
    from app.services.scan_service import deactivate_rfid_card
    
    result = deactivate_rfid_card(rfid_uid)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/registered-cards")
async def get_registered_cards(current_user=Depends(get_current_user)):
    from app.services.scan_service import get_all_registered_cards
    
    return {"cards": get_all_registered_cards()}


@router.get("/generate-qr/{student_id}")
async def generate_student_qr(student_id: int, current_user=Depends(get_current_user)):
    from app.services.scan_service import generate_student_qr
    from app.services.student_service import get_student_by_id
    
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    qr_data = generate_student_qr(student_id)
    
    return {
        "student_id": student_id,
        "qr_data": qr_data,
        "student_name": student.first_name + " " + student.last_name
    }
