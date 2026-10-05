import React, { useState } from 'react';
import { Phone, Clock, AlertTriangle, ShieldCheck, ChevronRight, Search } from 'lucide-react';
import type { Call } from '../../types';
import { getStatusBadgeClass } from '../../lib/utils';

interface CallsTableProps {
  calls: Call[];
  onSelectCall: (call: Call) => void;
}

export const CallsTable: React.FC<CallsTableProps> = ({ calls, onSelectCall }) => {
  const [filterType, setFilterType] = useState<'all' | 'emergency' | 'transferred' | 'completed'>('all');
  const [searchPhone, setSearchPhone] = useState('');

  const filteredCalls = calls.filter((c) => {
    const matchesSearch = c.caller_phone.includes(searchPhone) || c.session_id.includes(searchPhone);
    if (!matchesSearch) return false;

    if (filterType === 'emergency') return c.emergency_detected;
    if (filterType === 'transferred') return c.call_status === 'human_transfer' || c.outcome === 'human_transfer';
    if (filterType === 'completed') return c.call_status === 'completed';
    return true;
  });

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Header filter & search */}
      <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Inbound Call Logs & Transcripts</h2>
          <p className="text-xs text-slate-500 font-medium">Real-time telephony calls bridged between Exotel & Gemini Live</p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search phone number..."
              value={searchPhone}
              onChange={(e) => setSearchPhone(e.target.value)}
              className="pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
            {(['all', 'completed', 'emergency', 'transferred'] as const).map((ft) => (
              <button
                key={ft}
                onClick={() => setFilterType(ft)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize cursor-pointer transition-colors ${
                  filterType === ft
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {ft === 'emergency' ? '🚨 Emergencies' : ft}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100">
            <tr>
              <th className="py-3.5 px-5">Time</th>
              <th className="py-3.5 px-5">Caller Phone</th>
              <th className="py-3.5 px-5">Duration</th>
              <th className="py-3.5 px-5">Detected Intent</th>
              <th className="py-3.5 px-5">Safety Flags</th>
              <th className="py-3.5 px-5">Call Status</th>
              <th className="py-3.5 px-5 text-right">Transcript</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs font-medium">
            {filteredCalls.map((call) => (
              <tr key={call.id} className="hover:bg-slate-50/70 transition-colors">
                <td className="py-3.5 px-5 font-mono text-slate-500 whitespace-nowrap">
                  {new Date(call.started_at).toLocaleTimeString('en-IN', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </td>
                <td className="py-3.5 px-5 font-mono font-bold text-slate-900 whitespace-nowrap">
                  <div className="flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-blue-600" />
                    {call.caller_phone}
                  </div>
                </td>
                <td className="py-3.5 px-5 text-slate-600 whitespace-nowrap">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    {formatSeconds(call.duration_seconds)}
                  </div>
                </td>
                <td className="py-3.5 px-5">
                  <span className="font-semibold text-slate-800 capitalize">
                    {call.intent?.replace('_', ' ') || 'General Consultation'}
                  </span>
                  {call.specialty_routed && (
                    <div className="text-[11px] text-blue-600 font-medium">
                      → {call.specialty_routed}
                    </div>
                  )}
                </td>
                <td className="py-3.5 px-5 whitespace-nowrap">
                  {call.emergency_detected ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200 animate-pulse-subtle">
                      <AlertTriangle className="w-3 h-3 text-rose-600" />
                      EMERGENCY
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <ShieldCheck className="w-3 h-3 text-emerald-600" />
                      Normal
                    </span>
                  )}
                </td>
                <td className="py-3.5 px-5 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeClass(
                      call.call_status
                    )}`}
                  >
                    {call.call_status === 'human_transfer'
                      ? 'Transferred'
                      : call.call_status.toUpperCase()}
                  </span>
                </td>
                <td className="py-3.5 px-5 text-right whitespace-nowrap">
                  <button
                    onClick={() => onSelectCall(call)}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-blue-50 text-blue-700 font-semibold text-xs hover:bg-blue-100 transition-colors cursor-pointer"
                  >
                    <span>View Call</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
            {filteredCalls.length === 0 && (
              <tr>
                <td colSpan={7} className="text-center py-12 text-slate-400">
                  No call logs found matching filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
