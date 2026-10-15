import React from 'react';
import { Calendar } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  isAiOnline?: boolean;
  emergencyCount?: number;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
}) => {
  const todayStr = new Intl.DateTimeFormat('en-IN', {
    weekday: 'long',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date());

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10 shadow-xs">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500 font-medium">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Only Date in Navbar */}
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 bg-slate-50 px-3.5 py-1.5 rounded-xl border border-slate-200 shadow-2xs">
          <Calendar className="w-4 h-4 text-blue-600" />
          <span>{todayStr}</span>
        </div>
      </div>
    </header>
  );
};
