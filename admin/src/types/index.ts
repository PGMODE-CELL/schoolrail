/**
 * SchoolRail - Admin Types
 * TypeScript type definitions for admin dashboard
 */

export interface User {
  id: number;
  uuid?: string;
  username: string;
  email?: string;
  phone?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  role: 'admin' | 'school_admin' | 'driver' | 'parent' | 'teacher';
  school_id?: number;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string;
  last_login?: string;
}

export interface School {
  id: number;
  uuid?: string;
  name: string;
  code: string;
  display_name?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  pincode?: string;
  phone?: string;
  email?: string;
  logo_url?: string;
  primary_color?: string;
  timezone?: string;
  currency?: string;
  is_active: boolean;
  created_at?: string;
}

export interface Vehicle {
  id: number;
  uuid?: string;
  reg_number: string;
  reg_state?: string;
  vehicle_type: string;
  make?: string;
  model?: string;
  year?: number;
  color?: string;
  seating_capacity: number;
  insurance_number?: string;
  insurance_expiry?: string;
  permit_number?: string;
  permit_expiry?: string;
  fitness_certificate?: string;
  fitness_expiry?: string;
  gps_device_id?: string;
  gps_installed: boolean;
  status: 'active' | 'maintenance' | 'inactive';
  is_available: boolean;
  current_odometer?: number;
  fuel_level?: number;
  total_km?: number;
  created_at?: string;
}

export interface Driver {
  id: number;
  uuid?: string;
  first_name: string;
  last_name?: string;
  full_name: string;
  photo_url?: string;
  phone: string;
  email?: string;
  address?: string;
  license_number: string;
  license_type?: string;
  license_expiry: string;
  total_experience_years?: number;
  is_background_verified: boolean;
  status: 'active' | 'inactive' | 'on_leave';
  is_available: boolean;
  rating: number;
  safe_driving_score: number;
  total_trips: number;
  vehicle_id?: number;
  created_at?: string;
}

export interface Route {
  id: number;
  uuid?: string;
  name: string;
  route_code: string;
  description?: string;
  start_point: string;
  end_point: string;
  total_distance_km?: number;
  estimated_time_minutes?: number;
  morning_pickup_time?: string;
  evening_drop_time?: string;
  operating_days?: string;
  geofence_enabled: boolean;
  status: 'active' | 'inactive';
  base_fare?: number;
  vehicle_id?: number;
  driver_id?: number;
  stops?: Stop[];
  created_at?: string;
}

export interface Stop {
  id: number;
  name: string;
  address?: string;
  landmark?: string;
  latitude: number;
  longitude: number;
  stop_order: number;
  estimated_arrival_time?: string;
  is_active: boolean;
}

export interface Student {
  id: number;
  uuid?: string;
  first_name: string;
  last_name?: string;
  full_name?: string;
  student_id: string;
  class_name: string;
  section?: string;
  photo_url?: string;
  father_name?: string;
  father_phone?: string;
  mother_name?: string;
  mother_phone?: string;
  route_id?: number;
  pickup_stop_id?: number;
  drop_stop_id?: number;
  pickup_time?: string;
  drop_time?: string;
  transport_fees?: number;
  status: 'active' | 'inactive';
  created_at?: string;
}

export interface Attendance {
  id: number;
  student_id: number;
  trip_id?: number;
  date: string;
  trip_type: 'pickup' | 'drop';
  status: 'present' | 'absent' | 'late' | 'excused';
  stop_name?: string;
  time?: string;
  notes?: string;
  source?: string;
  created_at?: string;
}

export interface Fee {
  id: number;
  uuid?: string;
  student_id: number;
  fee_type: string;
  title: string;
  description?: string;
  amount: number;
  gst_rate?: number;
  gst_amount?: number;
  total_amount?: number;
  final_amount: number;
  due_date: string;
  status: 'pending' | 'paid' | 'overdue' | 'partial';
  paid_amount: number;
  paid_date?: string;
  payment_method?: string;
  transaction_id?: string;
  created_at?: string;
}

export interface Trip {
  id: number;
  uuid?: string;
  vehicle_id: number;
  driver_id?: number;
  route_id: number;
  trip_type: string;
  scheduled_start_time: string;
  actual_start_time?: string;
  scheduled_end_time?: string;
  actual_end_time?: string;
  status: 'scheduled' | 'ongoing' | 'completed' | 'cancelled';
  students_count?: number;
  distance_km?: number;
  notes?: string;
  created_at?: string;
}

export interface GPSLocation {
  id: number;
  vehicle_id: number;
  trip_id?: number;
  latitude: number;
  longitude: number;
  speed_kmh?: number;
  direction?: number;
  created_at: string;
}

export interface Alert {
  id: number;
  uuid?: string;
  alert_type: string;
  title: string;
  message: string;
  vehicle_id?: number;
  driver_id?: number;
  student_id?: number;
  route_id?: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  is_read: boolean;
  is_resolved: boolean;
  created_at: string;
  resolved_at?: string;
}

export interface MaintenanceRecord {
  id: number;
  vehicle_id: number;
  maintenance_type: string;
  title: string;
  description?: string;
  scheduled_date?: string;
  completed_date?: string;
  odometer_reading?: number;
  cost?: number;
  vendor_name?: string;
  created_at?: string;
}

export interface DashboardStats {
  total_students: number;
  active_students: number;
  total_vehicles: number;
  active_vehicles: number;
  total_drivers: number;
  active_drivers: number;
  total_routes: number;
  active_routes: number;
  today_trips: number;
  completed_trips: number;
  ongoing_trips: number;
  attendance_rate: number;
  fee_collection_rate: number;
  total_revenue: number;
  pending_fees: number;
}

export interface PaginationParams {
  page: number;
  limit: number;
  total: number;
}

export interface ApiResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}