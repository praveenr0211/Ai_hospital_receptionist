import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const CALL_DATA = [
  { day: 'Mon', calls: 94, booked: 38, transferred: 4 },
  { day: 'Tue', calls: 112, booked: 42, transferred: 6 },
  { day: 'Wed', calls: 108, booked: 39, transferred: 5 },
  { day: 'Thu', calls: 125, booked: 45, transferred: 7 },
  { day: 'Fri', calls: 138, booked: 49, transferred: 8 },
  { day: 'Sat', calls: 128, booked: 46, transferred: 7 },
  { day: 'Today', calls: 142, booked: 52, transferred: 6 },
];

export const CallsAnalyticsChart: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Weekly Call Volume & Resolution</h2>
          <p className="text-xs text-slate-500 font-medium">Inbound telephony calls handled by AI Receptionist</p>
        </div>
        <div className="flex items-center gap-3 text-xs font-semibold">
          <div className="flex items-center gap-1.5 text-slate-600">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
            Total Calls
          </div>
          <div className="flex items-center gap-1.5 text-slate-600">
            <span className="w-2.5 h-2.5 rounded-full bg-teal-500"></span>
            Booked
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={CALL_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="callsGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="bookedGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0F766E" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#0F766E" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F172A',
                border: 'none',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '12px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
              }}
              labelStyle={{ fontWeight: 'bold', color: '#93C5FD' }}
            />
            <Area
              type="monotone"
              dataKey="calls"
              name="Inbound Calls"
              stroke="#2563EB"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#callsGrad)"
            />
            <Area
              type="monotone"
              dataKey="booked"
              name="Appointments Booked"
              stroke="#0F766E"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#bookedGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
