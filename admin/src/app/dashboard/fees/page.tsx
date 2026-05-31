'use client';

import { useState, useEffect } from 'react';
import { feesAPI } from '@/lib/api';
import { Search, Filter, Plus, Download, CheckCircle, Clock, XCircle, Receipt, Calendar } from 'lucide-react';

export default function FeesPage() {
  const [fees, setFees] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFees = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await feesAPI.list();
        const data = res.data;
        setFees(data.items || (Array.isArray(data) ? data : []));
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load fees');
        setFees([]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFees();
  }, []);

  const totalAmount = fees.reduce((sum: number, f: any) => sum + (f.final_amount || f.amount || 0), 0);
  const collected = fees.filter((f: any) => f.status === 'paid').reduce((sum: number, f: any) => sum + (f.paid_amount || f.final_amount || f.amount || 0), 0);
  const pending = fees.filter((f: any) => f.status === 'pending').reduce((sum: number, f: any) => sum + (f.final_amount || f.amount || 0), 0);
  const overdue = fees.filter((f: any) => f.status === 'overdue').reduce((sum: number, f: any) => sum + (f.final_amount || f.amount || 0), 0);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'pending': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'overdue': return 'bg-red-50 text-red-700 border-red-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid': return <CheckCircle size={16} className="text-emerald-500" />;
      case 'pending': return <Clock size={16} className="text-amber-500" />;
      case 'overdue': return <XCircle size={16} className="text-red-500" />;
      default: return null;
    }
  };

  const collectionPct = totalAmount > 0 ? (collected / totalAmount) * 100 : 0;
  const pendingPct = totalAmount > 0 ? (pending / totalAmount) * 100 : 0;
  const overduePct = totalAmount > 0 ? (overdue / totalAmount) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Fees Management</h1>
          <p className="text-slate-500 mt-1">Manage transport fees, payments and invoices</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center gap-2 px-4 py-2.5 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors font-medium">
            <Download size={18} />
            Export
          </button>
          <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20">
            <Plus size={20} />
            Create Invoice
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Total Invoiced</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">₹{totalAmount.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
              <Receipt size={22} className="text-blue-600" />
            </div>
          </div>
          <div className="mt-3 flex items-center gap-1 text-sm text-slate-500">
            <span>{fees.length} invoices</span>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Collected</p>
              <p className="text-2xl font-bold text-emerald-600 mt-1">₹{collected.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center">
              <CheckCircle size={22} className="text-emerald-600" />
            </div>
          </div>
          <div className="mt-3 h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${collectionPct}%` }} />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Pending</p>
              <p className="text-2xl font-bold text-amber-600 mt-1">₹{pending.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center">
              <Clock size={22} className="text-amber-600" />
            </div>
          </div>
          <div className="mt-3 h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-amber-500 rounded-full" style={{ width: `${pendingPct}%` }} />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">Overdue</p>
              <p className="text-2xl font-bold text-red-600 mt-1">₹{overdue.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center">
              <XCircle size={22} className="text-red-600" />
            </div>
          </div>
          <div className="mt-3 h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-red-500 rounded-full" style={{ width: `${overduePct}%` }} />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search by student, invoice number..."
              className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-slate-50"
            />
          </div>
          <div className="flex items-center gap-2">
            <button className="inline-flex items-center gap-2 px-4 py-2.5 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors font-medium">
              <Filter size={18} />
              Filters
            </button>
          </div>
        </div>

        {isLoading && (
          <div className="p-12 text-center text-slate-400">Loading fees...</div>
        )}
        {error && (
          <div className="p-12 text-center text-red-400">{error}</div>
        )}
        {!isLoading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Student ID</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Fee Type</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Due Date</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {fees.map((fee: any) => (
                <tr key={fee.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-medium text-slate-900">Student #{fee.student_id}</span>
                  </td>
                  <td className="px-6 py-4 text-slate-600">{fee.title || fee.fee_type}</td>
                  <td className="px-6 py-4">
                    <span className="font-semibold text-slate-900">₹{(fee.final_amount || fee.amount || 0).toLocaleString()}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-slate-600">
                      <Calendar size={14} className="text-slate-400" />
                      {fee.due_date ? new Date(fee.due_date).toLocaleDateString() : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border ${getStatusColor(fee.status)}`}>
                      {getStatusIcon(fee.status)}
                      <span className="ml-1">{fee.status.charAt(0).toUpperCase() + fee.status.slice(1)}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="px-3 py-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded-lg transition-colors">
                      View
                    </button>
                  </td>
                </tr>
              ))}
              {fees.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">No fees found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        )}

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
          <p className="text-sm text-slate-500">Showing <span className="font-medium text-slate-900">{fees.length}</span> invoices</p>
        </div>
      </div>
    </div>
  );
}