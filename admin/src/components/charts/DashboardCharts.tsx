'use client';

import { useState } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const MonthlyData = [
  { month: 'Jan', students: 120, revenue: 180000 },
  { month: 'Feb', students: 135, revenue: 202500 },
  { month: 'Mar', students: 142, revenue: 213000 },
  { month: 'Apr', students: 148, revenue: 222000 },
  { month: 'May', students: 145, revenue: 217500 },
  { month: 'Jun', students: 150, revenue: 225000 },
];

const RouteDistribution = [
  { name: 'Route A', value: 45, color: '#6366f1' },
  { name: 'Route B', value: 35, color: '#10b981' },
  { name: 'Route C', value: 20, color: '#f59e0b' },
];

const AttendanceData = [
  { day: 'Mon', present: 140, absent: 10 },
  { day: 'Tue', present: 145, absent: 5 },
  { day: 'Wed', present: 138, absent: 12 },
  { day: 'Thu', present: 142, absent: 8 },
  { day: 'Fri', present: 148, absent: 2 },
];

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}

function ChartCard({ title, subtitle, children, action }: ChartCardProps) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
          {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

export function DashboardCharts() {
  const [timeRange, setTimeRange] = useState('6m');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Student Trend Chart */}
      <ChartCard 
        title="Student Enrollment" 
        subtitle="Last 6 months"
        action={
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-1.5 text-sm border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-700 text-slate-600 dark:text-slate-300"
          >
            <option value="3m">3 Months</option>
            <option value="6m">6 Months</option>
            <option value="1y">1 Year</option>
          </select>
        }
      >
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={MonthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e2e8f0', 
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="students" 
                stroke="#6366f1" 
                strokeWidth={3}
                dot={{ fill: '#6366f1', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Revenue Chart */}
      <ChartCard 
        title="Revenue Trend" 
        subtitle="Monthly transport fees collected"
      >
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={MonthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} tickFormatter={(value) => `₹${value/1000}k`} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e2e8f0', 
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [`₹${value.toLocaleString()}`, 'Revenue']}
              />
              <Bar dataKey="revenue" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Route Distribution */}
      <ChartCard title="Route Distribution" subtitle="Students per route">
        <div className="h-64 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={RouteDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {RouteDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend 
                verticalAlign="bottom" 
                height={36}
                formatter={(value) => <span className="text-slate-600 dark:text-slate-300 text-sm">{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Weekly Attendance */}
      <ChartCard title="Weekly Attendance" subtitle="Present vs Absent">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={AttendanceData} barSize={30}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e2e8f0', 
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="present" name="Present" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="absent" name="Absent" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>
    </div>
  );
}

export default DashboardCharts;