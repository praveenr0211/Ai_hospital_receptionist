import React from 'react';
import {
  LayoutDashboard,
  Stethoscope,
  CalendarDays,
  Users,
  PhoneCall,
  Sparkles,
  Settings,
  Activity,
  ShieldCheck,
} from 'lucide-react';

export type NavTab = 'dashboard' | 'doctors' | 'appointments' | 'patients' | 'calls' | 'ai-receptionist' | 'settings';

interface SidebarProps {
  currentTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  emergencyCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange, emergencyCount = 0 }) => {
  const navItems = [
    { id: 'dashboard' as NavTab, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'doctors' as NavTab, label: 'Doctors', icon: Stethoscope },
    { id: 'appointments' as NavTab, label: 'Appointments', icon: CalendarDays },
    { id: 'patients' as NavTab, label: 'Patients', icon: Users },
    { id: 'calls' as NavTab, label: 'Calls', icon: PhoneCall, badge: emergencyCount > 0 ? `${emergencyCount} 🚨` : undefined },
    { id: 'ai-receptionist' as NavTab, label: 'AI Receptionist', icon: Sparkles, highlight: true },
    { id: 'settings' as NavTab, label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0F172A] text-slate-300 flex flex-col shrink-0 h-screen sticky top-0 shadow-xl z-20">
      {/* Hospital Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <Activity className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="font-bold text-white tracking-tight text-base">Apollo Hospital</h1>
          </div>
          <p className="text-xs text-slate-400 font-medium flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            AI Operations Desk
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 px-3 pb-2">
          Operations
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 cursor-pointer ${
                isActive
                  ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                  : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 ${
                    isActive
                      ? 'text-white'
                      : item.highlight
                      ? 'text-purple-400'
                      : 'text-slate-400'
                  }`}
                />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* AI Telephony Status Indicator Card */}
      <div className="p-3 mx-3 mb-4 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-slate-400 font-medium">Telephony Engine</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Exotel Live
          </span>
        </div>
        <div className="text-[11px] text-slate-300 font-mono">
          Virtual: 095-138-86363
        </div>
        <div className="mt-1 text-[10px] text-slate-400">
          AI Model: Gemini 3.8-Live
        </div>
      </div>

      {/* Admin Profile Footer */}
      <div className="p-4 border-t border-slate-800 flex items-center gap-3 bg-slate-900/40">
        <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-white font-semibold text-xs border border-slate-600">
          AD
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-white truncate">Administrator</div>
          <div className="text-xs text-slate-400 truncate">Duty Receptionist</div>
        </div>
      </div>
    </aside>
  );
};
