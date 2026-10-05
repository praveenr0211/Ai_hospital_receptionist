import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import type { Appointment, TimeSlot } from '../../types';
import { api } from '../../lib/api';
import { formatDate, formatTime } from '../../lib/utils';

interface RescheduleModalProps {
  appointment: Appointment | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const RescheduleModal: React.FC<RescheduleModalProps> = ({
  appointment,
  onClose,
  onSuccess,
}) => {
  const [newDate, setNewDate] = useState<string>(
    appointment?.appointment_date || new Date().toISOString().split('T')[0]
  );
  const [selectedSlot, setSelectedSlot] = useState<string>('');
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!appointment) return;
    setLoading(true);

    api.getDoctorAvailability(appointment.doctor_id, newDate)
      .then((slots) => {
        const open = slots.filter((s) => s.is_available);
        setAvailableSlots(open);
        if (open.length > 0) {
          setSelectedSlot(open[0].start_time);
        } else {
          setSelectedSlot('');
        }
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [appointment, newDate]);

  if (!appointment) return null;

  const handleConfirmReschedule = async () => {
    if (!selectedSlot) return;
    setSubmitting(true);
    try {
      await api.rescheduleAppointment(appointment.id, newDate, selectedSlot);
      onSuccess();
      onClose();
    } catch (err) {
      alert(`Reschedule failed: ${err}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Deterministic Rescheduling
            </span>
            <h2 className="text-lg font-bold text-slate-900">
              Reschedule Appointment #{appointment.id}
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
          {/* Current slot info */}
          <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1">
            <span className="font-bold block">Current Confirmed Schedule:</span>
            <div className="flex items-center gap-3 text-amber-800">
              <span>📅 {formatDate(appointment.appointment_date)}</span>
              <span>⏰ {formatTime(appointment.start_time)}</span>
            </div>
            <p className="text-[11px] text-amber-700 mt-1">
              With {appointment.doctor?.name} ({appointment.doctor?.specialty})
            </p>
          </div>

          {/* New Date Picker */}
          <div>
            <label className="text-xs font-bold text-slate-600 block mb-1">
              Select New Consultation Date:
            </label>
            <input
              type="date"
              value={newDate}
              onChange={(e) => setNewDate(e.target.value)}
              className="w-full text-xs font-semibold text-slate-800 bg-white border border-slate-300 rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          {/* Available Slots */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-slate-600">
                Available Alternative Slots:
              </label>
              <span className="text-[11px] text-slate-400">
                {availableSlots.length} open slots
              </span>
            </div>

            {loading ? (
              <div className="py-6 text-center text-xs text-slate-400">
                Computing available alternative slots...
              </div>
            ) : availableSlots.length > 0 ? (
              <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto pr-1">
                {availableSlots.map((slot) => {
                  const isSelected = selectedSlot === slot.start_time;
                  return (
                    <button
                      key={slot.start_time}
                      type="button"
                      onClick={() => setSelectedSlot(slot.start_time)}
                      className={`p-2.5 rounded-xl border text-xs font-bold font-mono text-center transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-blue-600 border-blue-600 text-white shadow-sm ring-2 ring-blue-300'
                          : 'bg-emerald-50 border-emerald-200 text-emerald-800 hover:bg-emerald-100'
                      }`}
                    >
                      {formatTime(slot.start_time)}
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-center text-xs text-slate-500">
                No slots available on this date. Please pick another date.
              </div>
            )}
          </div>
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-200 cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirmReschedule}
            disabled={!selectedSlot || submitting}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            {submitting ? 'Rescheduling...' : 'Confirm Reschedule'}
          </button>
        </div>
      </div>
    </div>
  );
};
