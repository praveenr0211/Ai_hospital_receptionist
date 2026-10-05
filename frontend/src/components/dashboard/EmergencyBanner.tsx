import React from 'react';
import { ShieldAlert, ArrowRight, PhoneForwarded } from 'lucide-react';
import type { Call } from '../../types';

interface EmergencyBannerProps {
  emergencyCalls: Call[];
  onViewCall: (call: Call) => void;
}

export const EmergencyBanner: React.FC<EmergencyBannerProps> = ({ emergencyCalls, onViewCall }) => {
  if (emergencyCalls.length === 0) return null;

  const latest = emergencyCalls[0];

  return (
    <div className="bg-[#FEF2F2] border border-[#FECACA] rounded-2xl p-4 shadow-sm mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex items-start gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-rose-100 border border-rose-200 flex items-center justify-center shrink-0">
          <ShieldAlert className="w-6 h-6 text-[#DC2626]" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-600 text-white uppercase tracking-wider">
              Critical Emergency Protocol
            </span>
            <span className="text-xs font-bold text-rose-800">
              Caller: {latest.caller_phone}
            </span>
            <span className="text-xs text-rose-600 font-medium">
              (Call ID: #{latest.id})
            </span>
          </div>

          <p className="mt-1 text-sm font-semibold text-rose-950">
            Urgent clinical symptoms identified: booking blocked to prevent delay in emergency medical intervention.
          </p>

          <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-rose-700">
            <span className="flex items-center gap-1 font-medium">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              State: Booking Blocked
            </span>
            <span className="flex items-center gap-1 font-medium">
              <PhoneForwarded className="w-3.5 h-3.5" />
              Action: Human Operator Escalation Dispatched
            </span>
            <span>
              Specialty: {latest.specialty_routed || 'Emergency Medicine'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
        <button
          onClick={() => onViewCall(latest)}
          className="flex items-center gap-1.5 bg-[#DC2626] hover:bg-rose-700 text-white font-semibold text-xs px-4 py-2 rounded-xl transition-all shadow-sm cursor-pointer"
        >
          <span>View Call Transcript</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
