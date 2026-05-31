"""
SchoolRail - Pydantic Schemas
=============================
Request and response schemas for the API.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any
from datetime import datetime, date
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    SCHOOL_ADMIN = "school_admin"
    DRIVER = "driver"
    PARENT = "parent"


class VehicleStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class DriverStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class AttendanceStatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class FeeStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class BaseSchema(BaseModel):
    """Base schema with common fields"""
    id: int
    uuid: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int


# =============================================================================
# AUTH SCHEMAS
# =============================================================================

class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserCreate(BaseModel):
    """User creation schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: UserRoleEnum = UserRoleEnum.PARENT
    school_id: Optional[int] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserResponse(BaseSchema):
    """User response schema"""
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    school_id: Optional[int] = None
    is_active: bool = True
    is_verified: bool = False


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


# =============================================================================
# SCHOOL SCHEMAS
# =============================================================================

class SchoolCreate(BaseModel):
    """School creation schema"""
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    display_name: Optional[str] = None
    tagline: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#6366f1"
    secondary_color: Optional[str] = "#8b5cf6"
    timezone: Optional[str] = "Asia/Kolkata"
    currency: Optional[str] = "INR"
    language: Optional[str] = "en"


class SchoolResponse(BaseSchema):
    """School response schema"""
    name: str
    code: str
    display_name: Optional[str] = None
    tagline: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    pincode: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    timezone: str
    currency: str
    language: str
    is_active: bool
    is_verified: bool


class SchoolUpdate(SchoolCreate):
    """School update schema"""
    pass


# =============================================================================
# VEHICLE SCHEMAS
# =============================================================================

class VehicleCreate(BaseModel):
    """Vehicle creation schema"""
    school_id: int
    reg_number: str = Field(..., min_length=5, max_length=20)
    reg_state: Optional[str] = None
    reg_date: Optional[date] = None
    vehicle_type: str = Field(..., min_length=2)
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    chassis_number: Optional[str] = None
    engine_number: Optional[str] = None
    seating_capacity: int = Field(..., gt=0)
    standing_capacity: Optional[int] = 0
    insurance_number: Optional[str] = None
    insurance_expiry: Optional[date] = None
    permit_number: Optional[str] = None
    permit_expiry: Optional[date] = None
    fitness_certificate: Optional[str] = None
    fitness_expiry: Optional[date] = None
    pollution_certificate: Optional[str] = None
    pollution_expiry: Optional[date] = None
    gps_device_id: Optional[str] = None
    gps_device_number: Optional[str] = None
    gps_sim_number: Optional[str] = None
    gps_installed: bool = False
    front_image: Optional[str] = None
    back_image: Optional[str] = None
    side_image: Optional[str] = None
    status: VehicleStatusEnum = VehicleStatusEnum.ACTIVE
    purchase_price: Optional[float] = None
    features: Optional[dict] = None
    
    @validator('reg_number')
    def normalize_reg_number(cls, v):
        return v.upper().replace(' ', '')


class VehicleResponse(BaseSchema):
    """Vehicle response schema"""
    school_id: int
    reg_number: str
    reg_state: Optional[str] = None
    vehicle_type: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    seating_capacity: int
    standing_capacity: Optional[int] = None
    total_capacity: Optional[int] = None
    insurance_expiry: Optional[datetime] = None
    permit_expiry: Optional[datetime] = None
    fitness_expiry: Optional[datetime] = None
    gps_device_id: Optional[str] = None
    gps_installed: bool
    status: str
    is_available: bool
    total_km: Optional[float] = None
    front_image: Optional[str] = None


class VehicleUpdate(VehicleCreate):
    """Vehicle update schema"""
    pass


# =============================================================================
# DRIVER SCHEMAS
# =============================================================================

class DriverCreate(BaseModel):
    """Driver creation schema"""
    school_id: int
    user_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: str = Field(..., min_length=10, max_length=20)
    alternate_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    license_number: str = Field(..., min_length=5, max_length=50)
    license_type: Optional[str] = None
    license_expiry: date
    license_image: Optional[str] = None
    total_experience_years: Optional[int] = None
    previous_employer: Optional[str] = None
    is_background_verified: bool = False
    police_clearance: bool = False
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    status: DriverStatusEnum = DriverStatusEnum.ACTIVE
    salary_type: Optional[str] = None
    salary_amount: Optional[float] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None


class DriverResponse(BaseSchema):
    """Driver response schema"""
    school_id: int
    user_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    first_name: str
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    photo_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: str
    alternate_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    license_number: str
    license_type: Optional[str] = None
    license_expiry: datetime
    is_background_verified: bool
    police_clearance: bool
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    status: str
    is_available: bool
    rating: float
    total_trips: int
    safe_driving_score: int


class DriverUpdate(DriverCreate):
    """Driver update schema"""
    pass


# =============================================================================
# ROUTE SCHEMAS
# =============================================================================

class StopCreate(BaseModel):
    """Stop creation schema"""
    name: str = Field(..., min_length=2, max_length=200)
    address: Optional[str] = None
    landmark: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    stop_order: int = Field(..., ge=1)
    estimated_arrival_time: Optional[str] = None
    pickup_time_from: Optional[str] = None
    pickup_time_to: Optional[str] = None
    drop_time_from: Optional[str] = None
    drop_time_to: Optional[str] = None
    geofence_enabled: bool = False
    geofence_radius_meters: int = 50


class StopResponse(BaseModel):
    """Stop response schema"""
    id: int
    uuid: str
    route_id: int
    name: str
    address: Optional[str] = None
    landmark: Optional[str] = None
    latitude: float
    longitude: float
    stop_order: int
    estimated_arrival_time: Optional[str] = None
    geofence_enabled: bool
    is_active: bool

    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    """Route creation schema"""
    school_id: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    name: str = Field(..., min_length=2, max_length=200)
    route_code: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = None
    start_point: str = Field(..., min_length=2)
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    end_point: str = Field(..., min_length=2)
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    total_distance_km: Optional[float] = None
    estimated_time_minutes: Optional[int] = None
    morning_pickup_time: Optional[str] = None
    evening_drop_time: Optional[str] = None
    operating_days: Optional[List[str]] = None
    geofence_enabled: bool = False
    geofence_radius_meters: int = 100
    waypoints: Optional[List[dict]] = None
    base_fare: Optional[float] = None
    per_km_rate: Optional[float] = None
    stops: Optional[List[StopCreate]] = None


class RouteResponse(BaseSchema):
    """Route response schema"""
    school_id: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    name: str
    route_code: str
    description: Optional[str] = None
    start_point: str
    end_point: str
    total_distance_km: Optional[float] = None
    estimated_time_minutes: Optional[int] = None
    morning_pickup_time: Optional[str] = None
    evening_drop_time: Optional[str] = None
    geofence_enabled: bool
    status: str
    is_primary: bool
    base_fare: Optional[float] = None
    stops: List[StopResponse] = []


class RouteUpdate(RouteCreate):
    """Route update schema"""
    pass


# =============================================================================
# STUDENT SCHEMAS
# =============================================================================

class StudentCreate(BaseModel):
    """Student creation schema"""
    school_id: int
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    student_id: str = Field(..., min_length=2, max_length=50)
    roll_number: Optional[str] = None
    class_name: str = Field(..., min_length=1, max_length=20)
    section: Optional[str] = None
    admission_date: Optional[date] = None
    academic_year: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    father_name: Optional[str] = None
    father_phone: Optional[str] = None
    father_email: Optional[EmailStr] = None
    father_occupation: Optional[str] = None
    mother_name: Optional[str] = None
    mother_phone: Optional[str] = None
    mother_email: Optional[EmailStr] = None
    mother_occupation: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_relation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    route_id: Optional[int] = None
    pickup_stop_id: Optional[int] = None
    drop_stop_id: Optional[int] = None
    pickup_time: Optional[str] = None
    drop_time: Optional[str] = None
    transport_fees: Optional[float] = None
    status: str = "active"
    is_transport_applicable: bool = True


class StudentResponse(BaseSchema):
    """Student response schema"""
    school_id: int
    first_name: str
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    photo_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    student_id: str
    roll_number: Optional[str] = None
    class_name: str
    section: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    father_name: Optional[str] = None
    father_phone: Optional[str] = None
    mother_name: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    route_id: Optional[int] = None
    pickup_stop_id: Optional[int] = None
    drop_stop_id: Optional[int] = None
    transport_fees: Optional[float] = None
    status: str
    is_transport_applicable: bool


class StudentUpdate(StudentCreate):
    """Student update schema"""
    pass


# =============================================================================
# ATTENDANCE SCHEMAS
# =============================================================================

class AttendanceCreate(BaseModel):
    """Attendance creation schema"""
    student_id: int
    trip_id: Optional[int] = None
    date: date
    trip_type: str
    status: AttendanceStatusEnum
    scheduled_time: Optional[str] = None
    actual_time: Optional[str] = None
    stop_id: Optional[int] = None
    stop_name: Optional[str] = None
    notes: Optional[str] = None
    source: str = "manual"


class AttendanceResponse(BaseModel):
    """Attendance response schema"""
    id: int
    student_id: int
    trip_id: Optional[int] = None
    date: datetime
    trip_type: str
    status: str
    scheduled_time: Optional[str] = None
    actual_time: Optional[str] = None
    stop_id: Optional[int] = None
    stop_name: Optional[str] = None
    notes: Optional[str] = None
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class BulkAttendanceCreate(BaseModel):
    """Bulk attendance creation"""
    date: date
    trip_type: str
    attendances: List[AttendanceCreate]


# =============================================================================
# FEE SCHEMAS
# =============================================================================

class FeeCreate(BaseModel):
    """Fee creation schema"""
    school_id: int
    student_id: int
    fee_type: str = Field(..., min_length=2)
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    gst_rate: float = 0
    due_date: date
    issue_date: Optional[date] = None
    notes: Optional[str] = None


class FeeResponse(BaseSchema):
    """Fee response schema"""
    school_id: int
    student_id: int
    fee_type: str
    title: str
    description: Optional[str] = None
    amount: float
    gst_rate: float
    gst_amount: float
    total_amount: float
    discount_amount: float
    final_amount: float
    due_date: datetime
    status: str
    paid_amount: float
    paid_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None


class FeePaymentCreate(BaseModel):
    """Fee payment schema"""
    amount: float = Field(..., gt=0)
    payment_method: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


# =============================================================================
# GPS SCHEMAS
# =============================================================================

class GPSLocationCreate(BaseModel):
    """GPS location creation schema"""
    vehicle_id: int
    trip_id: Optional[int] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    direction: Optional[float] = None
    accuracy: Optional[float] = None
    provider: Optional[str] = "gps"
    battery_level: Optional[float] = None


class GPSLocationResponse(BaseModel):
    """GPS location response schema"""
    id: int
    vehicle_id: int
    trip_id: Optional[int] = None
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    direction: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# ALERT SCHEMAS
# =============================================================================

class AlertResponse(BaseSchema):
    """Alert response schema"""
    school_id: int
    alert_type: str
    title: str
    message: str
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    student_id: Optional[int] = None
    route_id: Optional[int] = None
    trip_id: Optional[int] = None
    severity: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    is_read: bool
    read_at: Optional[datetime] = None


class AlertResolve(BaseModel):
    """Alert resolution schema"""
    resolution_notes: Optional[str] = None


# =============================================================================
# REPORT SCHEMAS
# =============================================================================

class ReportGenerateRequest(BaseModel):
    """Report generation request"""
    report_type: str = Field(..., min_length=2)
    title: str = Field(..., min_length=2)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[dict] = None
    export_format: str = "pdf"  # pdf, excel, csv


# =============================================================================
# DASHBOARD SCHEMAS
# =============================================================================

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_vehicles: int = 0
    active_vehicles: int = 0
    total_drivers: int = 0
    active_drivers: int = 0
    total_routes: int = 0
    active_routes: int = 0
    total_students: int = 0
    active_students: int = 0
    total_fees: float = 0
    collected_fees: float = 0
    pending_fees: float = 0
    today_attendance_present: int = 0
    today_attendance_absent: int = 0
    active_trips: int = 0
    unread_alerts: int = 0


class ActivityItem(BaseModel):
    """Activity item"""
    id: int
    type: str
    title: str
    message: str
    time: str
    icon: str


# =============================================================================
# ERROR SCHEMAS
# =============================================================================

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[dict] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    message: str
    errors: List[dict]


# =============================================================================
# SUCCESS SCHEMAS
# =============================================================================

class SuccessResponse(BaseModel):
    """Success response schema"""
    success: bool = True
    message: str
    data: Optional[Any] = None


# =============================================================================
# ADDITIONAL SCHEMAS FOR ENDPOINTS
# =============================================================================

class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordChange(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None


class RouteListResponse(BaseModel):
    """Route list response"""
    items: List[Any]
    total: int
    skip: int = 0
    limit: int = 100


class StudentListResponse(BaseModel):
    """Student list response"""
    items: List[Any]
    total: int
    skip: int = 0
    limit: int = 100


class AttendanceListResponse(BaseModel):
    """Attendance list response"""
    items: List[Any]
    total: int
    skip: int = 0
    limit: int = 100


class DailyAttendanceReport(BaseModel):
    """Daily attendance report"""
    date: str
    total: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_percentage: float
    records: List[Any]


class MonthlyAttendanceReport(BaseModel):
    """Monthly attendance report"""
    year: int
    month: int
    total_days: int
    total_records: int
    stats: dict
    daily_breakdown: dict
    records: List[Any]


class FeeListResponse(BaseModel):
    """Fee list response"""
    items: List[Any]
    total: int
    skip: int = 0
    limit: int = 100


class PaymentCreate(BaseModel):
    """Payment creation schema"""
    amount: float = Field(..., gt=0)
    payment_method: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response schema"""
    id: int
    fee_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    payment_date: datetime
    collected_by: int
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    """Payment list response"""
    items: List[Any]
    total: int


class FeeSummary(BaseModel):
    """Fee summary"""
    total_fees: int
    total_amount: float
    total_paid: float
    total_pending: float
    pending_count: int
    paid_count: int
    overdue_count: int
    collection_percentage: float


class VehicleLocationResponse(BaseModel):
    """Vehicle location response"""
    vehicle_id: int
    vehicle_number: str
    latitude: Optional[float]
    longitude: Optional[float]
    speed: Optional[float]
    last_update: Optional[str]


class GPSLocationListResponse(BaseModel):
    """GPS location list response"""
    items: List[Any]
    total: int


class RouteProgressResponse(BaseModel):
    """Route progress response"""
    vehicle_id: int
    route_id: int
    current_location: dict
    completed_stops: List[dict]
    upcoming_stops: List[dict]
    total_stops: int
    completed_count: int
    progress_percentage: float


class NotificationCreate(BaseModel):
    """Notification creation schema"""
    user_id: Optional[int] = None
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    notification_type: str = "info"
    priority: str = "normal"
    data: Optional[dict] = None


class NotificationUpdate(BaseModel):
    """Notification update schema"""
    is_read: bool = False


class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: int
    user_id: Optional[int]
    title: str
    message: str
    notification_type: str
    priority: str
    is_read: bool
    is_delivered: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list response"""
    items: List[Any]
    total: int
    unread_count: int
    skip: int = 0
    limit: int = 50


class BulkNotificationCreate(BaseModel):
    """Bulk notification creation"""
    user_ids: List[int]
    title: str
    message: str
    notification_type: str = "broadcast"
    priority: str = "normal"
    data: Optional[dict] = None


# =============================================================================
# RIDERSHIP SCHEMAS
# =============================================================================

class RidershipCheckIn(BaseModel):
    student_id: int
    vehicle_id: int
    trip_id: Optional[int] = None
    stop_id: Optional[int] = None
    method: str = "manual"  # rfid, manual, qr
    rfid_card_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None


class RidershipCheckOut(BaseModel):
    student_id: int
    vehicle_id: int
    trip_id: Optional[int] = None
    stop_id: Optional[int] = None
    method: str = "manual"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class RidershipLogResponse(BaseModel):
    id: int
    student_id: int
    vehicle_id: int
    event: str
    method: str
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    student_name: Optional[str] = None
    stop_name: Optional[str] = None

    class Config:
        from_attributes = True


class RidershipStats(BaseModel):
    total_today: int = 0
    checked_in: int = 0
    checked_out: int = 0
    on_bus: int = 0


# =============================================================================
# GEOFENCE SCHEMAS
# =============================================================================

class GeofenceZoneCreate(BaseModel):
    school_id: int
    name: str
    zone_type: str = "stop"
    latitude: float
    longitude: float
    radius_meters: int = 100
    stop_id: Optional[int] = None
    route_id: Optional[int] = None
    notify_parents: bool = True
    notify_school: bool = True


class GeofenceZoneResponse(BaseModel):
    id: int
    school_id: int
    name: str
    zone_type: str
    latitude: float
    longitude: float
    radius_meters: int
    stop_id: Optional[int] = None
    route_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class GeofenceCheckRequest(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float
    trip_id: Optional[int] = None


class GeofenceEvent(BaseModel):
    zone_id: int
    zone_name: str
    zone_type: str
    vehicle_id: int
    event: str  # entered, exited
    distance_meters: float


# =============================================================================
# FIELD TRIP SCHEMAS
# =============================================================================

class FieldTripCreate(BaseModel):
    school_id: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    destination: str
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None
    departure_datetime: datetime
    return_datetime: datetime
    supervisor_name: Optional[str] = None
    supervisor_phone: Optional[str] = None
    permission_slip_required: bool = True
    cost_per_student: float = 0
    notes: Optional[str] = None
    student_ids: Optional[List[int]] = None


class FieldTripUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    title: Optional[str] = None
    destination: Optional[str] = None
    departure_datetime: Optional[datetime] = None
    return_datetime: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class FieldTripResponse(BaseModel):
    id: int
    school_id: int
    title: str
    destination: str
    departure_datetime: datetime
    return_datetime: datetime
    status: str
    total_students: int
    checked_in_count: int
    checked_out_count: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    supervisor_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FieldTripStudentAdd(BaseModel):
    student_ids: List[int]


class FieldTripStudentResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    permission_slip_received: bool
    checked_in: bool
    checked_out: bool

    class Config:
        from_attributes = True


# =============================================================================
# MAINTENANCE SCHEDULE SCHEMAS
# =============================================================================

class MaintenanceScheduleCreate(BaseModel):
    vehicle_id: int
    task_name: str
    description: Optional[str] = None
    maintenance_type: str = "service"
    interval_km: int = 5000
    interval_days: int = 90
    last_done_km: float = 0
    estimated_cost: float = 0
    assigned_to: Optional[str] = None


class MaintenanceScheduleResponse(BaseModel):
    id: int
    vehicle_id: int
    task_name: str
    maintenance_type: str
    interval_km: int
    interval_days: int
    last_done_km: float
    next_due_km: Optional[float] = None
    next_due_date: Optional[datetime] = None
    estimated_cost: float
    is_active: bool

    class Config:
        from_attributes = True


# =============================================================================
# TRIP STOP LOG SCHEMAS
# =============================================================================

class TripStopLogResponse(BaseModel):
    id: int
    trip_id: int
    stop_id: int
    stop_name: Optional[str] = None
    stop_order: int
    arrived_at: Optional[datetime] = None
    departed_at: Optional[datetime] = None
    students_boarded: int
    students_alighted: int
    delay_minutes: int
    status: str

    class Config:
        from_attributes = True