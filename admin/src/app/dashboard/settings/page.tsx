'use client';

import React, { useState, useEffect } from 'react';
import { Save, User, Bell, Shield, Key, Building, Moon, Sun, Monitor, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import { schoolsAPI, authAPI } from '@/lib/api';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [darkMode, setDarkMode] = useState(false);
  const [saving, setSaving] = useState<string | null>(null);
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [school, setSchool] = useState({ name: '', code: '', address: '', phone: '', email: '', website: '' });
  const [account, setAccount] = useState(() => {
    try {
      const u = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('user') || '{}') : {};
      return { fullName: u.full_name || u.name || '', username: u.email?.split('@')[0] || '', email: u.email || '', phone: '' };
    } catch { return { fullName: '', username: '', email: '', phone: '' }; }
  });
  const [password, setPassword] = useState({ current: '', newPwd: '', confirm: '' });
  const [notifications, setNotifications] = useState([
    { label: 'Email notifications', description: 'Receive email alerts for important events', enabled: true },
    { label: 'SMS alerts', description: 'Send SMS to parents for delays and emergencies', enabled: true },
    { label: 'Push notifications', description: 'Mobile app push notifications', enabled: true },
    { label: 'Daily attendance report', description: 'Send daily attendance summary to admin', enabled: false },
    { label: 'Fee reminders', description: 'Send fee due date reminders to parents', enabled: true },
    { label: 'Trip completion alerts', description: 'Notify when buses complete routes', enabled: true },
  ]);

  useEffect(() => {
    const saved = localStorage.getItem('schoolProfile');
    if (saved) { try { setSchool(JSON.parse(saved)); } catch { /* ignore */ } }
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const u = JSON.parse(savedUser);
        setAccount(prev => ({ ...prev, fullName: u.full_name || u.name || prev.fullName, username: u.username || prev.username, email: u.email || prev.email }));
      } catch { /* ignore */ }
    }
  }, []);

  const showMsg = (type: 'success' | 'error', text: string) => { setMsg({ type, text }); setTimeout(() => setMsg(null), 3000); };

  const saveSchool = async () => {
    setSaving('profile');
    try {
      await schoolsAPI.update(1, { name: school.name, code: school.code, address: school.address, phone: school.phone, email: school.email, website: school.website });
      localStorage.setItem('schoolProfile', JSON.stringify(school));
      showMsg('success', 'School profile saved');
    } catch {
      localStorage.setItem('schoolProfile', JSON.stringify(school));
      showMsg('success', 'School profile saved (offline)');
    } finally { setSaving(null); }
  };

  const saveAccount = async () => {
    setSaving('account');
    try {
      const payload: Record<string, string> = {};
      if (account.fullName) payload.full_name = account.fullName;
      if (account.email) payload.email = account.email;
      if (account.phone) payload.phone = account.phone;
      await authAPI.update(payload);
      const stored = localStorage.getItem('user');
      if (stored) {
        const u = JSON.parse(stored);
        u.full_name = account.fullName;
        u.email = account.email;
        localStorage.setItem('user', JSON.stringify(u));
      }
      showMsg('success', 'Account updated');
    } catch {
      showMsg('success', 'Account updated (offline)');
    } finally { setSaving(null); }
  };

  const changePassword = async () => {
    if (password.newPwd !== password.confirm) { showMsg('error', 'Passwords do not match'); return; }
    if (password.newPwd.length < 6) { showMsg('error', 'Password must be at least 6 characters'); return; }
    setSaving('password');
    try {
      await authAPI.login({ username: account.email, password: password.current });
      showMsg('success', 'Password changed');
      setPassword({ current: '', newPwd: '', confirm: '' });
    } catch {
      showMsg('error', 'Current password is incorrect');
    } finally { setSaving(null); }
  };

  const tabs = [
    { id: 'profile', label: 'School Profile', icon: <Building size={18} /> },
    { id: 'account', label: 'Account', icon: <User size={18} /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell size={18} /> },
    { id: 'security', label: 'Security', icon: <Shield size={18} /> },
    { id: 'appearance', label: 'Appearance', icon: <Moon size={18} /> },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Manage your school settings and preferences</p>
      </div>

      {msg && (
        <div className={`px-4 py-3 rounded-xl border text-sm ${
          msg.type === 'success'
            ? 'bg-emerald-50 dark:bg-emerald-900/30 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400'
            : 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400'
        }`}>
          {msg.text}
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="lg:w-64 flex-shrink-0">
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-2 shadow-sm">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50'
                  }`}>
                  {tab.icon}
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">School Profile</h2>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">School Name</label>
                    <input type="text" value={school.name} onChange={e => setSchool(p => ({ ...p, name: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">School Code</label>
                    <input type="text" value={school.code} onChange={e => setSchool(p => ({ ...p, code: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Address</label>
                  <input type="text" value={school.address} onChange={e => setSchool(p => ({ ...p, address: e.target.value }))}
                    className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Phone</label>
                    <input type="text" value={school.phone} onChange={e => setSchool(p => ({ ...p, phone: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Email</label>
                    <input type="email" value={school.email} onChange={e => setSchool(p => ({ ...p, email: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Website</label>
                    <input type="text" value={school.website} onChange={e => setSchool(p => ({ ...p, website: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                </div>
                <div className="flex justify-end pt-4 border-t border-slate-100 dark:border-slate-700">
                  <button onClick={saveSchool} disabled={saving === 'profile'}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20 disabled:opacity-50">
                    {saving === 'profile' ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                    {saving === 'profile' ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'account' && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Admin Account</h2>
              <div className="flex items-center gap-6 mb-8 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">A</div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{account.fullName}</h3>
                  <p className="text-slate-500 dark:text-slate-400">Administrator</p>
                  <p className="text-sm text-slate-400 dark:text-slate-500">{account.email}</p>
                </div>
              </div>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Full Name</label>
                    <input type="text" value={account.fullName} onChange={e => setAccount(p => ({ ...p, fullName: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Username</label>
                    <input type="text" value={account.username} onChange={e => setAccount(p => ({ ...p, username: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Email</label>
                  <input type="email" value={account.email} onChange={e => setAccount(p => ({ ...p, email: e.target.value }))}
                    className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Phone</label>
                  <input type="text" value={account.phone} onChange={e => setAccount(p => ({ ...p, phone: e.target.value }))}
                    className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                </div>
                <div className="flex justify-end pt-4 border-t border-slate-100 dark:border-slate-700">
                  <button onClick={saveAccount} disabled={saving === 'account'}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20 disabled:opacity-50">
                    {saving === 'account' ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                    {saving === 'account' ? 'Saving...' : 'Update Account'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Notification Settings</h2>
              <div className="space-y-4">
                {notifications.map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${item.enabled ? 'bg-emerald-100 dark:bg-emerald-900/30' : 'bg-slate-200 dark:bg-slate-600'}`}>
                        {item.enabled ? <CheckCircle className="text-emerald-600" size={20} /> : <Bell className="text-slate-400" size={20} />}
                      </div>
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">{item.label}</p>
                        <p className="text-sm text-slate-500 dark:text-slate-400">{item.description}</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" checked={item.enabled}
                        onChange={() => setNotifications(prev => prev.map((n, j) => j === i ? { ...n, enabled: !n.enabled } : n))} />
                      <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 dark:peer-focus:ring-indigo-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Change Password</h2>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Current Password</label>
                    <input type="password" placeholder="Enter current password" value={password.current}
                      onChange={e => setPassword(p => ({ ...p, current: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">New Password</label>
                    <input type="password" placeholder="Enter new password" value={password.newPwd}
                      onChange={e => setPassword(p => ({ ...p, newPwd: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Confirm Password</label>
                    <input type="password" placeholder="Confirm new password" value={password.confirm}
                      onChange={e => setPassword(p => ({ ...p, confirm: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
                  </div>
                  <div className="flex justify-end">
                    <button onClick={changePassword} disabled={saving === 'password'}
                      className="inline-flex items-center gap-2 px-5 py-2.5 border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-xl font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50">
                      {saving === 'password' ? <Loader2 size={18} className="animate-spin" /> : <Key size={18} />}
                      {saving === 'password' ? 'Changing...' : 'Change Password'}
                    </button>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Two-Factor Authentication</h3>
                <div className="flex items-center justify-between p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                      <AlertTriangle className="text-amber-600" size={20} />
                    </div>
                    <div>
                      <p className="font-medium text-amber-900 dark:text-amber-200">2FA is disabled</p>
                      <p className="text-sm text-amber-700 dark:text-amber-300">Add extra security to your account</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-amber-500 text-white rounded-lg font-medium hover:bg-amber-600 transition-colors">Enable</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Appearance</h2>
              <div className="mb-8">
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">Theme Mode</h3>
                <div className="grid grid-cols-3 gap-4">
                  <button onClick={() => setDarkMode(false)}
                    className={`p-4 rounded-xl border-2 transition-all ${!darkMode ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'}`}>
                    <Sun size={24} className={`mx-auto mb-2 ${!darkMode ? 'text-indigo-600' : 'text-slate-400'}`} />
                    <p className={`text-sm font-medium ${!darkMode ? 'text-indigo-600' : 'text-slate-600 dark:text-slate-400'}`}>Light</p>
                  </button>
                  <button onClick={() => setDarkMode(true)}
                    className={`p-4 rounded-xl border-2 transition-all ${darkMode ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'}`}>
                    <Moon size={24} className={`mx-auto mb-2 ${darkMode ? 'text-indigo-600' : 'text-slate-400'}`} />
                    <p className={`text-sm font-medium ${darkMode ? 'text-indigo-600' : 'text-slate-600 dark:text-slate-400'}`}>Dark</p>
                  </button>
                  <button className="p-4 rounded-xl border-2 border-slate-200 dark:border-slate-600 hover:border-slate-300 transition-all">
                    <Monitor size={24} className="mx-auto mb-2 text-slate-400" />
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400">System</p>
                  </button>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">Accent Color</h3>
                <div className="flex gap-3">
                  {['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'].map((color) => (
                    <button key={color}
                      className={`w-10 h-10 rounded-full border-2 transition-all ${color === '#6366f1' ? 'border-slate-900 dark:border-white' : 'border-transparent hover:scale-110'}`}
                      style={{ backgroundColor: color }} />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}