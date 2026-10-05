import React, { useState } from 'react';
import { Search, Calendar, Clock, Filter } from 'lucide-react';
import type { Appointment } from '../../types';
import { formatDate, formatTime, getStatusBadgeClass } from '../../lib/utils';

interface AppointmentsTableProps {
  appointments: Appointment[];
  onSelectAppointment: (appt: Appointment) => void;
  onReschedule: (appt: Appointment) => void;
  onCancel: (appt: Appointment) => void;
}

export const AppointmentsTable: React.FC<AppointmentsTableProps> = ({
  appointments,
  onSelectAppointment,
  onReschedule,
  onCancel,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredAppointments = appointments.filter((appt) => {
    const matchesSearch =
      (appt.patient?.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
      (appt.doctor?.name?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
      (appt.patient?.phone_number?.includes(searchTerm) || false) ||
      appt.id.toString().includes(searchTerm);

    const matchesStatus =
      statusFilter === 'all' || appt.status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Search and Filters Header */}
      <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex-1 max-w-md relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by patient, phone, doctor, or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <div className="flex items-center gap-1.5 overflow-x-auto">
            {['all', 'confirmed', 'pending', 'cancelled'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize cursor-pointer transition-colors ${
                  statusFilter === st
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100">
            <tr>
              <th className="py-3.5 px-5">ID</th>
              <th className="py-3.5 px-5">Date & Time</th>
              <th className="py-3.5 px-5">Patient</th>
              <th className="py-3.5 px-5">Doctor & Dept</th>
              <th className="py-3.5 px-5">Chief Complaint</th>
              <th className="py-3.5 px-5">Status</th>
              <th className="py-3.5 px-5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs font-medium">
            {filteredAppointments.map((appt) => (
              <tr key={appt.id} className="hover:bg-slate-50/70 transition-colors">
                <td className="py-3.5 px-5 font-mono text-slate-400 font-bold">
                  #{appt.id}
                </td>
                <td className="py-3.5 px-5 whitespace-nowrap text-slate-900 font-semibold">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{formatDate(appt.appointment_date)}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-500 font-normal text-[11px] mt-0.5">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>{formatTime(appt.start_time)}</span>
                  </div>
                </td>
                <td className="py-3.5 px-5 font-semibold text-slate-900">
                  {appt.patient?.full_name || `Patient #${appt.patient_id}`}
                  <div className="text-[11px] text-slate-400 font-mono font-normal">
                    {appt.patient?.phone_number || ''}
                  </div>
                </td>
                <td className="py-3.5 px-5">
                  <div className="font-semibold text-slate-800">
                    {appt.doctor?.name || `Doctor #${appt.doctor_id}`}
                  </div>
                  <span className="text-[11px] text-blue-600 font-medium">
                    {appt.doctor?.specialty || 'General'}
                  </span>
                </td>
                <td className="py-3.5 px-5 max-w-[200px] truncate text-slate-600">
                  {appt.reason || 'General Consultation'}
                </td>
                <td className="py-3.5 px-5 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeClass(
                      appt.status
                    )}`}
                  >
                    {appt.status.charAt(0).toUpperCase() + appt.status.slice(1)}
                  </span>
                </td>
                <td className="py-3.5 px-5 text-right whitespace-nowrap">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onSelectAppointment(appt)}
                      className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors cursor-pointer"
                    >
                      Details
                    </button>
                    {appt.status !== 'cancelled' && (
                      <>
                        <button
                          onClick={() => onReschedule(appt)}
                          className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors cursor-pointer"
                        >
                          Reschedule
                        </button>
                        <button
                          onClick={() => onCancel(appt)}
                          className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100 transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {filteredAppointments.length === 0 && (
              <tr>
                <td colSpan={7} className="text-center py-12 text-slate-400">
                  No appointments found matching your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
