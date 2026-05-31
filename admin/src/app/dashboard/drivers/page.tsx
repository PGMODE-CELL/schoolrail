'use client';

import { useState } from 'react';
import { useDrivers } from '@/hooks/useSchoolRail';
import { Users, Plus, Search, Filter, Phone, Star, Car, Eye, Edit, MessageCircle } from 'lucide-react';

export default function DriversPage() {
  const { data: drivers, isLoading, error } = useDrivers();
  const [searchTerm, setSearchTerm] = useState('');

  const driverArr = Array.isArray(drivers) ? drivers : [];

  const filtered = driverArr.filter((d: any) =>
    !searchTerm || d.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) || d.phone?.includes(searchTerm)
  );

  const avgRating = driverArr.length
    ? (driverArr.reduce((s: number, d: any) => s + (d.rating || 0), 0) / driverArr.length).toFixed(1)
    : '0.0';

  const stats = [
    { label: 'Total Drivers', value: driverArr.length, icon: Users, color: 'blue' },
    { label: 'Active Now', value: driverArr.filter((d: any) => d.status === 'active').length, icon: Car, color: 'green' },
    { label: 'Avg Rating', value: avgRating, icon: Star, color: 'amber' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'inactive': return 'bg-slate-50 text-slate-600 border-slate-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

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
                'bg-amber-50 text-amber-600'
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
          <h1 className="text-2xl font-bold text-slate-900">Drivers</h1>
          <p className="text-slate-500 mt-1">Manage your driver fleet and assignments</p>
        </div>
        <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20">
          <Plus size={20} />
          Add Driver
        </button>
      </div>

      {/* Search & Filter */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search by name, phone, license..."
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
        <div className="p-12 text-center text-slate-400">Loading drivers...</div>
      )}
      {error && (
        <div className="p-12 text-center text-red-400">Error loading drivers</div>
      )}
      {!isLoading && !error && (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((driver: any) => (
          <div key={driver.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-lg hover:border-slate-300 transition-all duration-300">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-indigo-500/30">
                  {(driver.first_name || '?')[0]}{(driver.last_name || '')[0]}
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 text-lg">{driver.first_name} {driver.last_name || ''}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(driver.status)}`}>
                    <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                      driver.status === 'active' ? 'bg-emerald-500' : 'bg-slate-400'
                    }`} />
                    {driver.status.charAt(0).toUpperCase() + driver.status.slice(1)}
                  </span>
                </div>
              </div>
            </div>

            {/* Info */}
            <div className="space-y-3 mb-6">
              <div className="flex items-center gap-3 text-slate-600">
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                  <Phone size={16} className="text-slate-500" />
                </div>
                <span className="text-sm">{driver.phone}</span>
              </div>
              <div className="flex items-center gap-3 text-slate-600">
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                  <Car size={16} className="text-slate-500" />
                </div>
                <span className="text-sm">License: <span className="font-medium">{driver.license_number}</span></span>
              </div>
            </div>

            {/* Stats */}
            <div className="flex items-center justify-between py-4 border-t border-b border-slate-100 mb-4">
              <div className="text-center flex-1">
                <div className="flex items-center justify-center gap-1">
                  <Star size={16} className="text-amber-500 fill-amber-500" />
                  <span className="text-lg font-bold text-slate-900">{driver.rating || 'N/A'}</span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">Rating</p>
              </div>
              <div className="w-px h-10 bg-slate-200" />
              <div className="text-center flex-1">
                <span className="text-lg font-bold text-slate-900">{driver.total_trips || 0}</span>
                <p className="text-xs text-slate-500 mt-0.5">Total Trips</p>
              </div>
              <div className="w-px h-10 bg-slate-200" />
              <div className="text-center flex-1">
                <span className="text-lg font-bold text-slate-900">{driver.created_at ? new Date(driver.created_at).toLocaleDateString() : '-'}</span>
                <p className="text-xs text-slate-500 mt-0.5">Joined</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-50 text-indigo-600 rounded-xl font-medium hover:bg-indigo-100 transition-colors">
                <Eye size={18} />
                View
              </button>
              <button className="p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
                <MessageCircle size={18} />
              </button>
              <button className="p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
                <Edit size={18} />
              </button>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="col-span-full p-12 text-center text-slate-400">No drivers found</div>
        )}
      </div>
      )}
    </div>
  );
}