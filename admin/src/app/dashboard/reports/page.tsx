'use client';

import React, { useState } from 'react';
import { 
  Download, FileText, BarChart3, Users, Bus, DollarSign, 
  TrendingUp, Calendar, Filter, Printer, Share2, Eye,
  Clock, CheckCircle, AlertCircle, ArrowUpRight, ArrowDownRight, Loader2
} from 'lucide-react';
import { EmptyState } from '@/components/ui/EmptyState';
import api, { attendanceAPI, feesAPI, vehiclesAPI, studentsAPI } from '@/lib/api';

interface ReportData {
  id: string;
  name: string;
  description: string;
  type: 'attendance' | 'financial' | 'vehicle' | 'student';
  lastGenerated?: string;
  format: 'pdf' | 'excel' | 'csv';
}

const availableReports: ReportData[] = [
  { 
    id: 'attendance', 
    name: 'Attendance Report', 
    description: 'Daily and monthly attendance summary with present, absent, and late counts',
    type: 'attendance',
    lastGenerated: '2024-05-15 10:30 AM',
    format: 'pdf'
  },
  { 
    id: 'fee-collection', 
    name: 'Fee Collection Report', 
    description: 'Fee collection, pending payments, and overdue summary',
    type: 'financial',
    lastGenerated: '2024-05-14 2:15 PM',
    format: 'excel'
  },
  { 
    id: 'vehicle-performance', 
    name: 'Vehicle Performance', 
    description: 'Vehicle utilization, mileage, fuel consumption, and maintenance',
    type: 'vehicle',
    lastGenerated: '2024-05-13 9:00 AM',
    format: 'pdf'
  },
  { 
    id: 'student-transport', 
    name: 'Student Transport', 
    description: 'Student route allocation, pickup points, and transport status',
    type: 'student',
    lastGenerated: '2024-05-12 4:45 PM',
    format: 'pdf'
  },
  { 
    id: 'route-analysis', 
    name: 'Route Analysis', 
    description: 'Route efficiency, timing analysis, and stop optimization',
    type: 'vehicle',
    lastGenerated: '2024-05-11 11:20 AM',
    format: 'excel'
  },
  { 
    id: 'financial-summary', 
    name: 'Financial Summary', 
    description: 'Monthly revenue, expenses, and profit analysis',
    type: 'financial',
    lastGenerated: '2024-05-10 3:30 PM',
    format: 'pdf'
  },
  { 
    id: 'driver-performance', 
    name: 'Driver Performance', 
    description: 'Driver ratings, trip completion, and safety records',
    type: 'vehicle',
    format: 'pdf'
  },
  { 
    id: 'trip-log', 
    name: 'Trip Log', 
    description: 'Complete trip history with start/end times and routes',
    type: 'vehicle',
    lastGenerated: '2024-05-15 8:00 AM',
    format: 'csv'
  },
];

const recentReports = [
  { id: 1, name: 'Attendance Report - May 2024', date: 'May 15, 2024', size: '2.4 MB', downloads: 12 },
  { id: 2, name: 'Fee Collection - April 2024', date: 'April 30, 2024', size: '1.8 MB', downloads: 8 },
  { id: 3, name: 'Vehicle Performance Q1', date: 'April 15, 2024', size: '3.2 MB', downloads: 5 },
];

const stats = [
  { label: 'Reports Generated', value: '24', change: '+12%', up: true },
  { label: 'Total Downloads', value: '156', change: '+8%', up: true },
  { label: 'Avg. Report Size', value: '2.4 MB', change: '-5%', up: false },
  { label: 'PDF Reports', value: '18', change: '+15%', up: true },
];

export default function ReportsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [exporting, setExporting] = useState<string | null>(null);
  const [exportMsg, setExportMsg] = useState<string | null>(null);

  const filteredReports = availableReports.filter(report => {
    const matchesSearch = report.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedType === 'all' || report.type === selectedType;
    return matchesSearch && matchesType;
  });

  const handleExport = async (reportId: string, format: string) => {
    setExporting(reportId);
    setExportMsg(null);
    try {
      const apiMap: Record<string, any> = {
        attendance: attendanceAPI.daily,
        financial: feesAPI.list,
        vehicle: vehiclesAPI.list,
        student: studentsAPI.list,
      };
      const fetcher = apiMap[reportId];
      const res = fetcher ? await fetcher() : await api.get(`/reports/${reportId}`);
      const data = res.data;
      const blob = new Blob(
        [JSON.stringify(data, null, 2)],
        { type: 'application/json' }
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportId}-report.${format === 'csv' ? 'csv' : format === 'excel' ? 'xlsx' : 'json'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setExportMsg(`${reportId} report downloaded successfully`);
    } catch (err: any) {
      setExportMsg(`Export failed: ${err?.message || 'Unknown error'}`);
    } finally {
      setExporting(null);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'attendance': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'financial': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'vehicle': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'student': return 'bg-purple-50 text-purple-700 border-purple-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'attendance': return <Users size={16} />;
      case 'financial': return <DollarSign size={16} />;
      case 'vehicle': return <Bus size={16} />;
      case 'student': return <FileText size={16} />;
      default: return <FileText size={16} />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reports</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Generate and download reports for your transport system</p>
        </div>
        {exportMsg && (
          <div className="px-4 py-2 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 rounded-xl text-sm">
            {exportMsg}
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
            <p className="text-sm text-slate-500 dark:text-slate-400">{stat.label}</p>
            <div className="flex items-end justify-between mt-2">
              <span className="text-2xl font-bold text-slate-900 dark:text-white">{stat.value}</span>
              <div className={`flex items-center gap-1 text-sm ${stat.up ? 'text-emerald-600' : 'text-red-600'}`}>
                {stat.up ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Available Reports */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  placeholder="Search reports..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium"
              >
                <option value="all">All Types</option>
                <option value="attendance">Attendance</option>
                <option value="financial">Financial</option>
                <option value="vehicle">Vehicle</option>
                <option value="student">Student</option>
              </select>
            </div>
          </div>

          {/* Reports Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredReports.map((report) => (
              <div 
                key={report.id}
                className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm hover:shadow-lg hover:border-indigo-200 dark:hover:border-indigo-700 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${getTypeColor(report.type)}`}>
                    {getTypeIcon(report.type)}
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getTypeColor(report.type)}`}>
                    {report.type}
                  </span>
                </div>
                
                <h3 className="font-semibold text-slate-900 dark:text-white mb-2">{report.name}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">{report.description}</p>
                
                {report.lastGenerated && (
                  <div className="flex items-center gap-2 text-xs text-slate-400 mb-4">
                    <Clock size={14} />
                    Last generated: {report.lastGenerated}
                  </div>
                )}
                
                <div className="flex items-center gap-2 pt-4 border-t border-slate-100 dark:border-slate-700">
                  <button className="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg text-sm font-medium hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors">
                    <Eye size={16} />
                    View
                  </button>
                  <button 
                    onClick={() => handleExport(report.id, report.format)}
                    disabled={exporting === report.id}
                    className="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {exporting === report.id ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Download size={16} />
                    )}
                    {exporting === report.id ? 'Exporting...' : report.format.toUpperCase()}
                  </button>
                  <button className="p-2 rounded-lg border border-slate-200 dark:border-slate-600 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                    <Printer size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredReports.length === 0 && (
            <EmptyState 
              title="No reports found"
              description="Try adjusting your search or filter criteria"
              icon="search"
            />
          )}
        </div>

        {/* Recent Reports */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Recent Downloads</h3>
            <div className="space-y-3">
              {recentReports.map((report) => (
                <div 
                  key={report.id}
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
                >
                  <div className="w-10 h-10 rounded-lg bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                    <FileText className="text-red-600" size={18} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{report.name}</p>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <span>{report.date}</span>
                      <span>•</span>
                      <span>{report.size}</span>
                    </div>
                  </div>
                  <button className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 text-slate-400 hover:text-indigo-600 transition-colors">
                    <Download size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-5 text-white">
            <h3 className="font-semibold mb-2">Schedule Reports</h3>
            <p className="text-sm text-indigo-200 mb-4">Automatically generate and email reports on a schedule</p>
            <button className="w-full py-2.5 bg-white/20 hover:bg-white/30 rounded-xl font-medium transition-colors flex items-center justify-center gap-2">
              <Calendar size={18} />
              Schedule Report
            </button>
          </div>

          {/* Format Legend */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3">Export Formats</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <span className="w-3 h-3 rounded bg-red-500" />
                <span className="text-slate-600 dark:text-slate-400">PDF - Best for printing</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="w-3 h-3 rounded bg-emerald-500" />
                <span className="text-slate-600 dark:text-slate-400">Excel - Best for数据分析</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="w-3 h-3 rounded bg-blue-500" />
                <span className="text-slate-600 dark:text-slate-400">CSV - Best for raw data</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}