"""
SchoolRail - Utility Functions
===============================
Helper functions and utilities.
"""

import re
import hashlib
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import json


# =============================================================================
# STRING UTILITIES
# =============================================================================

def normalize_string(s: str) -> str:
    """Normalize string - lowercase, trim, remove extra spaces"""
    return " ".join(s.lower().strip().split())


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def format_phone(phone: str) -> str:
    """Format phone number"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}"
    elif len(digits) == 12:
        return f"+{digits[:2]} {digits[2:7]} {digits[7:]}"
    return phone


def format_vehicle_number(reg: str) -> str:
    """Format vehicle registration number"""
    return reg.upper().replace(' ', '')


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number (Indian)"""
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10 and len(digits) <= 12


def is_valid_vehicle_number(reg: str) -> bool:
    """Validate vehicle registration number format"""
    # Indian format: XX-XX-XXXX or XX XX XXXX
    pattern = r'^[A-Z]{2}[-\s]?[0-9]{2}[-\s]?[A-Z0-9]{4}$'
    return bool(re.match(pattern, reg.upper()))


def is_valid_license(license: str) -> bool:
    """Validate driving license number format"""
    # Various Indian formats
    pattern = r'^[A-Z]{2}[0-9]{7,14}$'
    return bool(re.match(pattern, license.upper()))


def is_strong_password(password: str) -> bool:
    """Check if password is strong"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True


# =============================================================================
# DATE/TIME UTILITIES
# =============================================================================

def format_date(d: date, format: str = "%d-%m-%Y") -> str:
    """Format date"""
    return d.strftime(format)


def format_datetime(dt: datetime, format: str = "%d-%m-%Y %H:%M") -> str:
    """Format datetime"""
    return dt.strftime(format)


def parse_date(date_str: str) -> Optional[date]:
    """Parse date from string"""
    formats = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def get_date_range(start: date, end: date) -> List[date]:
    """Get list of dates between start and end"""
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def get_month_date_range(year: int, month: int) -> tuple[date, date]:
    """Get first and last date of month"""
    first = date(year, month, 1)
    
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    
    return first, last


def get_week_date_range(week_offset: int = 0) -> tuple[date, date]:
    """Get start and end of week"""
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday() + (week_offset * 7))
    end = start + timedelta(days=6)
    return start, end


def get_age_from_dob(dob: date) -> int:
    """Calculate age from date of birth"""
    today = datetime.now().date()
    age = today.year - dob.year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age -= 1
    return age


def is_expired(expiry_date: date) -> bool:
    """Check if date has expired"""
    return expiry_date < datetime.now().date()


def days_until(date: date) -> int:
    """Days until specified date"""
    return (date - datetime.now().date()).days


# =============================================================================
# NUMBER UTILITIES
# =============================================================================

def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format currency amount"""
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage"""
    return f"{value:.{decimals}f}%"


def round_to_nearest(value: float, nearest: float = 0.5) -> float:
    """Round to nearest specified value"""
    return round(value / nearest) * nearest


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def format_file_size(bytes: int) -> str:
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


# =============================================================================
# GENERATOR UTILITIES
# =============================================================================

def generate_unique_id(prefix: str = "") -> str:
    """Generate unique ID"""
    unique = str(uuid.uuid4())[:8]
    return f"{prefix}{unique}" if prefix else unique


def generate_student_id(school_code: str, class_name: str, year: int) -> str:
    """Generate student ID"""
    return f"{school_code}{class_name}{year}{generate_unique_id()[:4]}"


def generate_otp(length: int = 6) -> str:
    """Generate OTP"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def generate_temp_password(length: int = 12) -> str:
    """Generate temporary password"""
    import random
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%"
    return ''.join(random.choice(chars) for _ in range(length))


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash string"""
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    else:
        return hashlib.sha256(text.encode()).hexdigest()


# =============================================================================
# COLLECTION UTILITIES
# =============================================================================

def group_by(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Group list of dicts by key"""
    groups = {}
    for item in items:
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups


def sort_by(items: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
    """Sort list of dicts by key"""
    return sorted(items, key=lambda x: x.get(key, ""), reverse=reverse)


def filter_by(items: List[Dict], **kwargs) -> List[Dict]:
    """Filter list of dicts by multiple criteria"""
    result = items
    for key, value in kwargs.items():
        if value is not None:
            result = [item for item in result if item.get(key) == value]
    return result


def paginate(items: List[Any], page: int = 1, per_page: int = 20) -> tuple[List[Any], int]:
    """Paginate list"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total


# =============================================================================
# JSON UTILITIES
# =============================================================================

def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safe JSON parsing"""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safe JSON stringify"""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return default


# =============================================================================
# ADDRESS UTILITIES
# =============================================================================

def format_address(
    street: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    pincode: Optional[str] = None,
    country: str = "India"
) -> str:
    """Format address"""
    parts = []
    
    if street:
        parts.append(street)
    if city:
        parts.append(city)
    if state:
        parts.append(state)
    if pincode:
        parts.append(pincode)
    if country:
        parts.append(country)
    
    return ", ".join(parts)


def parse_address(address: str) -> Dict[str, Optional[str]]:
    """Parse address string"""
    parts = [p.strip() for p in address.split(',')]
    
    result = {
        "street": parts[0] if len(parts) > 0 else None,
        "city": parts[1] if len(parts) > 1 else None,
        "state": parts[2] if len(parts) > 2 else None,
        "pincode": parts[3] if len(parts) > 3 else None,
        "country": parts[4] if len(parts) > 4 else "India"
    }
    
    return result


# =============================================================================
# GEOLOCATION UTILITIES
# =============================================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km (Haversine formula)"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def is_within_radius(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    radius_km: float = 1.0
) -> bool:
    """Check if point is within radius of another point"""
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_km


def get_bounding_box(
    latitude: float,
    longitude: float,
    radius_km: float
) -> tuple[float, float, float, float]:
    """Get bounding box for radius around point"""
    # Approximate degrees per km
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * abs(latitude / 90) if latitude else 111.0)
    
    return (
        latitude - lat_delta,  # min_lat
        latitude + lat_delta,  # max_lat
        longitude - lon_delta,  # min_lon
        longitude + lon_delta   # max_lon
    )


# =============================================================================
# NAME UTILITIES
# =============================================================================

def get_initials(name: str) -> str:
    """Get initials from name"""
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else ""


def format_full_name(first: Optional[str], last: Optional[str]) -> str:
    """Format full name"""
    if first and last:
        return f"{first} {last}"
    elif first:
        return first
    elif last:
        return last
    return ""


def split_name(full_name: str) -> tuple[Optional[str], Optional[str]]:
    """Split full name into first and last"""
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])
    elif len(parts) == 1:
        return parts[0], None
    return None, None


# =============================================================================
# ENUM UTILITIES
# =============================================================================

def enum_to_list(enum_class) -> List[str]:
    """Convert enum to list of values"""
    return [member.value for member in enum_class]


def get_enum_display(enum_value: str, enum_class) -> str:
    """Get display text for enum value"""
    try:
        return enum_class(enum_value).name.replace('_', ' ').title()
    except ValueError:
        return enum_value


# =============================================================================
# EXPORT UTILITIES
# =============================================================================

def to_csv(data: List[Dict], headers: Optional[List[str]] = None) -> str:
    """Convert list of dicts to CSV string"""
    if not data:
        return ""
    
    if not headers:
        headers = list(data[0].keys())
    
    rows = [",".join(headers)]
    
    for item in data:
        row = [str(item.get(h, "")) for h in headers]
        rows.append(",".join(row))
    
    return "\n".join(rows)


def to_json(data: Any, pretty: bool = False) -> str:
    """Convert to JSON string"""
    if pretty:
        return json.dumps(data, indent=2, default=str)
    return json.dumps(data, default=str)


# =============================================================================
# CACHE UTILITIES
# =============================================================================

class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._cache.get(key, default)
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        self._cache[key] = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=ttl)
        }
    
    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        self._cache.clear()
    
    def cleanup(self) -> None:
        """Remove expired entries"""
        now = datetime.now()
        self._cache = {
            k: v for k, v in self._cache.items()
            if v["expires"] > now
        }


# Global cache instance
cache = SimpleCache()


class ResponseHelper:
    """Helper class for API responses"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", meta: Dict = None):
        response = {"success": True, "message": message}
        if data is not None:
            response["data"] = data
        if meta:
            response["meta"] = meta
        return response
    
    @staticmethod
    def error(message: str, code: str = "ERROR", details: Dict = None):
        response = {"success": False, "message": message, "code": code}
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def paginated(data: List, page: int, limit: int, total: int):
        return {
            "success": True,
            "data": data,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }