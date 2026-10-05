import React, { useState } from 'react';
import { Search, Phone, ArrowRight } from 'lucide-react';
import type { Patient, Appointment } from '../../types';
import { formatDate } from '../../lib/utils';

interface PatientListProps {
  patients: Patient[];
  appointments: Appointment[];
  onSelectPatient: (patient: Patient) => void;
}

export const PatientList: React.FC<PatientListProps> = ({
  patients,
  appointments,
  onSelectPatient,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPatients = patients.filter((p) => {
    return (
      p.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.phone_number.includes(searchTerm) ||
      p.id.toString().includes(searchTerm)
    );
  });

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Patient Directory</h2>
          <p className="text-xs text-slate-500 font-medium">Registered patients identified via voice telephony & clinic desk</p>
        </div>

        <div className="w-full md:w-72 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search patient name or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100">
            <tr>
              <th className="py-3.5 px-5">Patient ID</th>
              <th className="py-3.5 px-5">Full Name</th>
              <th className="py-3.5 px-5">Telephone</th>
              <th className="py-3.5 px-5">Total Bookings</th>
              <th className="py-3.5 px-5">Registered Date</th>
              <th className="py-3.5 px-5 text-right">Profile</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs font-medium">
            {filteredPatients.map((patient) => {
              const patientAppts = appointments.filter((a) => a.patient_id === patient.id);
              return (
                <tr key={patient.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-5 font-mono text-slate-400 font-bold">
                    #{patient.id}
                  </td>
                  <td className="py-3.5 px-5 font-bold text-slate-900">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-full bg-blue-50 text-blue-700 border border-blue-200 flex items-center justify-center font-bold text-xs">
                        {patient.full_name.charAt(0).toUpperCase()}
                      </div>
                      <span>{patient.full_name}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-5 text-slate-700 font-mono">
                    <div className="flex items-center gap-1.5">
                      <Phone className="w-3.5 h-3.5 text-slate-400" />
                      {patient.phone_number}
                    </div>
                  </td>
                  <td className="py-3.5 px-5">
                    <span className="px-2.5 py-0.5 rounded-full bg-slate-100 font-semibold text-slate-700">
                      {patientAppts.length} appointments
                    </span>
                  </td>
                  <td className="py-3.5 px-5 text-slate-500">
                    {patient.created_at ? formatDate(patient.created_at) : 'Active'}
                  </td>
                  <td className="py-3.5 px-5 text-right">
                    <button
                      onClick={() => onSelectPatient(patient)}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                    >
                      <span>View History</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
