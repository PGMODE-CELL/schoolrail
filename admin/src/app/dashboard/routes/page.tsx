'use client';

import { useState } from 'react';
import { useRoutes } from '@/hooks/useSchoolRail';
import { MapPin, Plus, Search, Filter, Clock, Navigation, Bus, Map, Eye, Edit, Trash2, Play } from 'lucide-react';

export default function RoutesPage() {
  const { data: routes, isLoading, error } = useRoutes();
  const [searchTerm, setSearchTerm] = useState('');

  const routeArr = Array.isArray(routes) ? routes : [];

  const filtered = routeArr.filter((r: any) =>
    !searchTerm || r.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalStops = routeArr.reduce((sum: number, r: any) => sum + (r.stops?.length || 0), 0);

  const stats = [
    { label: 'Total Routes', value: routeArr.length, icon: MapPin, color: 'blue' },
    { label: 'Active Routes', value: routeArr.filter((r: any) => r.status === 'active').length, icon: Play, color: 'green' },
    { label: 'Total Stops', value: totalStops, icon: Navigation, color: 'purple' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'inactive': return 'bg-slate-50 text-slate-600 border-slate-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const activeCount = routeArr.filter((r: any) => r.status === 'active').length;
  const inactiveCount = routeArr.length - activeCount;

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                stat.color === 'blue' ? 'bg-blue-50 text-blue-600' :
                stat.color === 'green' ? 'bg-emerald-50 text-emerald-600' :
                'bg-purple-50 text-purple-600'
              }`}>
                <stat.icon size={22} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Routes</h1>
          <p className="text-slate-500 mt-1">Manage bus routes, stops and schedules</p>
        </div>
        <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20">
          <Plus size={20} />
          Add Route
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Routes List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search */}
          <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                <input
                  type="text"
                  placeholder="Search routes by name, area..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-slate-50"
                />
              </div>
              <button className="inline-flex items-center gap-2 px-4 py-2.5 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors font-medium">
                <Filter size={18} />
                Filters
              </button>
            </div>
          </div>

          {isLoading && (
            <div className="p-12 text-center text-slate-400">Loading routes...</div>
          )}
          {error && (
            <div className="p-12 text-center text-red-400">Error loading routes</div>
          )}
          {!isLoading && !error && (
          <div className="space-y-4">
            {filtered.map((route: any) => (
              <div key={route.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-lg hover:border-slate-300 transition-all duration-300">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
                      <MapPin className="text-white" size={22} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 text-lg">{route.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="flex items-center gap-1 text-sm text-slate-500">
                          <Bus size={14} />
                          {route.route_code}
                        </span>
                        <span className="text-slate-300">•</span>
                        <span className="text-sm text-slate-500">{route.stops?.length || 0} stops</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border ${getStatusColor(route.status)}`}>
                      <span className={`w-1.5 h-1.5 rounded-full mr-2 ${
                        route.status === 'active' ? 'bg-emerald-500' : 'bg-slate-400'
                      }`} />
                      {route.status.charAt(0).toUpperCase() + route.status.slice(1)}
                    </span>
                  </div>
                </div>

                {/* Route Details */}
                <div className="flex flex-wrap items-center gap-4 py-3 border-t border-b border-slate-100 mb-4">
                  <div className="flex items-center gap-2 text-slate-600">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                      <MapPin size={16} className="text-slate-500" />
                    </div>
                    <span className="text-sm font-medium">{route.stops?.length || 0}</span>
                    <span className="text-sm text-slate-500">stops</span>
                  </div>
                  <div className="w-px h-6 bg-slate-200" />
                  <div className="flex items-center gap-2 text-slate-600">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                      <Navigation size={16} className="text-slate-500" />
                    </div>
                    <span className="text-sm font-medium">{route.total_distance_km ? `${route.total_distance_km} km` : '-'}</span>
                  </div>
                  <div className="w-px h-6 bg-slate-200" />
                  <div className="flex items-center gap-2 text-slate-600">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                      <Clock size={16} className="text-slate-500" />
                    </div>
                    <span className="text-sm font-medium">{route.estimated_time_minutes ? `${route.estimated_time_minutes} min` : '-'}</span>
                  </div>
                  <div className="w-px h-6 bg-slate-200" />
                  <div className="flex items-center gap-2 text-slate-600">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                      <Play size={16} className="text-slate-500" />
                    </div>
                    <span className="text-sm">{route.start_point} - {route.end_point}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-600 rounded-xl font-medium hover:bg-indigo-100 transition-colors">
                    <Eye size={18} />
                    View Stops
                  </button>
                  <button className="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 text-slate-600 rounded-xl font-medium hover:bg-slate-50 transition-colors">
                    <Edit size={18} />
                    Edit
                  </button>
                  <button className="ml-auto p-2.5 rounded-xl border border-slate-200 text-slate-400 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="p-12 text-center text-slate-400">No routes found</div>
            )}
          </div>
          )}
        </div>

        {/* Map Panel */}
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Route Overview</h3>
            <div className="h-48 bg-gradient-to-br from-slate-100 to-slate-200 rounded-xl flex items-center justify-center mb-4">
              <div className="text-center">
                <Map className="mx-auto text-slate-400 mb-2" size={40} />
                <p className="text-slate-500 text-sm font-medium">Interactive Map</p>
                <p className="text-slate-400 text-xs">Select a route to view</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50 border border-emerald-100">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                    <Play size={14} className="text-emerald-600" />
                  </div>
                  <span className="font-medium text-emerald-800">Active</span>
                </div>
                <span className="text-emerald-700 font-semibold">{activeCount} routes</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center">
                    <MapPin size={14} className="text-slate-600" />
                  </div>
                  <span className="font-medium text-slate-700">Inactive</span>
                </div>
                <span className="text-slate-600 font-semibold">{inactiveCount} routes</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-5 text-white">
            <h3 className="font-semibold mb-2">Quick Add Route</h3>
            <p className="text-indigo-200 text-sm mb-4">Create a new route with automatic stop detection</p>
            <button className="w-full py-2.5 bg-white/20 hover:bg-white/30 rounded-xl font-medium transition-colors flex items-center justify-center gap-2">
              <Plus size={18} />
              Create New Route
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}