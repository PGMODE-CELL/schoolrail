from typing import Optional, List, Dict, Any
from datetime import datetime, date
import io
import csv
from io import StringIO


def generate_attendance_report_csv(
    data: List[Dict[str, Any]],
    filename: str = "attendance_report"
) -> bytes:
    output = StringIO()
    if not data:
        return output.getvalue().encode()
    
    fieldnames = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    
    return output.getvalue().encode()


def generate_fee_report_csv(
    data: List[Dict[str, Any]],
    filename: str = "fee_report"
) -> bytes:
    output = StringIO()
    if not data:
        return output.getvalue().encode()
    
    fieldnames = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    
    return output.getvalue().encode()


def generate_student_list_csv(
    students: List[Dict[str, Any]],
    filename: str = "student_list"
) -> bytes:
    output = StringIO()
    if not students:
        return output.getvalue().encode()
    
    fieldnames = list(students[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(students)
    
    return output.getvalue().encode()


def generate_vehicle_report_csv(
    vehicles: List[Dict[str, Any]],
    filename: str = "vehicle_report"
) -> bytes:
    output = StringIO()
    if not vehicles:
        return output.getvalue().encode()
    
    fieldnames = list(vehicles[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(vehicles)
    
    return output.getvalue().encode()


def generate_route_report_csv(
    routes: List[Dict[str, Any]],
    filename: str = "route_report"
) -> bytes:
    output = StringIO()
    if not routes:
        return output.getvalue().encode()
    
    fieldnames = list(routes[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(routes)
    
    return output.getvalue().encode()


def generate_monthly_collection_report(
    data: Dict[str, Any],
    filename: str = "monthly_collection"
) -> bytes:
    output = StringIO()
    
    output.write("Monthly Collection Report\n")
    output.write("=" * 40 + "\n")
    output.write(f"Month: {data.get('month', 'N/A')}\n")
    output.write(f"Year: {data.get('year', 'N/A')}\n")
    output.write(f"Total Collected: ₹{data.get('total_collected', 0):,.2f}\n")
    output.write(f"Total Transactions: {data.get('total_transactions', 0)}\n")
    output.write("\nBreakdown by Fee Type:\n")
    output.write("-" * 40 + "\n")
    
    if 'by_fee_type' in data:
        for fee_type, amount in data['by_fee_type'].items():
            output.write(f"{fee_type}: ₹{amount:,.2f}\n")
    
    return output.getvalue().encode()


def generate_attendance_summary_text(
    summary: Dict[str, Any],
    date: str,
    filename: str = "attendance_summary"
) -> bytes:
    output = StringIO()
    
    output.write("=" * 50 + "\n")
    output.write("SCHOOL ATTENDANCE REPORT\n")
    output.write("=" * 50 + "\n")
    output.write(f"Date: {date}\n")
    output.write("-" * 50 + "\n")
    output.write(f"Total Students: {summary.get('total_students', 0)}\n")
    output.write(f"Present: {summary.get('present', 0)}\n")
    output.write(f"Absent: {summary.get('absent', 0)}\n")
    output.write(f"Late: {summary.get('late', 0)}\n")
    output.write(f"On Leave: {summary.get('on_leave', 0)}\n")
    output.write(f"Attendance %: {summary.get('present_percentage', 0)}%\n")
    output.write("=" * 50 + "\n")
    
    return output.getvalue().encode()


def generate_fee_receipt_text(
    student_name: str,
    fee_type: str,
    amount: float,
    transaction_id: str,
    payment_date: str,
    filename: str = "fee_receipt"
) -> bytes:
    output = StringIO()
    
    output.write("=" * 50 + "\n")
    output.write("SCHOOL TRANSPORT FEE RECEIPT\n")
    output.write("=" * 50 + "\n")
    output.write(f"Student Name: {student_name}\n")
    output.write(f"Fee Type: {fee_type}\n")
    output.write(f"Amount Paid: ₹{amount:,.2f}\n")
    output.write(f"Transaction ID: {transaction_id}\n")
    output.write(f"Payment Date: {payment_date}\n")
    output.write("-" * 50 + "\n")
    output.write("This is a computer-generated receipt.\n")
    output.write("=" * 50 + "\n")
    
    return output.getvalue().encode()


def generate_driver_performance_report(
    driver_data: Dict[str, Any],
    filename: str = "driver_performance"
) -> bytes:
    output = StringIO()
    
    output.write("=" * 50 + "\n")
    output.write("DRIVER PERFORMANCE REPORT\n")
    output.write("=" * 50 + "\n")
    output.write(f"Driver Name: {driver_data.get('name', 'N/A')}\n")
    output.write(f"Rating: {driver_data.get('rating', 0)}/5\n")
    output.write(f"Total Trips: {driver_data.get('total_trips', 0)}\n")
    output.write("-" * 50 + "\n")
    output.write("Performance Metrics:\n")
    output.write(f"On-Time %: {driver_data.get('on_time_percentage', 0)}%\n")
    output.write(f"Safety Score: {driver_data.get('safety_score', 0)}\n")
    output.write(f"Incidents: {driver_data.get('incidents', 0)}\n")
    output.write("=" * 50 + "\n")
    
    return output.getvalue().encode()


class ReportGenerator:
    def __init__(self):
        self.formats = ['csv', 'txt']
    
    def generate(self, report_type: str, data: Dict[str, Any], format: str = 'csv') -> bytes:
        if format == 'csv':
            if report_type == 'attendance':
                return generate_attendance_report_csv(data.get('records', []))
            elif report_type == 'fees':
                return generate_fee_report_csv(data.get('records', []))
            elif report_type == 'students':
                return generate_student_list_csv(data.get('records', []))
            elif report_type == 'vehicles':
                return generate_vehicle_report_csv(data.get('records', []))
            elif report_type == 'routes':
                return generate_route_report_csv(data.get('records', []))
        elif format == 'txt':
            if report_type == 'attendance_summary':
                return generate_attendance_summary_text(
                    data.get('summary', {}),
                    data.get('date', '')
                )
            elif report_type == 'fee_receipt':
                return generate_fee_receipt_text(
                    data.get('student_name', ''),
                    data.get('fee_type', ''),
                    data.get('amount', 0),
                    data.get('transaction_id', ''),
                    data.get('payment_date', '')
                )
            elif report_type == 'driver_performance':
                return generate_driver_performance_report(data)
        
        return b""


report_generator = ReportGenerator()


def get_available_report_types() -> List[Dict[str, str]]:
    return [
        {"type": "attendance", "name": "Attendance Report", "format": "csv"},
        {"type": "fees", "name": "Fees Report", "format": "csv"},
        {"type": "students", "name": "Student List", "format": "csv"},
        {"type": "vehicles", "name": "Vehicle Report", "format": "csv"},
        {"type": "routes", "name": "Route Report", "format": "csv"},
        {"type": "attendance_summary", "name": "Daily Attendance Summary", "format": "txt"},
        {"type": "fee_receipt", "name": "Fee Receipt", "format": "txt"},
        {"type": "driver_performance", "name": "Driver Performance", "format": "txt"},
    ]
