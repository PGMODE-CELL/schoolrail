'use client';

import React, { useState, useEffect } from 'react';
import { MapPin, Bus, Navigation, Clock, AlertCircle, RefreshCw, Filter, Search, Phone, User, Route, Loader2 } from 'lucide-react';
import { gpsAPI } from '@/lib/api';

interface VehicleLocation {
  id: number;
  vehicle_number: string;
  driver: string;
  route: string;
  lat: number;
  lng: number;
  speed: number;
  status: 'moving' | 'stopped' | 'idle';
  last_update: string;
  students: number;
}

export default function MapPage() {
  const [vehicles, setVehicles] = useState<VehicleLocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVehicle, setSelectedVehicle] = useState<VehicleLocation | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchVehicles = async () => {
    setLoading(true);
    try {
      const res = await gpsAPI.latest();
      const data = Array.isArray(res.data) ? res.data : (res.data?.vehicles || res.data?.data || []);
      setVehicles(data.map((v: any) => ({
        id: v.id || v.vehicle_id || Math.random(),
        vehicle_number: v.vehicle_number || v.registration_number || `Vehicle #${v.id || ''}`,
        driver: v.driver_name || v.driver || 'Unknown',
        route: v.route_name || v.route || 'Unknown Route',
        lat: v.latitude || v.lat || 0,
        lng: v.longitude || v.lng || 0,
        speed: v.speed || 0,
        status: v.status || 'idle',
        last_update: v.last_update || v.timestamp || 'N/A',
        students: v.students || v.student_count || 0,
      })));
    } catch {
      setVehicles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchVehicles(); }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'moving': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'stopped': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'idle': return 'bg-slate-50 text-slate-600 border-slate-200';
      default: return 'bg-slate-50 text-slate-600 border-slate-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'moving': return <Navigation size={14} className="text-emerald-500" />;
      case 'stopped': return <Clock size={14} className="text-amber-500" />;
      case 'idle': return <AlertCircle size={14} className="text-slate-400" />;
      default: return null;
    }
  };

  const filteredVehicles = vehicles.filter(v => 
    v.vehicle_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.driver.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.route.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Live Tracking</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Real-time vehicle monitoring and location tracking</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center gap-2 px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
            <Filter size={18} />
            Filters
          </button>
          <button onClick={fetchVehicles} disabled={loading} className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50">
            {loading ? <Loader2 size={18} className="animate-spin" /> : <RefreshCw size={18} />}
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
              <Bus className="text-blue-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{vehicles.length}</p>
              <p className="text-sm text-slate-500">Total Vehicles</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center">
              <Navigation className="text-emerald-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                {vehicles.filter(v => v.status === 'moving').length}
              </p>
              <p className="text-sm text-slate-500">Moving</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-50 dark:bg-amber-900/30 flex items-center justify-center">
              <Clock className="text-amber-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                {vehicles.filter(v => v.status === 'stopped').length}
              </p>
              <p className="text-sm text-slate-500">Stopped</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center">
              <AlertCircle className="text-slate-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                {vehicles.filter(v => v.status === 'idle').length}
              </p>
              <p className="text-sm text-slate-500">Idle</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Area */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          {/* Map Header */}
          <div className="p-4 border-b border-slate-100 dark:border-slate-700">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="text"
                placeholder="Search vehicles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Map Placeholder */}
          <div className="h-[500px] bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800 relative">
            {/* Grid pattern */}
            <div className="absolute inset-0" style={{
              backgroundImage: `linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px),
                               linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px)`,
              backgroundSize: '30px 30px'
            }} />
            
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="flex flex-col items-center gap-3">
                  <Loader2 size={32} className="animate-spin text-indigo-500" />
                  <span className="text-sm text-slate-500 dark:text-slate-400">Loading vehicle positions...</span>
                </div>
              </div>
            ) : filteredVehicles.length === 0 ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <MapPin size={48} className="mx-auto text-slate-300 dark:text-slate-600 mb-3" />
                  <p className="text-sm text-slate-500 dark:text-slate-400">No vehicles currently active</p>
                </div>
              </div>
            ) : (
              <>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  <div className="w-16 h-16 bg-indigo-500/20 rounded-full flex items-center justify-center">
                    <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/30">
                      <MapPin className="text-white" size={16} />
                    </div>
                  </div>
                </div>
                {filteredVehicles.map((vehicle, index) => {
                  const positions = [
                    { top: '30%', left: '25%' },
                    { top: '45%', left: '60%' },
                    { top: '60%', left: '35%' },
                    { top: '70%', left: '70%' },
                  ];
                  return (
                    <button
                      key={vehicle.id}
                      onClick={() => setSelectedVehicle(vehicle)}
                      className={`absolute transform -translate-x-1/2 -translate-y-1/2 transition-all hover:scale-110 ${
                        selectedVehicle?.id === vehicle.id ? 'scale-110' : ''
                      }`}
                      style={{ top: positions[index].top, left: positions[index].left }}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
                        vehicle.status === 'moving' ? 'bg-emerald-500' :
                        vehicle.status === 'stopped' ? 'bg-amber-500' : 'bg-slate-500'
                      }`}>
                        <Bus className="text-white" size={18} />
                      </div>
                    </button>
                  );
                })}
              </>
            )}

            {/* Map legend */}
            <div className="absolute bottom-4 left-4 bg-white dark:bg-slate-800 rounded-xl p-3 shadow-lg border border-slate-200 dark:border-slate-700">
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="text-slate-600 dark:text-slate-300">Moving</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <span className="text-slate-600 dark:text-slate-300">Stopped</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-slate-500" />
                  <span className="text-slate-600 dark:text-slate-300">Idle</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Vehicle List */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 dark:border-slate-700">
            <h3 className="font-semibold text-slate-900 dark:text-white">Vehicles</h3>
            <p className="text-sm text-slate-500">{filteredVehicles.length} active</p>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-700 max-h-[500px] overflow-y-auto">
            {filteredVehicles.map((vehicle) => (
              <button
                key={vehicle.id}
                onClick={() => setSelectedVehicle(vehicle)}
                className={`w-full p-4 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors ${
                  selectedVehicle?.id === vehicle.id ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      vehicle.status === 'moving' ? 'bg-emerald-100 dark:bg-emerald-900/30' :
                      vehicle.status === 'stopped' ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-slate-100 dark:bg-slate-700'
                    }`}>
                      <Bus className={
                        vehicle.status === 'moving' ? 'text-emerald-600' :
                        vehicle.status === 'stopped' ? 'text-amber-600' : 'text-slate-500'
                      } size={18} />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white">{vehicle.vehicle_number}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">{vehicle.driver}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusColor(vehicle.status)}`}>
                    {getStatusIcon(vehicle.status)}
                    <span className="ml-1 capitalize">{vehicle.status}</span>
                  </span>
                </div>
                {selectedVehicle?.id === vehicle.id && (
                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <Route size={14} className="text-slate-400" />
                      <span className="text-slate-600 dark:text-slate-300">{vehicle.route}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1 text-sm">
                        <Navigation size={14} className="text-slate-400" />
                        <span className="text-slate-600 dark:text-slate-300">{vehicle.speed} km/h</span>
                      </div>
                      <div className="flex items-center gap-1 text-sm">
                        <User size={14} className="text-slate-400" />
                        <span className="text-slate-600 dark:text-slate-300">{vehicle.students} students</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="flex-1 py-2 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg text-sm font-medium hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors">
                        View Details
                      </button>
                      <button className="p-2 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 rounded-lg hover:bg-emerald-200 dark:hover:bg-emerald-900/50 transition-colors">
                        <Phone size={16} />
                      </button>
                    </div>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}