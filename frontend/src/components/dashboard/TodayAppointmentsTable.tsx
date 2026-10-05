import React from 'react';
import { Calendar, Clock, ChevronRight } from 'lucide-react';
import type { Appointment } from '../../types';
import { formatTime, getStatusBadgeClass } from '../../lib/utils';

interface TodayAppointmentsTableProps {
  appointments: Appointment[];
  onViewDetails: (appt: Appointment) => void;
  onViewAll: () => void;
}

export const TodayAppointmentsTable: React.FC<TodayAppointmentsTableProps> = ({
  appointments,
  onViewDetails,
  onViewAll,
}) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Today's Appointment Schedule</h2>
          <p className="text-xs text-slate-500 font-medium">Real-time bookings coordinated by AI Receptionist</p>
        </div>
        <button
          onClick={onViewAll}
          className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 cursor-pointer transition-colors"
        >
          View All Appointments
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100">
            <tr>
              <th className="py-3 px-4">Time</th>
              <th className="py-3 px-4">Patient</th>
              <th className="py-3 px-4">Doctor</th>
              <th className="py-3 px-4">Department</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-xs">
            {appointments.slice(0, 6).map((appt) => (
              <tr key={appt.id} className="hover:bg-slate-50/60 transition-colors">
                <td className="py-3 px-4 text-slate-900 font-semibold whitespace-nowrap">
                  <div className="flex items-center gap-1.5 text-slate-800">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    {formatTime(appt.start_time)}
                  </div>
                </td>
                <td className="py-3 px-4 font-semibold text-slate-900">
                  {appt.patient?.full_name || `Patient #${appt.patient_id}`}
                  <div className="text-[11px] text-slate-400 font-mono font-normal">
                    {appt.patient?.phone_number || ''}
                  </div>
                </td>
                <td className="py-3 px-4 text-slate-800">
                  {appt.doctor?.name || `Dr. ID #${appt.doctor_id}`}
                </td>
                <td className="py-3 px-4">
                  <span className="inline-block px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-medium">
                    {appt.doctor?.specialty || 'General'}
                  </span>
                </td>
                <td className="py-3 px-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeClass(
                      appt.status
                    )}`}
                  >
                    {appt.status.charAt(0).toUpperCase() + appt.status.slice(1)}
                  </span>
                </td>
                <td className="py-3 px-4 text-right whitespace-nowrap">
                  <button
                    onClick={() => onViewDetails(appt)}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                  >
                    Manage
                  </button>
                </td>
              </tr>
            ))}
            {appointments.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-8 text-slate-400">
                  <Calendar className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                  No appointments booked for today yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
