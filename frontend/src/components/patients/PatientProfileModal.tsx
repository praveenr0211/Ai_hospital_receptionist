import React from 'react';
import { X, User, Phone, Calendar, Clock } from 'lucide-react';
import type { Patient, Appointment } from '../../types';
import { formatDate, formatTime, getStatusBadgeClass } from '../../lib/utils';

interface PatientProfileModalProps {
  patient: Patient | null;
  appointments: Appointment[];
  onClose: () => void;
  onSelectAppointment: (appt: Appointment) => void;
}

export const PatientProfileModal: React.FC<PatientProfileModalProps> = ({
  patient,
  appointments,
  onClose,
  onSelectAppointment,
}) => {
  if (!patient) return null;

  const patientAppointments = appointments.filter((a) => a.patient_id === patient.id);

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-xl w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold text-base shadow-sm">
              <User className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Patient Operational Profile
              </span>
              <h2 className="text-lg font-bold text-slate-900">{patient.full_name}</h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {/* Contact summary */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                <Phone className="w-3.5 h-3.5 text-blue-600" />
                Phone Number
              </div>
              <div className="text-xs font-bold text-slate-900 font-mono mt-1">
                {patient.phone_number}
              </div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
              <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-blue-600" />
                Total Visits
              </div>
              <div className="text-xs font-bold text-slate-900 mt-1">
                {patientAppointments.length} Booked Appointments
              </div>
            </div>
          </div>

          {/* Appointment History List */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Consultation & Visit History
            </h3>

            <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
              {patientAppointments.map((appt) => (
                <div
                  key={appt.id}
                  onClick={() => {
                    onClose();
                    onSelectAppointment(appt);
                  }}
                  className="p-3.5 bg-white border border-slate-200 hover:border-blue-300 rounded-xl flex items-center justify-between cursor-pointer transition-all hover:shadow-xs"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-slate-900">
                        {appt.doctor?.name || `Doctor #${appt.doctor_id}`}
                      </span>
                      <span className="text-[11px] font-medium text-blue-600">
                        ({appt.doctor?.specialty || 'General'})
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-1">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        {formatDate(appt.appointment_date)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {formatTime(appt.start_time)}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeClass(
                      appt.status
                    )}`}
                  >
                    {appt.status.charAt(0).toUpperCase() + appt.status.slice(1)}
                  </span>
                </div>
              ))}

              {patientAppointments.length === 0 && (
                <div className="p-6 text-center text-xs text-slate-400 border border-dashed border-slate-200 rounded-xl">
                  No appointments on record for this patient.
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-semibold cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
