"""
SchoolRail - Database Seed Data
================================
Seed script to populate initial demo data.
"""

import os
import random
from datetime import datetime, timedelta
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.models import (
    User, School, Vehicle, Driver, Route, Student,
    Attendance, Trip, Fee, Alert, GPSLocation
)


def seed():
    """Seed the database with demo data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        db.close()
        print("Database already seeded. Skipping.")
        return

    school = School(
        name="Demo Public School",
        code="DPS001",
        display_name="Demo Public School",
        address="Dwarka Sector 12, New Delhi",
        city="New Delhi",
        state="Delhi",
        country="India",
        pincode="110078",
        phone="+911123456789",
        email="info@demopublic.edu",
        timezone="Asia/Kolkata",
        currency="INR",
        is_active=True,
    )
    db.add(school)
    db.flush()

    users_data = [
        {"username": "admin", "email": "admin@schoolrail.com", "full_name": "Administrator", "role": "admin", "phone": "+919876543210"},
        {"username": "driver1", "email": "driver1@schoolrail.com", "full_name": "Rajesh Kumar", "role": "driver", "phone": "+919876543211"},
        {"username": "parent1", "email": "parent1@schoolrail.com", "full_name": "Priya Sharma", "role": "parent", "phone": "+919876543212"},
    ]
    for ud in users_data:
        u = User(
            school_id=school.id,
            password_hash=get_password_hash("admin123"),
            first_name=ud["full_name"].split()[0],
            last_name=ud["full_name"].split()[-1],
            is_active=True,
            is_verified=True,
            **ud,
        )
        db.add(u)
    db.flush()

    vehicles_data = [
        {"reg_number": "DL-01-AB-1234", "vehicle_type": "Bus", "make": "Ashok Leyland",
         "model": "Urbanist", "year": 2022, "seating_capacity": 50, "color": "Yellow",
         "status": "active", "is_available": True, "gps_installed": True},
        {"reg_number": "DL-01-CD-5678", "vehicle_type": "Bus", "make": "Tata",
         "model": "Starbus", "year": 2021, "seating_capacity": 45, "color": "Yellow",
         "status": "active", "is_available": True, "gps_installed": True},
        {"reg_number": "DL-01-EF-9012", "vehicle_type": "Minibus", "make": "Eicher",
         "model": "Starline", "year": 2023, "seating_capacity": 30, "color": "Orange",
         "status": "active", "is_available": True, "gps_installed": True},
    ]
    vehicles = []
    for vd in vehicles_data:
        v = Vehicle(school_id=school.id, **vd)
        db.add(v)
        vehicles.append(v)
    db.flush()

    drivers_data = [
        {"first_name": "Rajesh", "last_name": "Kumar", "phone": "+919876543210",
         "license_number": "DL-0123456789",
         "license_expiry": (datetime.now() + timedelta(days=365)).date(),
         "total_experience_years": 5, "status": "active", "is_available": True,
         "rating": 4.5, "safe_driving_score": 95},
        {"first_name": "Mohammad", "last_name": "Imran", "phone": "+919876543211",
         "license_number": "DL-0123456790",
         "license_expiry": (datetime.now() + timedelta(days=200)).date(),
         "total_experience_years": 3, "status": "active", "is_available": True,
         "rating": 4.2, "safe_driving_score": 90},
        {"first_name": "Suresh", "last_name": "Patel", "phone": "+919876543212",
         "license_number": "DL-0123456791",
         "license_expiry": (datetime.now() + timedelta(days=150)).date(),
         "total_experience_years": 7, "status": "active", "is_available": True,
         "rating": 4.8, "safe_driving_score": 98},
    ]
    for dd in drivers_data:
        d = Driver(school_id=school.id, vehicle_id=vehicles[drivers_data.index(dd)].id, **dd)
        db.add(d)
    db.flush()

    routes_data = [
        {"name": "Route R1 - Dwarka", "route_code": "R1",
         "start_point": "Dwarka Sector 12", "end_point": "Demo Public School",
         "total_distance_km": 8.5, "estimated_time_minutes": 45,
         "morning_pickup_time": "07:00", "evening_drop_time": "14:30",
         "status": "active", "base_fare": 2500},
        {"name": "Route R2 - Vasant Kunj", "route_code": "R2",
         "start_point": "Vasant Kunj Sector 5", "end_point": "Demo Public School",
         "total_distance_km": 12.0, "estimated_time_minutes": 60,
         "morning_pickup_time": "06:45", "evening_drop_time": "15:00",
         "status": "active", "base_fare": 2800},
        {"name": "Route R3 - Janakpuri", "route_code": "R3",
         "start_point": "Janakpuri D-Block", "end_point": "Demo Public School",
         "total_distance_km": 10.0, "estimated_time_minutes": 50,
         "morning_pickup_time": "07:15", "evening_drop_time": "14:45",
         "status": "active", "base_fare": 2600},
    ]
    for rd in routes_data:
        r = Route(school_id=school.id, **rd)
        db.add(r)
    db.flush()

    routes = db.query(Route).filter(Route.school_id == school.id).all()

    students_data = [
        {"first_name": "Aryan", "last_name": "Sharma", "student_id": "STU001",
         "class_name": "Class 5", "section": "A",
         "father_name": "Rajesh Sharma", "father_phone": "+919876543210",
         "transport_fees": 2500, "status": "active"},
        {"first_name": "Ananya", "last_name": "Sharma", "student_id": "STU002",
         "class_name": "Class 3", "section": "B",
         "father_name": "Rajesh Sharma", "father_phone": "+919876543210",
         "transport_fees": 2500, "status": "active"},
        {"first_name": "Rahul", "last_name": "Verma", "student_id": "STU003",
         "class_name": "Class 4", "section": "A",
         "father_name": "Suresh Verma", "father_phone": "+919876543211",
         "transport_fees": 2500, "status": "active"},
        {"first_name": "Priya", "last_name": "Singh", "student_id": "STU004",
         "class_name": "Class 5", "section": "B",
         "father_name": "Amit Singh", "father_phone": "+919876543212",
         "transport_fees": 2800, "status": "active"},
        {"first_name": "Amit", "last_name": "Kumar", "student_id": "STU005",
         "class_name": "Class 6", "section": "A",
         "father_name": "Raj Kumar", "father_phone": "+919876543213",
         "transport_fees": 2500, "status": "active"},
    ]
    for i, sd in enumerate(students_data):
        s = Student(school_id=school.id, route_id=routes[i % len(routes)].id, **sd)
        db.add(s)
    db.flush()

    today = datetime.now().date()
    students = db.query(Student).filter(Student.school_id == school.id).all()
    for s in students:
        for trip_type in ["morning_pickup", "evening_drop"]:
            status = "present" if random.random() > 0.15 else "absent"
            if status == "present" and random.random() > 0.8:
                status = "late"
            a = Attendance(
                student_id=s.id,
                date=today,
                trip_type=trip_type,
                status=status,
                scheduled_time=datetime.now(),
                actual_time=datetime.now(),
                source="seed",
            )
            db.add(a)

    for i, s in enumerate(students):
        fee = Fee(
            school_id=school.id,
            student_id=s.id,
            fee_type="Transport Fee",
            title="Monthly Transport Fee",
            amount=s.transport_fees,
            total_amount=s.transport_fees,
            final_amount=s.transport_fees,
            paid_amount=s.transport_fees if i % 3 != 0 else 0,
            due_date=today + timedelta(days=15),
            status="paid" if i % 3 != 0 else "pending",
        )
        db.add(fee)

    drivers = db.query(Driver).filter(Driver.school_id == school.id).all()
    for i, v in enumerate(vehicles):
        driver = drivers[i % len(drivers)]
        t = Trip(
            school_id=school.id,
            vehicle_id=v.id,
            driver_id=driver.id,
            route_id=routes[i % len(routes)].id,
            trip_type="morning_pickup",
            scheduled_start_time=datetime.now(),
            status="completed" if i < 2 else "ongoing",
            students_count=2,
        )
        db.add(t)

    for v in vehicles:
        gl = GPSLocation(
            vehicle_id=v.id,
            latitude=28.5929 + random.uniform(-0.01, 0.01),
            longitude=77.0461 + random.uniform(-0.01, 0.01),
            speed_kmh=random.uniform(0, 40),
            direction=random.uniform(0, 360),
            is_valid=True,
        )
        db.add(gl)

    alert = Alert(
        school_id=school.id,
        alert_type="delay",
        title="Route R2 Delayed",
        message="Route R2 (Vasant Kunj) is running 10 minutes late due to traffic",
        severity="medium",
        is_resolved=False,
        is_read=False,
    )
    db.add(alert)

    db.commit()
    db.close()
    print(f"Seeded: school, admin (admin/admin123), {len(vehicles)} vehicles, {len(drivers_data)} drivers, "
          f"{len(routes_data)} routes, {len(students_data)} students, attendance, fees, trips, gps, alerts")


def main():
    os.environ.setdefault("DATABASE_URL", "sqlite:///./schoolrail.db")
    seed()


if __name__ == "__main__":
    main()