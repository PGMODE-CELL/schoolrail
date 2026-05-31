'use client';

import React from 'react';

interface FormFieldProps {
  label: string;
  name: string;
  type?: 'text' | 'number' | 'select' | 'date' | 'textarea' | 'email';
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  options?: { value: string | number; label: string }[];
  required?: boolean;
  error?: string;
  placeholder?: string;
}

export function FormField({
  label,
  name,
  type = 'text',
  value,
  onChange,
  options,
  required,
  error,
  placeholder,
}: FormFieldProps) {
  const baseInputClass =
    'w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-slate-50 text-slate-900 placeholder-slate-400 transition-colors';
  const errorInputClass = error ? 'border-red-300 focus:ring-red-500/20 focus:border-red-500 bg-red-50' : '';
  const inputClass = `${baseInputClass} ${errorInputClass}`;

  return (
    <div className="space-y-1.5">
      <label htmlFor={name} className="block text-sm font-medium text-slate-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      {type === 'select' && options ? (
        <select id={name} name={name} value={value} onChange={onChange} required={required} className={inputClass}>
          <option value="">Select {label}</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : type === 'textarea' ? (
        <textarea
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          required={required}
          placeholder={placeholder}
          rows={4}
          className={`${inputClass} resize-none`}
        />
      ) : (
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          required={required}
          placeholder={placeholder}
          className={inputClass}
        />
      )}

      {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
    </div>
  );
}

export default FormField;
