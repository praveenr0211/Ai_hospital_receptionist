import React, { useState } from 'react';
import { X, Calendar, Clock, User, Phone, Stethoscope, AlertCircle } from 'lucide-react';
import type { Appointment } from '../../types';
import { formatDate, formatTime, getStatusBadgeClass } from '../../lib/utils';

interface AppointmentDetailModalProps {
  appointment: Appointment | null;
  onClose: () => void;
  onConfirmCancel: (apptId: number, reason: string) => void;
  onOpenReschedule: (appt: Appointment) => void;
}

export const AppointmentDetailModal: React.FC<AppointmentDetailModalProps> = ({
  appointment,
  onClose,
  onConfirmCancel,
  onOpenReschedule,
}) => {
  const [showCancelPrompt, setShowCancelPrompt] = useState(false);
  const [cancelReason, setCancelReason] = useState('Patient requested cancellation');

  if (!appointment) return null;

  const handleCancel = () => {
    if (showCancelPrompt) {
      onConfirmCancel(appointment.id, cancelReason);
      setShowCancelPrompt(false);
      onClose();
    } else {
      setShowCancelPrompt(true);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Appointment Summary
            </span>
            <h2 className="text-lg font-bold text-slate-900">
              Appointment #{appointment.id}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* Status Badge */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="text-xs font-semibold text-slate-500">Booking Status</span>
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${getStatusBadgeClass(
                appointment.status
              )}`}
            >
              {appointment.status.toUpperCase()}
            </span>
          </div>

          {/* Patient Details */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80 space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-blue-600" />
              Patient Information
            </div>
            <div className="text-sm font-bold text-slate-900">
              {appointment.patient?.full_name || `Patient #${appointment.patient_id}`}
            </div>
            <div className="text-xs text-slate-600 flex items-center gap-1.5 font-mono">
              <Phone className="w-3 h-3 text-slate-400" />
              {appointment.patient?.phone_number || 'N/A'}
            </div>
          </div>

          {/* Doctor & Dept */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/80 space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Stethoscope className="w-3.5 h-3.5 text-teal-600" />
              Assigned Doctor
            </div>
            <div className="text-sm font-bold text-slate-900">
              {appointment.doctor?.name || `Doctor #${appointment.doctor_id}`}
            </div>
            <div className="text-xs text-blue-600 font-semibold">
              {appointment.doctor?.specialty || 'General Medicine'}
            </div>
          </div>

          {/* Schedule Time */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl border border-slate-200 bg-white">
              <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-400" />
                Date
              </div>
              <div className="text-xs font-bold text-slate-800 mt-1">
                {formatDate(appointment.appointment_date)}
              </div>
            </div>

            <div className="p-3 rounded-xl border border-slate-200 bg-white">
              <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-400" />
                Time Slot
              </div>
              <div className="text-xs font-bold text-slate-800 mt-1">
                {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
              </div>
            </div>
          </div>

          {/* Reason */}
          <div>
            <div className="text-xs font-semibold text-slate-500 mb-1">Chief Clinical Reason</div>
            <div className="text-xs font-medium text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200">
              {appointment.reason || 'General medical consultation'}
            </div>
          </div>

          {/* Cancellation reason if cancelled */}
          {appointment.cancellation_reason && (
            <div className="bg-rose-50 border border-rose-200 p-3 rounded-xl text-xs text-rose-800">
              <div className="font-bold flex items-center gap-1 mb-0.5">
                <AlertCircle className="w-3.5 h-3.5" />
                Cancellation Reason:
              </div>
              {appointment.cancellation_reason}
            </div>
          )}

          {/* Cancellation prompt input if active */}
          {showCancelPrompt && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl space-y-2 animate-in fade-in">
              <label className="text-xs font-bold text-rose-800 block">
                Reason for Cancellation:
              </label>
              <input
                type="text"
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                className="w-full text-xs p-2 bg-white border border-rose-300 rounded-lg outline-none focus:ring-2 focus:ring-rose-500"
              />
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-2">
          {appointment.status !== 'cancelled' ? (
            <div className="flex items-center gap-2 w-full justify-between">
              <button
                onClick={handleCancel}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 transition-colors cursor-pointer"
              >
                {showCancelPrompt ? 'Confirm Cancellation' : 'Cancel Appointment'}
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    onClose();
                    onOpenReschedule(appointment);
                  }}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 transition-colors cursor-pointer shadow-xs"
                >
                  Reschedule
                </button>
              </div>
            </div>
          ) : (
            <div className="w-full flex justify-end">
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-200 hover:bg-slate-300 text-slate-700 cursor-pointer"
              >
                Close
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
