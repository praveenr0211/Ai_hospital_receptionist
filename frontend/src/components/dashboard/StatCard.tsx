import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  isPositive?: boolean;
  icon: LucideIcon;
  colorScheme: 'blue' | 'teal' | 'violet' | 'rose' | 'amber';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  change,
  isPositive = true,
  icon: Icon,
  colorScheme,
}) => {
  const colorMap = {
    blue: {
      iconBg: 'bg-blue-50 text-blue-600 border-blue-200',
      badge: 'text-blue-700 bg-blue-50',
    },
    teal: {
      iconBg: 'bg-teal-50 text-teal-600 border-teal-200',
      badge: 'text-teal-700 bg-teal-50',
    },
    violet: {
      iconBg: 'bg-purple-50 text-purple-600 border-purple-200',
      badge: 'text-purple-700 bg-purple-50',
    },
    rose: {
      iconBg: 'bg-rose-50 text-rose-600 border-rose-200',
      badge: 'text-rose-700 bg-rose-50',
    },
    amber: {
      iconBg: 'bg-amber-50 text-amber-600 border-amber-200',
      badge: 'text-amber-700 bg-amber-50',
    },
  };

  const scheme = colorMap[colorScheme];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:-translate-y-0.5 transition-all duration-200">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${scheme.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-slate-900 tracking-tight">{value}</span>
        {change && (
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              isPositive ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
            }`}
          >
            {isPositive ? '↑' : '↓'} {change}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-1 text-xs text-slate-500 font-medium">{subtitle}</p>}
    </div>
  );
};
