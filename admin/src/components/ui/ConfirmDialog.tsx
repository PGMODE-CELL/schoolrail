'use client';

import React from 'react';
import { AlertTriangle, Trash2, Loader2 } from 'lucide-react';
import { Modal } from './Modal';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  variant?: 'danger' | 'default';
  loading?: boolean;
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  variant = 'default',
  loading = false,
}: ConfirmDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <div className="flex flex-col items-center text-center py-2">
        <div
          className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-4 ${
            variant === 'danger' ? 'bg-red-50 text-red-600' : 'bg-slate-100 text-slate-600'
          }`}
        >
          {variant === 'danger' ? <Trash2 size={28} /> : <AlertTriangle size={28} />}
        </div>
        <p className="text-slate-600 text-sm leading-relaxed">{message}</p>
        <div className="flex items-center gap-3 mt-6 w-full">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-slate-600 font-medium hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className={`flex-1 px-4 py-2.5 rounded-xl text-white font-medium transition-colors flex items-center justify-center gap-2 ${
              loading ? 'opacity-60 cursor-not-allowed' : ''
            } ${
              variant === 'danger'
                ? 'bg-red-600 hover:bg-red-700 shadow-lg shadow-red-600/20'
                : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-600/20'
            }`}
          >
            {loading && <Loader2 size={18} className="animate-spin" />}
            {confirmText}
          </button>
        </div>
      </div>
    </Modal>
  );
}

export default ConfirmDialog;
