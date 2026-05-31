"""
SchoolRail - Constants and Enums
=================================
Application-wide constants and enumerations.
"""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    SCHOOL_ADMIN = "school_admin"
    DRIVER = "driver"
    PARENT = "parent"
    TEACHER = "teacher"


class VehicleStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class VehicleType(str, Enum):
    BUS = "bus"
    VAN = "van"
    MINIBUS = "minibus"
    SEDAN = "sedan"
    SUV = "suv"


class DriverStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"


class RouteStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class StudentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSFERRED = "transferred"
    GRADUATED = "graduated"


class TripStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripType(str, Enum):
    MORNING_PICKUP = "morning_pickup"
    EVENING_DROP = "evening_drop"
    SPECIAL = "special"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class FeeStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIAL = "partial"


class FeeType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"


class AlertType(str, Enum):
    ROUTE_DELAY = "route_delay"
    SPEED_VIOLATION = "speed_violation"
    GEOFENCE_BREACH = "geofence_breach"
    EMERGENCY = "emergency"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    ATTENDANCE = "attendance"
    FEE = "fee"
    MAINTENANCE = "maintenance"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    WHATSAPP = "whatsapp"


class MaintenanceType(str, Enum):
    ROUTINE = "routine"
    REPAIR = "repair"
    INSPECTION = "inspection"
    EMERGENCY = "emergency"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    ONLINE = "online"


# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M"

# Vehicle capacity defaults
MIN_SEATING_CAPACITY = 10
MAX_SEATING_CAPACITY = 80

# Speed limits (km/h)
MAX_SPEED_LIMIT = 80
SPEED_WARNING_THRESHOLD = 60

# Geofence defaults (meters)
DEFAULT_GEOFENCE_RADIUS = 100
STOP_GEOFENCE_RADIUS = 50

# Token expiry (minutes)
ACCESS_TOKEN_EXPIRE = 1440  # 24 hours
REFRESH_TOKEN_EXPIRE = 43200  # 30 days

# File upload limits
MAX_FILE_SIZE_MB = 10
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", "application/vnd.ms-excel"]

# SMS templates
SMS_TEMPLATE_ATTENDANCE = "Your child {student_name} was {status} at {stop_name}."
SMS_TEMPLATE_FEE_REMINDER = "Fee reminder: {amount} due on {due_date} for {student_name}."
SMS_TEMPLATE_TRIP_START = "Bus {vehicle_number} has started on route {route_name}."

# Email templates
EMAIL_TEMPLATE_ATTENDANCE = """
<h2>Attendance Update</h2>
<p>Dear Parent,</p>
<p>Your child <strong>{student_name}</strong> was marked as <strong>{status}</strong>.</p>
<ul>
  <li><strong>Stop:</strong> {stop_name}</li>
  <li><strong>Time:</strong> {time}</li>
  <li><strong>Date:</strong> {date}</li>
</ul>
"""

# Colors for UI (hex)
COLORS = {
    "primary": "#6366f1",
    "primary_dark": "#4f46e5",
    "secondary": "#8b5cf6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "light": "#f3f4f6",
    "dark": "#1f2937",
    "gray": "#6b7280",
    "white": "#ffffff",
    "background": "#f9fafb",
}

# Error messages
ERROR_MESSAGES = {
    "UNAUTHORIZED": "You are not authorized to perform this action",
    "NOT_FOUND": "The requested resource was not found",
    "VALIDATION_ERROR": "Validation error occurred",
    "DUPLICATE_ENTRY": "Duplicate entry found",
    "SERVER_ERROR": "Internal server error occurred",
}

# Success messages
SUCCESS_MESSAGES = {
    "CREATED": "Created successfully",
    "UPDATED": "Updated successfully",
    "DELETED": "Deleted successfully",
    "SAVED": "Saved successfully",
}