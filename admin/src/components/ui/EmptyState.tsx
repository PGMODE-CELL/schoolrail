'use client';

import React from 'react';
import { Search, FileText, Users, Bus, MapPin, Inbox } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: 'search' | 'file' | 'users' | 'bus' | 'map' | 'inbox';
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const iconMap = {
  search: Search,
  file: FileText,
  users: Users,
  bus: Bus,
  map: MapPin,
  inbox: Inbox,
};

export function EmptyState({ title, description, icon = 'inbox', action, className = '' }: EmptyStateProps) {
  const Icon = iconMap[icon];

  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 ${className}`}>
      <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
        <Icon size={32} className="text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-sm text-slate-500 dark:text-slate-400 text-center max-w-sm mb-6">
          {description}
        </p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

export function TableEmptyState({ 
  title = 'No data found',
  description = 'Try adjusting your search or filter criteria',
}: { title?: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="w-14 h-14 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
        <Search size={24} className="text-slate-400" />
      </div>
      <h3 className="text-base font-medium text-slate-900 dark:text-white mb-1">
        {title}
      </h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 text-center">
        {description}
      </p>
    </div>
  );
}

export default EmptyState;