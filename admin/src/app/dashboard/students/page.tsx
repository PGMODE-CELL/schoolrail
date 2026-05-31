'use client';

import { useState, useEffect } from 'react';
import { useStudents } from '@/hooks/useSchoolRail';
import { studentsAPI } from '@/lib/api';
import { Modal } from '@/components/ui/Modal';
import { FormField } from '@/components/ui/FormField';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { GraduationCap, Plus, Search, Filter, Phone, MapPin, User, Eye, Edit, Trash2, Send, Loader2, X, XCircle } from 'lucide-react';

const defaultForm = {
  first_name: '',
  last_name: '',
  student_id: '',
  class_name: '',
  section: '',
  gender: '',
  date_of_birth: '',
  phone: '',
  father_name: '',
  father_phone: '',
  mother_name: '',
  mother_phone: '',
  address: '',
  blood_group: '',
  route_id: '',
  pickup_stop_id: '',
  status: 'active',
};

const classOptions = [
  { value: 'I-II', label: 'I-II' },
  { value: 'III-V', label: 'III-V' },
  { value: 'VI-VIII', label: 'VI-VIII' },
  { value: 'IX-X', label: 'IX-X' },
  { value: 'XI-XII', label: 'XI-XII' },
];

const genderOptions = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
];

const statusOptions = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
];

function toDateValue(date: string | null | undefined): string {
  if (!date) return '';
  try {
    return date.split('T')[0];
  } catch {
    return '';
  }
}

export default function StudentsPage() {
  const { data: students, isLoading, error, refetch } = useStudents();
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<any>(null);
  const [form, setForm] = useState(defaultForm);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<{ type: 'error' | 'success'; message: string } | null>(null);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const studentArr = Array.isArray(students) ? students : [];

  const filtered = studentArr.filter((s: any) =>
    !searchTerm || s.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) || s.student_id?.toLowerCase().includes(searchTerm.toLowerCase()) || s.class_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = [
    { label: 'Total Students', value: studentArr.length, icon: GraduationCap, color: 'blue' },
    { label: 'Active', value: studentArr.filter((s: any) => s.status === 'active').length, icon: User, color: 'green' },
    { label: 'Assigned to Route', value: studentArr.filter((s: any) => s.route_id).length, icon: MapPin, color: 'purple' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'inactive': return 'bg-slate-50 text-slate-600 border-slate-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const openAddModal = () => {
    setEditingItem(null);
    setForm(defaultForm);
    setShowModal(true);
  };

  const openEditModal = (student: any) => {
    setEditingItem(student);
    setForm({
      first_name: student.first_name || '',
      last_name: student.last_name || '',
      student_id: student.student_id || '',
      class_name: student.class_name || '',
      section: student.section || '',
      gender: student.gender || '',
      date_of_birth: toDateValue(student.date_of_birth),
      phone: student.phone || '',
      father_name: student.father_name || '',
      father_phone: student.father_phone || '',
      mother_name: student.mother_name || '',
      mother_phone: student.mother_phone || '',
      address: student.address || '',
      blood_group: student.blood_group || '',
      route_id: student.route_id ?? '',
      pickup_stop_id: student.pickup_stop_id ?? '',
      status: student.status || 'active',
    });
    setShowModal(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: name === 'route_id' || name === 'pickup_stop_id' ? (value ? Number(value) : '') : value,
    }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setToast(null);
    try {
      const payload = {
        ...form,
        route_id: form.route_id === '' ? null : Number(form.route_id),
        pickup_stop_id: form.pickup_stop_id === '' ? null : Number(form.pickup_stop_id),
        date_of_birth: form.date_of_birth ? new Date(form.date_of_birth).toISOString() : null,
      };
      if (editingItem) {
        await studentsAPI.update(editingItem.id, payload);
      } else {
        await studentsAPI.create(payload);
      }
      await refetch();
      setShowModal(false);
      setToast({ type: 'success', message: editingItem ? 'Student updated successfully' : 'Student added successfully' });
    } catch (err: any) {
      setToast({ type: 'error', message: err.response?.data?.message || err.message || 'An error occurred' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;
    setSubmitting(true);
    setToast(null);
    try {
      await studentsAPI.delete(deleteConfirm.id);
      await refetch();
      setDeleteConfirm(null);
      setToast({ type: 'success', message: 'Student deleted successfully' });
    } catch (err: any) {
      setToast({ type: 'error', message: err.response?.data?.message || err.message || 'An error occurred' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {toast && (
        <div className={`flex items-center gap-3 px-5 py-3 rounded-xl border ${
          toast.type === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-emerald-50 border-emerald-200 text-emerald-700'
        }`}>
          <XCircle size={20} className="shrink-0" />
          <span className="text-sm font-medium flex-1">{toast.message}</span>
          <button onClick={() => setToast(null)} className="p-1 rounded-lg hover:bg-black/5 transition-colors">
            <X size={16} />
          </button>
        </div>
      )}

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
          <h1 className="text-2xl font-bold text-slate-900">Students</h1>
          <p className="text-slate-500 mt-1">Manage students and transport assignments</p>
        </div>
        <button
          onClick={openAddModal}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20"
        >
          <Plus size={20} />
          Add Student
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search by name, class, roll number..."
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

        {isLoading && (
          <div className="p-12 text-center text-slate-400">Loading students...</div>
        )}
        {error && (
          <div className="p-12 text-center text-red-400">Error loading students</div>
        )}
        {!isLoading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Student</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Class</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Parent</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Contact</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((student: any) => (
                <tr key={student.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white font-semibold shadow-lg shadow-purple-500/20">
                        {(student.first_name || '?')[0]}{(student.last_name || '')[0]}
                      </div>
                      <div>
                        <p className="font-semibold text-slate-900">{student.first_name} {student.last_name || ''}</p>
                        <p className="text-xs text-slate-500">ID: {student.student_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-sm font-medium">
                      {student.class_name}{student.section ? ` - ${student.section}` : ''}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-slate-600">{student.father_name || student.guardian_name || '-'}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-slate-600">
                      <Phone size={14} className="text-slate-400" />
                      <span className="text-sm">{student.father_phone || student.guardian_phone || '-'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border ${getStatusColor(student.status)}`}>
                      <span className={`w-1.5 h-1.5 rounded-full mr-2 ${
                        student.status === 'active' ? 'bg-emerald-500' : 'bg-slate-400'
                      }`} />
                      {student.status.charAt(0).toUpperCase() + student.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-indigo-600 transition-colors" title="Send Message">
                        <Send size={18} />
                      </button>
                      <button className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors" title="View">
                        <Eye size={18} />
                      </button>
                      <button
                        onClick={() => openEditModal(student)}
                        className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-indigo-600 transition-colors"
                        title="Edit"
                      >
                        <Edit size={18} />
                      </button>
                      <button
                        onClick={() => setDeleteConfirm(student)}
                        className="p-2 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-600 transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">No students found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        )}

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
          <p className="text-sm text-slate-500">Showing <span className="font-medium text-slate-900">{filtered.length}</span> of <span className="font-medium text-slate-900">{studentArr.length}</span> students</p>
          <div className="flex items-center gap-2">
            <button className="px-3 py-1.5 text-sm font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 disabled:opacity-50" disabled>Previous</button>
            <button className="px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">1</button>
            <button className="px-3 py-1.5 text-sm font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 disabled:opacity-50" disabled>Next</button>
          </div>
        </div>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={editingItem ? 'Edit Student' : 'Add Student'}
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="First Name" name="first_name" value={form.first_name} onChange={handleChange} required placeholder="e.g. John" />
            <FormField label="Last Name" name="last_name" value={form.last_name} onChange={handleChange} placeholder="e.g. Doe" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Student ID" name="student_id" value={form.student_id} onChange={handleChange} required placeholder="e.g. STU-001" />
            <FormField label="Class" name="class_name" type="select" value={form.class_name} onChange={handleChange} options={classOptions} required />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Section" name="section" value={form.section} onChange={handleChange} placeholder="e.g. A" />
            <FormField label="Gender" name="gender" type="select" value={form.gender} onChange={handleChange} options={genderOptions} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Date of Birth" name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} />
            <FormField label="Phone" name="phone" value={form.phone} onChange={handleChange} placeholder="e.g. 9876543210" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Father Name" name="father_name" value={form.father_name} onChange={handleChange} placeholder="e.g. Robert Doe" />
            <FormField label="Father Phone" name="father_phone" value={form.father_phone} onChange={handleChange} placeholder="e.g. 9876543210" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Mother Name" name="mother_name" value={form.mother_name} onChange={handleChange} placeholder="e.g. Jane Doe" />
            <FormField label="Mother Phone" name="mother_phone" value={form.mother_phone} onChange={handleChange} placeholder="e.g. 9876543210" />
          </div>
          <FormField label="Address" name="address" type="textarea" value={form.address} onChange={handleChange} placeholder="Enter full address" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Blood Group" name="blood_group" value={form.blood_group} onChange={handleChange} placeholder="e.g. O+" />
            <FormField label="Route ID" name="route_id" type="number" value={form.route_id} onChange={handleChange} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Pickup Stop ID" name="pickup_stop_id" type="number" value={form.pickup_stop_id} onChange={handleChange} />
            <FormField label="Status" name="status" type="select" value={form.status} onChange={handleChange} options={statusOptions} />
          </div>
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setShowModal(false)}
              className="px-5 py-2.5 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-indigo-600/20"
            >
              {submitting && <Loader2 size={18} className="animate-spin" />}
              {editingItem ? 'Update Student' : 'Add Student'}
            </button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        onConfirm={handleDelete}
        title="Delete Student"
        message={`Are you sure you want to delete ${deleteConfirm?.first_name} ${deleteConfirm?.last_name || ''}? This action cannot be undone.`}
        variant="danger"
        loading={submitting}
      />
    </div>
  );
}
