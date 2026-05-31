"""
SchoolRail Project Summary
Complete school transportation management system
"""

PROJECT = {
    "name": "SchoolRail",
    "version": "1.0.0",
    "description": "Complete school bus tracking and transportation management system",
    "tech_stack": {
        "frontend": {
            "admin": "Next.js 14 + TypeScript + Tailwind CSS",
            "mobile": "React Native + Expo"
        },
        "backend": {
            "api": "Python FastAPI",
            "database": "PostgreSQL (SQLAlchemy)",
            "cache": "Redis"
        }
    },
    "features": {
        "admin": [
            "Dashboard with real-time analytics",
            "Vehicle management (CRUD, status tracking)",
            "Driver management (assignments, ratings)",
            "Route management (stops, optimization)",
            "Student enrollment and tracking",
            "Attendance marking and reporting",
            "Fee collection and tracking",
            "Report generation (PDF, Excel, CSV)",
            "Live GPS tracking map",
            "Settings (profile, notifications, security)"
        ],
        "mobile": {
            "parent": [
                "Dashboard with child info",
                "Live bus tracking",
                "Attendance history",
                "Fee payment",
                "Notifications"
            ],
            "driver": [
                "Route assignment",
                "Student attendance",
                "Vehicle status",
                "Navigation"
            ]
        },
        "backend": [
            "JWT Authentication",
            "Role-based access control",
            "RESTful API",
            "Real-time WebSocket",
            "Notification system",
            "GPS tracking service",
            "Analytics engine",
            "Report generation",
            "Caching layer",
            "System monitoring"
        ]
    },
    "api_endpoints": {
        "auth": ["/login", "/register", "/me"],
        "vehicles": ["/vehicles", "/vehicles/:id"],
        "drivers": ["/drivers", "/drivers/:id"],
        "students": ["/students", "/students/:id"],
        "routes": ["/routes", "/routes/:id"],
        "attendance": ["/attendance", "/attendance/:id"],
        "fees": ["/fees", "/fees/:id", "/fees/:id/pay"],
        "analytics": ["/analytics/dashboard", "/analytics/vehicles", "/analytics/attendance"],
        "gps": ["/gps/vehicles", "/gps/vehicles/:id"],
        "notifications": ["/notifications", "/notifications/:id/read"]
    }
}

if __name__ == "__main__":
    print(f"SchoolRail v{PROJECT['version']}")
    print(f"Description: {PROJECT['description']}")
    print(f"Tech Stack: {PROJECT['tech_stack']}")