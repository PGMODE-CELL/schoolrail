"""
SchoolRail - Database Models
=============================
All database models for the application.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum, Index, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base


# =============================================================================
# ENUMS - Database level enums
# =============================================================================

class UserRole:
    ADMIN = "admin"
    SCHOOL_ADMIN = "school_admin"
    DRIVER = "driver"
    PARENT = "parent"
    STUDENT = "student"


class VehicleStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class DriverStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class AttendanceStatus:
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class FeeStatus:
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


# =============================================================================
# SCHOOL MODEL
# =============================================================================

class School(Base):
    """School/Institution model"""
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(255))
    tagline = Column(String(255))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    pincode = Column(String(20))
    phone = Column(String(20))
    alternate_phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    logo_url = Column(String(500))
    primary_color = Column(String(7), default="#6366f1")
    secondary_color = Column(String(7), default="#8b5cf6")
    timezone = Column(String(50), default="Asia/Kolkata")
    currency = Column(String(10), default="INR")
    language = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    features = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="school", lazy="dynamic")
    vehicles = relationship("Vehicle", back_populates="school", lazy="dynamic")
    drivers = relationship("Driver", back_populates="school", lazy="dynamic")
    routes = relationship("Route", back_populates="school", lazy="dynamic")
    students = relationship("Student", back_populates="school", lazy="dynamic")
    fees = relationship("Fee", back_populates="school", lazy="dynamic")
    trips = relationship("Trip", back_populates="school", lazy="dynamic")
    alerts = relationship("Alert", back_populates="school", lazy="dynamic")
    
    def __repr__(self):
        return f"<School {self.name}>"


# =============================================================================
# USER MODEL
# =============================================================================

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    
    # Authentication
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200))
    avatar_url = Column(String(500))
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    address = Column(Text)
    
    # Role
    role = Column(String(20), nullable=False, default=UserRole.PARENT)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="users")
    driver_profile = relationship("Driver", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def name(self):
        return self.full_name or f"{self.first_name} {self.last_name}" if self.first_name else self.username


# =============================================================================
# VEHICLE MODEL
# =============================================================================

class Vehicle(Base):
    """Vehicle model for school fleet"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    
    # Registration
    reg_number = Column(String(20), unique=True, nullable=False, index=True)
    reg_state = Column(String(50))
    reg_date = Column(DateTime)
    
    # Vehicle Details
    vehicle_type = Column(String(20), nullable=False)  # bus, van, mini_bus
    make = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)
    color = Column(String(50))
    chassis_number = Column(String(50))
    engine_number = Column(String(50))
    
    # Capacity
    seating_capacity = Column(Integer, nullable=False)
    standing_capacity = Column(Integer, default=0)
    total_capacity = Column(Integer)
    
    # Documents
    insurance_number = Column(String(50))
    insurance_expiry = Column(DateTime)
    permit_number = Column(String(50))
    permit_expiry = Column(DateTime)
    fitness_certificate = Column(String(50))
    fitness_expiry = Column(DateTime)
    pollution_certificate = Column(String(50))
    pollution_expiry = Column(DateTime)
    
    # Device
    gps_device_id = Column(String(50))
    gps_device_number = Column(String(50))
    gps_sim_number = Column(String(20))
    gps_installed = Column(Boolean, default=False)
    
    # Image
    front_image = Column(String(500))
    back_image = Column(String(500))
    side_image = Column(String(500))
    
    # Status
    status = Column(String(20), default=VehicleStatus.ACTIVE)
    is_available = Column(Boolean, default=True)
    
    # Maintenance
    last_service_date = Column(DateTime)
    next_service_date = Column(DateTime)
    total_km = Column(Float, default=0)
    
    # Cost
    purchase_date = Column(DateTime)
    purchase_price = Column(Float)
    current_value = Column(Float)
    
    # Features (JSON)
    features = Column(Text)  # AC, WiFi, CCTV
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="vehicles")
    drivers = relationship("Driver", back_populates="vehicle", lazy="dynamic")
    routes = relationship("Route", back_populates="vehicle", lazy="dynamic")
    gps_locations = relationship("GPSLocation", back_populates="vehicle", lazy="dynamic")
    trips = relationship("Trip", back_populates="vehicle", lazy="dynamic")
    alerts = relationship("Alert", back_populates="vehicle", lazy="dynamic")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle", lazy="dynamic")
    
    def __repr__(self):
        return f"<Vehicle {self.reg_number}>"


# =============================================================================
# DRIVER MODEL
# =============================================================================

class Driver(Base):
    """Driver model"""
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    
    # Personal
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    full_name = Column(String(200))
    photo_url = Column(String(500))
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    
    # Contact
    phone = Column(String(20), nullable=False)
    alternate_phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    
    # License
    license_number = Column(String(50), nullable=False)
    license_type = Column(String(20))  # LMV, HMV
    license_expiry = Column(DateTime, nullable=False)
    license_image = Column(String(500))
    
    # Experience
    total_experience_years = Column(Integer)
    previous_employer = Column(String(200))
    
    # Background
    is_background_verified = Column(Boolean, default=False)
    police_clearance = Column(Boolean, default=False)
    
    # Emergency
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(50))
    
    # Status
    status = Column(String(20), default=DriverStatus.ACTIVE)
    is_available = Column(Boolean, default=True)
    
    # Performance
    rating = Column(Float, default=5.0)
    total_trips = Column(Integer, default=0)
    safe_driving_score = Column(Integer, default=100)
    
    # Salary
    salary_type = Column(String(20))
    salary_amount = Column(Float)
    bank_account_number = Column(String(30))
    bank_name = Column(String(100))
    ifsc_code = Column(String(20))
    
    # Timestamps
    joined_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="drivers")
    user = relationship("User", back_populates="driver_profile")
    vehicle = relationship("Vehicle", back_populates="drivers")
    routes = relationship("Route", back_populates="driver", lazy="dynamic")
    trips = relationship("Trip", back_populates="driver", lazy="dynamic")
    attendances = relationship("DriverAttendance", back_populates="driver", lazy="dynamic")
    
    def __repr__(self):
        return f"<Driver {self.full_name}>"
    
    @property
    def name(self):
        return self.full_name or f"{self.first_name} {self.last_name}"


# =============================================================================
# ROUTE MODEL
# =============================================================================

class Route(Base):
    """Route model"""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    
    # Route Info
    name = Column(String(200), nullable=False)
    route_code = Column(String(20), nullable=False)
    description = Column(Text)
    
    # Start/End
    start_point = Column(String(200), nullable=False)
    start_latitude = Column(Float)
    start_longitude = Column(Float)
    end_point = Column(String(200), nullable=False)
    end_latitude = Column(Float)
    end_longitude = Column(Float)
    
    # Distance & Time
    total_distance_km = Column(Float)
    estimated_time_minutes = Column(Integer)
    
    # Schedule
    morning_pickup_time = Column(String(10))
    evening_drop_time = Column(String(10))
    
    # Operating Days
    operating_days = Column(String(50))  # JSON
    
    # Geofence
    geofence_enabled = Column(Boolean, default=False)
    geofence_radius_meters = Column(Integer, default=100)
    waypoints = Column(Text)  # JSON
    
    # Status
    status = Column(String(20), default="active")
    is_primary = Column(Boolean, default=False)
    
    # Fare
    base_fare = Column(Float)
    per_km_rate = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="routes")
    vehicle = relationship("Vehicle", back_populates="routes")
    driver = relationship("Driver", back_populates="routes")
    stops = relationship("Stop", back_populates="route", order_by="Stop.stop_order", lazy="dynamic")
    students = relationship("StudentRouteAssignment", back_populates="route", lazy="dynamic")
    trips = relationship("Trip", back_populates="route", lazy="dynamic")
    
    def __repr__(self):
        return f"<Route {self.name}>"


# =============================================================================
# STOP MODEL
# =============================================================================

class Stop(Base):
    """Stop model"""
    __tablename__ = "stops"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    
    # Details
    name = Column(String(200), nullable=False)
    address = Column(Text)
    landmark = Column(String(200))
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Sequence
    stop_order = Column(Integer, nullable=False)
    
    # Timing
    estimated_arrival_time = Column(String(10))
    pickup_time_from = Column(String(10))
    pickup_time_to = Column(String(10))
    drop_time_from = Column(String(10))
    drop_time_to = Column(String(10))
    
    # Geofence
    geofence_enabled = Column(Boolean, default=False)
    geofence_radius_meters = Column(Integer, default=50)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    route = relationship("Route", back_populates="stops")
    student_pickups = relationship("StudentRouteAssignment", foreign_keys="StudentRouteAssignment.pickup_stop_id", back_populates="pickup_stop")
    student_drops = relationship("StudentRouteAssignment", foreign_keys="StudentRouteAssignment.drop_stop_id", back_populates="drop_stop")
    
    def __repr__(self):
        return f"<Stop {self.name}>"


# =============================================================================
# STUDENT MODEL
# =============================================================================

class Student(Base):
    """Student model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    
    # Personal
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    full_name = Column(String(200))
    photo_url = Column(String(500))
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    blood_group = Column(String(10))
    
    # Academic
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    roll_number = Column(String(20))
    class_name = Column(String(20), nullable=False, index=True)
    section = Column(String(10))
    admission_date = Column(DateTime)
    academic_year = Column(String(20))
    
    # Contact
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    
    # Parents
    father_name = Column(String(200))
    father_phone = Column(String(20))
    father_email = Column(String(255))
    mother_name = Column(String(200))
    mother_phone = Column(String(20))
    mother_email = Column(String(255))
    guardian_name = Column(String(200))
    guardian_phone = Column(String(20))
    guardian_relation = Column(String(50))
    
    # Emergency
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    medical_conditions = Column(Text)
    allergies = Column(Text)
    
    # Transport
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    pickup_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    drop_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    pickup_time = Column(String(10))
    drop_time = Column(String(10))
    transport_fees = Column(Float)
    
    # Status
    status = Column(String(20), default="active")
    is_transport_applicable = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="students")
    route = relationship("Route", foreign_keys=[route_id])
    pickup_stop = relationship("Stop", foreign_keys=[pickup_stop_id])
    drop_stop = relationship("Stop", foreign_keys=[drop_stop_id])
    attendances = relationship("Attendance", back_populates="student", lazy="dynamic")
    fees = relationship("Fee", back_populates="student", lazy="dynamic")
    route_assignments = relationship("StudentRouteAssignment", back_populates="student", lazy="dynamic")
    alerts = relationship("Alert", back_populates="student", lazy="dynamic")
    
    def __repr__(self):
        return f"<Student {self.full_name}>"
    
    @property
    def name(self):
        return self.full_name or f"{self.first_name} {self.last_name}"


class StudentRouteAssignment(Base):
    """Student Route Assignment"""
    __tablename__ = "student_route_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    pickup_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    drop_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    
    pickup_time = Column(String(10))
    drop_time = Column(String(10))
    
    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_till = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="route_assignments")
    route = relationship("Route", back_populates="students")
    pickup_stop = relationship("Stop", foreign_keys=[pickup_stop_id], back_populates="student_pickups")
    drop_stop = relationship("Stop", foreign_keys=[drop_stop_id], back_populates="student_drops")


# =============================================================================
# TRIP MODEL
# =============================================================================

class Trip(Base):
    """Trip model"""
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    
    trip_type = Column(String(20), nullable=False)  # morning_pickup, evening_drop
    
    scheduled_start_time = Column(DateTime)
    actual_start_time = Column(DateTime)
    scheduled_end_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    
    start_odometer = Column(Float)
    end_odometer = Column(Float)
    distance_km = Column(Float)
    
    start_location = Column(String(200))
    end_location = Column(String(200))
    
    status = Column(String(20))  # scheduled, in_progress, completed, cancelled
    
    students_count = Column(Integer, default=0)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="trips")
    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    route = relationship("Route", back_populates="trips")
    attendances = relationship("Attendance", back_populates="trip", lazy="dynamic")


# =============================================================================
# ATTENDANCE MODEL
# =============================================================================

class Attendance(Base):
    """Attendance model"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    
    date = Column(DateTime, nullable=False, index=True)
    trip_type = Column(String(20), nullable=False)
    
    status = Column(String(20), nullable=False)
    
    scheduled_time = Column(String(10))
    actual_time = Column(String(10))
    
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    stop_name = Column(String(200))
    
    notes = Column(Text)
    source = Column(String(20))  # manual, auto, rfid
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="attendances")
    trip = relationship("Trip", back_populates="attendances")
    stop = relationship("Stop")


# =============================================================================
# GPS LOCATION MODEL
# =============================================================================

class GPSLocation(Base):
    """GPS Location model"""
    __tablename__ = "gps_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    
    speed_kmh = Column(Float)
    direction = Column(Float)
    
    accuracy = Column(Float)
    provider = Column(String(20))
    
    is_valid = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="gps_locations")
    trip = relationship("Trip")


# =============================================================================
# FEE MODEL
# =============================================================================

class Fee(Base):
    """Fee model"""
    __tablename__ = "fees"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    fee_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    amount = Column(Float, nullable=False)
    gst_rate = Column(Float, default=0)
    gst_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)
    
    due_date = Column(DateTime)
    issue_date = Column(DateTime)
    
    status = Column(String(20), default=FeeStatus.PENDING)
    
    paid_amount = Column(Float, default=0)
    paid_date = Column(DateTime)
    payment_method = Column(String(20))
    transaction_id = Column(String(100))
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="fees")
    student = relationship("Student", back_populates="fees")
    payments = relationship("Payment", back_populates="fee", lazy="dynamic")


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    fee_id = Column(Integer, ForeignKey("fees.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    payment_method = Column(String(20), nullable=False)
    transaction_id = Column(String(100))
    
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(20))
    
    gateway_response = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fee = relationship("Fee", back_populates="payments")


# =============================================================================
# ALERT MODEL
# =============================================================================

class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    
    alert_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    
    severity = Column(String(20))  # low, medium, high, critical
    
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(200))
    
    extra_data = Column(Text)  # JSON
    
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    school = relationship("School", back_populates="alerts")
    vehicle = relationship("Vehicle", back_populates="alerts")
    student = relationship("Student", back_populates="alerts")


# =============================================================================
# MAINTENANCE RECORD MODEL
# =============================================================================

class MaintenanceRecord(Base):
    """Maintenance Record model"""
    __tablename__ = "maintenance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    maintenance_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    odometer_reading = Column(Float)
    
    cost = Column(Float)
    vendor_name = Column(String(200))
    vendor_phone = Column(String(20))
    
    parts_replaced = Column(Text)  # JSON
    
    next_due_date = Column(DateTime)
    next_due_km = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")


# =============================================================================
# DRIVER ATTENDANCE MODEL
# =============================================================================

class DriverAttendance(Base):
    """Driver Attendance model"""
    __tablename__ = "driver_attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    
    date = Column(DateTime, nullable=False, index=True)
    
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    
    status = Column(String(20))  # present, absent, leave
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    driver = relationship("Driver", back_populates="attendances")


# =============================================================================
# NOTIFICATION MODEL
# =============================================================================

class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    
    notification_type = Column(String(20), nullable=False)  # sms, email, push
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    
    target_type = Column(String(20))
    target_id = Column(Integer)
    
    data = Column(Text)  # JSON
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    
    delivery_status = Column(String(20))  # pending, sent, failed
    
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================================
# RIDERSHIP LOG MODEL (RFID Check-in/out)
# =============================================================================

class RidershipLog(Base):
    """Student bus check-in/out tracking (competitor's paid add-on)"""
    __tablename__ = "ridership_logs"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)

    event = Column(String(10), nullable=False)  # check_in, check_out
    method = Column(String(20), default="manual")  # rfid, manual, qr
    rfid_card_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
    photo_url = Column(String(500))

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    school = relationship("School")
    student = relationship("Student")
    vehicle = relationship("Vehicle")
    trip = relationship("Trip")
    stop = relationship("Stop")


# =============================================================================
# GEOFENCE ZONES MODEL
# =============================================================================

class GeofenceZone(Base):
    """Geofence zones for stop/school proximity alerts"""
    __tablename__ = "geofence_zones"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    name = Column(String(200), nullable=False)
    zone_type = Column(String(20), nullable=False)  # stop, school, custom
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, nullable=False, default=100)
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)

    notify_parents = Column(Boolean, default=True)
    notify_school = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    school = relationship("School")
    stop = relationship("Stop")
    route = relationship("Route")


# =============================================================================
# FIELD TRIP MODEL
# =============================================================================

class FieldTrip(Base):
    """Field trip / excursion management"""
    __tablename__ = "field_trips"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)

    title = Column(String(200), nullable=False)
    description = Column(Text)
    destination = Column(String(200), nullable=False)
    destination_latitude = Column(Float)
    destination_longitude = Column(Float)

    departure_datetime = Column(DateTime, nullable=False)
    return_datetime = Column(DateTime, nullable=False)
    actual_departure = Column(DateTime)
    actual_return = Column(DateTime)

    total_students = Column(Integer, default=0)
    checked_in_count = Column(Integer, default=0)
    checked_out_count = Column(Integer, default=0)
    status = Column(String(20), default="scheduled")  # scheduled, ongoing, completed, cancelled

    supervisor_name = Column(String(200))
    supervisor_phone = Column(String(20))
    permission_slip_required = Column(Boolean, default=True)
    cost_per_student = Column(Float, default=0)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    school = relationship("School")
    vehicle = relationship("Vehicle")
    driver = relationship("Driver")
    students = relationship("FieldTripStudent", back_populates="field_trip", lazy="dynamic")


class FieldTripStudent(Base):
    """Student enrollment in a field trip"""
    __tablename__ = "field_trip_students"

    id = Column(Integer, primary_key=True, index=True)
    field_trip_id = Column(Integer, ForeignKey("field_trips.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    permission_slip_received = Column(Boolean, default=False)
    checked_in = Column(Boolean, default=False)
    checked_in_time = Column(DateTime)
    checked_out = Column(Boolean, default=False)
    checked_out_time = Column(DateTime)

    emergency_contact = Column(String(20))
    medical_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    field_trip = relationship("FieldTrip", back_populates="students")
    student = relationship("Student")


# =============================================================================
# MAINTENANCE SCHEDULE MODEL (recurring maintenance)
# =============================================================================

class MaintenanceSchedule(Base):
    """Scheduled recurring maintenance tasks"""
    __tablename__ = "maintenance_schedules"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    task_name = Column(String(200), nullable=False)
    description = Column(Text)
    maintenance_type = Column(String(50), nullable=False)  # oil_change, tire_rotation, inspection, service, other
    interval_km = Column(Integer, default=5000)
    interval_days = Column(Integer, default=90)

    last_done_km = Column(Float, default=0)
    last_done_date = Column(DateTime)
    next_due_km = Column(Float)
    next_due_date = Column(DateTime)

    assigned_to = Column(String(200))
    estimated_cost = Column(Float)
    is_recurring = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle = relationship("Vehicle")


# =============================================================================
# TRIP STOP LOG (for tracking stop-by-stop progress)
# =============================================================================

class TripStopLog(Base):
    """Record when a bus reaches/leaves each stop on a trip"""
    __tablename__ = "trip_stop_logs"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)

    arrived_at = Column(DateTime)
    departed_at = Column(DateTime)
    students_boarded = Column(Integer, default=0)
    students_alighted = Column(Integer, default=0)
    delay_minutes = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, arrived, departed, skipped

    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip")
    stop = relationship("Stop")