import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const DEPT_DATA = [
  { name: 'General', count: 18, color: '#2563EB' },
  { name: 'Cardio', count: 12, color: '#0F766E' },
  { name: 'Derm', count: 9, color: '#7C3AED' },
  { name: 'Ortho', count: 8, color: '#0284C7' },
  { name: 'Pedia', count: 7, color: '#0D9488' },
  { name: 'Neuro', count: 5, color: '#6366F1' },
];

export const DepartmentDistributionChart: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Appointments by Specialty</h2>
          <p className="text-xs text-slate-500 font-medium">Departmental distribution for today</p>
        </div>
        <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100">
          59 Booked Total
        </span>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={DEPT_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F172A',
                border: 'none',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '12px',
              }}
              formatter={(value: any) => [`${value} appointments`, 'Volume']}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {DEPT_DATA.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
