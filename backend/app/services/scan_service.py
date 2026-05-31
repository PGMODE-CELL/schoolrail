from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.attendance import StudentAttendanceCreate


QR_CODE_PREFIXES = {
    "STUDENT": "SR_STU",
    "VEHICLE": "SR_VEH",
    "STOP": "SR_STP",
    "ROUTE": "SR_RTE",
}


def parse_qr_code(qr_data: str) -> Dict[str, Any]:
    parts = qr_data.split(":")
    
    if len(parts) < 2:
        return {"valid": False, "error": "Invalid QR code format"}
    
    prefix = parts[0]
    id_part = parts[1]
    
    if prefix not in QR_CODE_PREFIXES.values():
        return {"valid": False, "error": "Unknown QR code type"}
    
    try:
        entity_id = int(id_part)
    except ValueError:
        return {"valid": False, "error": "Invalid ID format"}
    
    entity_type = None
    for key, value in QR_CODE_PREFIXES.items():
        if value == prefix:
            entity_type = key.lower()
            break
    
    return {
        "valid": True,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "raw_data": qr_data,
        "timestamp": datetime.now().isoformat()
    }


def generate_student_qr(student_id: int) -> str:
    return f"{QR_CODE_PREFIXES['STUDENT']}:{student_id}"


def generate_vehicle_qr(vehicle_id: int) -> str:
    return f"{QR_CODE_PREFIXES['VEHICLE']}:{vehicle_id}"


def generate_stop_qr(stop_id: int) -> str:
    return f"{QR_CODE_PREFIXES['STOP']}:{stop_id}"


def generate_route_qr(route_id: int) -> str:
    return f"{QR_CODE_PREFIXES['ROUTE']}:{route_id}"


MOCK_RFID_CARDS = {
    "RFID001": {"student_id": 1, "student_name": "Arjun Sharma"},
    "RFID002": {"student_id": 2, "student_name": "Ananya Verma"},
    "RFID003": {"student_id": 3, "student_name": "Rohan Kumar"},
    "RFID004": {"student_id": 4, "student_name": "Priya Singh"},
    "RFID005": {"student_id": 5, "student_name": "Karthik Nair"},
}


def process_rfid_card(rfid_uid: str) -> Dict[str, Any]:
    if rfid_uid in MOCK_RFID_CARDS:
        card_data = MOCK_RFID_CARDS[rfid_uid]
        return {
            "valid": True,
            "student_id": card_data["student_id"],
            "student_name": card_data["student_name"],
            "rfid_uid": rfid_uid,
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "valid": False,
        "error": "Unknown RFID card",
        "rfid_uid": rfid_uid
    }


def scan_and_mark_attendance(
    scan_type: str,
    scan_data: str,
    route_id: int,
    status: str = "present"
) -> Dict[str, Any]:
    timestamp = datetime.now()
    
    if scan_type == "qr":
        parsed = parse_qr_code(scan_data)
        if not parsed["valid"]:
            return {"success": False, "error": parsed["error"]}
        
        if parsed["entity_type"] != "student":
            return {"success": False, "error": "QR code is not a student QR"}
        
        student_id = parsed["entity_id"]
    
    elif scan_type == "rfid":
        rfid_data = process_rfid_card(scan_data)
        if not rfid_data["valid"]:
            return {"success": False, "error": rfid_data["error"]}
        
        student_id = rfid_data["student_id"]
    
    else:
        return {"success": False, "error": "Invalid scan type"}
    
    from app.services.attendance_service import mark_attendance
    from app.services.student_service import get_student_by_id
    
    student = get_student_by_id(student_id)
    if not student:
        return {"success": False, "error": "Student not found"}
    
    attendance_data = StudentAttendanceCreate(
        student_id=student_id,
        route_id=route_id,
        status=status,
        pickup_time=timestamp.strftime("%I:%M %p") if status == "present" else None,
        drop_time=None
    )
    
    attendance = mark_attendance(attendance_data)
    
    from app.core.websocket import notify_attendance_update
    import asyncio
    try:
        asyncio.create_task(notify_attendance_update(route_id, student_id, status, 1))
    except:
        pass
    
    return {
        "success": True,
        "student_id": student_id,
        "student_name": student.first_name + " " + student.last_name,
        "status": status,
        "attendance_id": attendance.id,
        "timestamp": timestamp.isoformat()
    }


def bulk_scan_attendance(
    scans: List[Dict[str, Any]],
    route_id: int,
    status: str = "present"
) -> Dict[str, Any]:
    results = []
    successful = 0
    failed = 0
    
    for scan in scans:
        result = scan_and_mark_attendance(
            scan_type=scan["type"],
            scan_data=scan["data"],
            route_id=route_id,
            status=status
        )
        
        if result["success"]:
            successful += 1
            results.append(result)
        else:
            failed += 1
            results.append({"success": False, "error": result["error"]})
    
    return {
        "total_scans": len(scans),
        "successful": successful,
        "failed": failed,
        "results": results
    }


def get_attendance_by_scan(student_id: int, date: str) -> Dict[str, Any]:
    from datetime import date as date_type
    from app.services.attendance_service import get_student_attendance
    from datetime import datetime, timedelta
    
    try:
        attendance_date = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        attendance_date = datetime.now().date()
    
    start_date = attendance_date
    end_date = attendance_date
    
    attendance = get_student_attendance(student_id, start_date, end_date)
    
    if attendance:
        return {
            "found": True,
            "student_id": student_id,
            "date": date,
            "status": attendance[0].status,
            "pickup_time": attendance[0].pickup_time,
            "drop_time": attendance[0].drop_time
        }
    
    return {
        "found": False,
        "student_id": student_id,
        "date": date
    }


def register_rfid_card(student_id: int, rfid_uid: str) -> Dict[str, Any]:
    from app.services.student_service import get_student_by_id
    
    student = get_student_by_id(student_id)
    if not student:
        return {"success": False, "error": "Student not found"}
    
    student_name = student.first_name + " " + student.last_name
    
    if rfid_uid in MOCK_RFID_CARDS:
        return {"success": False, "error": "RFID card already registered"}
    
    MOCK_RFID_CARDS[rfid_uid] = {
        "student_id": student_id,
        "student_name": student_name
    }
    
    return {
        "success": True,
        "message": "RFID card registered successfully",
        "student_id": student_id,
        "rfid_uid": rfid_uid
    }


def get_student_by_rfid(rfid_uid: str) -> Optional[Dict[str, Any]]:
    if rfid_uid in MOCK_RFID_CARDS:
        return MOCK_RFID_CARDS[rfid_uid]
    return None


def deactivate_rfid_card(rfid_uid: str) -> Dict[str, Any]:
    if rfid_uid in MOCK_RFID_CARDS:
        del MOCK_RFID_CARDS[rfid_uid]
        return {"success": True, "message": "RFID card deactivated"}
    return {"success": False, "error": "RFID card not found"}


def get_all_registered_cards() -> List[Dict[str, Any]]:
    return [
        {"rfid_uid": uid, **data}
        for uid, data in MOCK_RFID_CARDS.items()
    ]
