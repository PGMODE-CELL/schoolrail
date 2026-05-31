from typing import Optional, Any, Callable
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl
    
    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "ttl": self.ttl
        }


class InMemoryCache:
    def __init__(self):
        self._cache: dict = {}
        self._hit_count = 0
        self._miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                self._hit_count += 1
                return entry.value
            else:
                del self._cache[key]
        
        self._miss_count += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        self._cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0
    
    def get_stats(self) -> dict:
        total = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total * 100) if total > 0 else 0
        return {
            "size": len(self._cache),
            "hits": self._hit_count,
            "misses": self._miss_count,
            "hit_rate": round(hit_rate, 2)
        }


cache = InMemoryCache()


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()[:32]


def cached(prefix: str, ttl: int = 300):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        wrapper.cache_clear = lambda: cache.delete(generate_cache_key(prefix, *args, **kwargs))
        return wrapper
    return decorator


def get_cached(key: str) -> Optional[Any]:
    return cache.get(key)


def set_cached(key: str, value: Any, ttl: int = 300):
    cache.set(key, value, ttl)


def invalidate_cache(key: str):
    cache.delete(key)


def clear_cache():
    cache.clear()


def get_cache_stats() -> dict:
    return cache.get_stats()


def cache_routes_list():
    from app.services.route_service import get_all_routes
    cache_key = "routes:list:all"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    routes = get_all_routes()
    cache.set(cache_key, routes, ttl=600)
    return routes


def cache_students_list(route_id: Optional[int] = None):
    from app.services.student_service import get_all_students
    cache_key = f"students:list:{route_id or 'all'}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    students = get_all_students(route_id=route_id)
    cache.set(cache_key, students, ttl=600)
    return students


def cache_vehicles_list():
    from app.services.vehicle_service import get_all_vehicles
    cache_key = "vehicles:list:all"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    vehicles = get_all_vehicles()
    cache.set(cache_key, vehicles, ttl=300)
    return vehicles


def cache_drivers_list():
    from app.services.driver_service import get_all_drivers
    cache_key = "drivers:list:all"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    drivers = get_all_drivers()
    cache.set(cache_key, drivers, ttl=600)
    return drivers


def cache_daily_attendance(date_str: str):
    from datetime import datetime
    from app.services.attendance_service import get_attendance_by_date
    cache_key = f"attendance:daily:{date_str}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        attendance_date = datetime.now().date()
    
    attendance = get_attendance_by_date(attendance_date)
    cache.set(cache_key, attendance, ttl=300)
    return attendance


def cache_fee_structures():
    from app.services.fee_service import get_all_fee_structures
    cache_key = "fees:structures:all"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    structures = get_all_fee_structures()
    cache.set(cache_key, structures, ttl=3600)
    return structures


def cache_student_fees(student_id: int):
    from app.services.fee_service import get_student_fees
    cache_key = f"fees:student:{student_id}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    fees = get_student_fees(student_id)
    cache.set(cache_key, fees, ttl=600)
    return fees


def invalidate_routes_cache():
    cache.delete("routes:list:all")


def invalidate_students_cache():
    for key in list(cache._cache.keys()):
        if key.startswith("students:"):
            cache.delete(key)


def invalidate_vehicles_cache():
    cache.delete("vehicles:list:all")


def invalidate_drivers_cache():
    cache.delete("drivers:list:all")


def invalidate_fees_cache():
    for key in list(cache._cache.keys()):
        if key.startswith("fees:"):
            cache.delete(key)


def invalidate_attendance_cache():
    for key in list(cache._cache.keys()):
        if key.startswith("attendance:"):
            cache.delete(key)
