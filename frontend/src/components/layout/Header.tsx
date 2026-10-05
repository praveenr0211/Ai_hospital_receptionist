import React from 'react';
import {
  Bell,
  RefreshCw,
  Sparkles,
  Phone,
  AlertTriangle,
} from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  isAiOnline: boolean;
  emergencyCount: number;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  isAiOnline,
  emergencyCount,
  onRefresh,
  isRefreshing,
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

      <div className="flex items-center gap-4">
        {/* Date display */}
        <div className="hidden md:block text-xs font-medium text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
          📅 {todayStr}
        </div>

        {/* AI Receptionist Live Pulse Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-semibold">
          {isAiOnline ? (
            <>
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-emerald-700 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                AI Receptionist Online
              </span>
            </>
          ) : (
            <>
              <span className="inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
              <span className="text-rose-700">AI Receptionist Offline</span>
            </>
          )}
        </div>

        {/* Emergency Alert indicator if any */}
        {emergencyCount > 0 && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-rose-50 border border-rose-200 text-xs font-bold text-rose-700 animate-pulse-subtle">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
            <span>{emergencyCount} Emergency Alert{emergencyCount > 1 ? 's' : ''}</span>
          </div>
        )}

        {/* Sync / Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors cursor-pointer border border-slate-200"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-blue-600' : ''}`} />
        </button>

        {/* Telephony Hotline Shortcut */}
        <a
          href="tel:09513886363"
          className="hidden lg:flex items-center gap-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
        >
          <Phone className="w-3.5 h-3.5 text-blue-600" />
          <span>Hotline: 095-138-86363</span>
        </a>

        {/* Notification Bell */}
        <div className="relative">
          <button className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors border border-slate-200">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-600"></span>
          </button>
        </div>
      </div>
    </header>
  );
};
