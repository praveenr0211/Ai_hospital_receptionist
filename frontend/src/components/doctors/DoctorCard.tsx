import React from 'react';
import { Calendar, Award, Clock } from 'lucide-react';
import type { Doctor } from '../../types';
import { formatCurrency } from '../../lib/utils';

interface DoctorCardProps {
  doctor: Doctor;
  onViewSchedule: (doctor: Doctor) => void;
}

export const DoctorCard: React.FC<DoctorCardProps> = ({ doctor, onViewSchedule }) => {
  const isAvailable = doctor.status === 'active';

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:-translate-y-1 transition-all duration-200 flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 font-bold text-base">
              {doctor.name.replace('Dr. ', '').slice(0, 2).toUpperCase()}
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 leading-tight">{doctor.name}</h3>
              <p className="text-xs font-semibold text-blue-600 mt-0.5">{doctor.specialty}</p>
            </div>
          </div>

          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
              isAvailable
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${isAvailable ? 'bg-emerald-500' : 'bg-amber-500'}`}
            ></span>
            {isAvailable ? 'Available' : 'On Leave'}
          </span>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 text-xs text-slate-600">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium">Qualification:</span>
            <span className="font-semibold text-slate-700 truncate max-w-[160px]">
              {doctor.qualification || 'MBBS, MD'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-slate-400" />
              Experience:
            </span>
            <span className="font-semibold text-slate-700">
              {doctor.experience_years ? `${doctor.experience_years} Years` : '10+ Years'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium">Consultation Fee:</span>
            <span className="font-bold text-slate-900">{formatCurrency(doctor.consultation_fee)}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              Slot Duration:
            </span>
            <span className="font-semibold text-slate-700">30 minutes</span>
          </div>
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center gap-2">
        <button
          onClick={() => onViewSchedule(doctor)}
          className="w-full flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs py-2.5 px-3 rounded-xl transition-colors cursor-pointer shadow-xs"
        >
          <Calendar className="w-3.5 h-3.5" />
          <span>View Availability & Slots</span>
        </button>
      </div>
    </div>
  );
};
