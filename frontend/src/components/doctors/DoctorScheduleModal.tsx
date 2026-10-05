import React, { useState, useEffect } from 'react';
import { X, Clock, CheckCircle2, XCircle, Stethoscope, RefreshCw } from 'lucide-react';
import type { Doctor, TimeSlot } from '../../types';
import { api } from '../../lib/api';
import { formatCurrency, formatTime } from '../../lib/utils';

interface DoctorScheduleModalProps {
  doctor: Doctor | null;
  onClose: () => void;
}

export const DoctorScheduleModal: React.FC<DoctorScheduleModalProps> = ({ doctor, onClose }) => {
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [slots, setSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!doctor) return;
    let isMounted = true;
    setLoading(true);

    api.getDoctorAvailability(doctor.id, selectedDate)
      .then((data) => {
        if (isMounted) {
          setSlots(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [doctor, selectedDate]);

  if (!doctor) return null;

  const availableCount = slots.filter((s) => s.is_available).length;
  const bookedCount = slots.filter((s) => !s.is_available).length;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-2xl w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-start justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
              <Stethoscope className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900">{doctor.name}</h2>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Active Practice
                </span>
              </div>
              <p className="text-xs font-semibold text-blue-600 mt-0.5">
                {doctor.specialty} • {doctor.qualification || 'MBBS, MD'} • Fee: {formatCurrency(doctor.consultation_fee)}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Schedule Controls */}
        <div className="p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Select Consultation Date
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="text-xs font-semibold text-slate-800 bg-white border border-slate-300 rounded-xl px-3 py-2 shadow-xs focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            {/* Quick stats summary */}
            <div className="flex items-center gap-3">
              <div className="px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>{availableCount} Available</span>
              </div>
              <div className="px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1.5">
                <XCircle className="w-3.5 h-3.5 text-slate-500" />
                <span>{bookedCount} Booked</span>
              </div>
            </div>
          </div>

          {/* Availability Slots Grid */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Availability Slots (Phase 2 Deterministic Schedule)
              </h3>
              {loading && (
                <span className="text-xs text-blue-600 flex items-center gap-1 font-medium">
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  Checking slots...
                </span>
              )}
            </div>

            {loading ? (
              <div className="py-12 text-center text-slate-400">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
                <p className="text-xs">Computing availability from calendar engine...</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {slots.map((slot, index) => {
                  const isAvailable = slot.is_available;
                  return (
                    <div
                      key={index}
                      className={`p-3 rounded-xl border flex flex-col items-center justify-center transition-all ${
                        isAvailable
                          ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900 hover:bg-emerald-100/70'
                          : 'bg-slate-100/70 border-slate-200 text-slate-500'
                      }`}
                    >
                      <div className="flex items-center gap-1 text-xs font-bold font-mono">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {formatTime(slot.start_time)}
                      </div>
                      <span
                        className={`mt-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                          isAvailable
                            ? 'bg-emerald-200/60 text-emerald-800'
                            : 'bg-slate-200 text-slate-600'
                        }`}
                      >
                        {isAvailable ? 'Available' : 'Booked'}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <span>AI Receptionist checks this live schedule via telephony tool calls</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold cursor-pointer transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
