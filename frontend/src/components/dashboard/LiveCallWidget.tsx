import React, { useState, useEffect } from 'react';
import { Sparkles, Phone, CheckCircle2, Circle } from 'lucide-react';
import type { Call } from '../../types';

interface LiveCallWidgetProps {
  onViewCall?: (call: Call) => void;
}

const CONVERSATION_STEPS = [
  { id: 'greeting', label: 'Greeting' },
  { id: 'identify', label: 'Patient ID' },
  { id: 'symptoms', label: 'Symptoms' },
  { id: 'routing', label: 'Medical Routing' },
  { id: 'doctor', label: 'Doctor Choice' },
  { id: 'availability', label: 'Check Slots' },
  { id: 'booking', label: 'Booked' },
];

export const LiveCallWidget: React.FC<LiveCallWidgetProps> = () => {
  const [activeStepIndex, setActiveStepIndex] = useState(5); // Checking availability
  const [seconds, setSeconds] = useState(84); // 01:24

  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950 text-white rounded-2xl p-5 border border-slate-800 shadow-md relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute -top-12 -right-12 w-48 h-48 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            Live AI Telephony Call
          </span>
        </div>

        {/* Live Audio Waveform Animation */}
        <div className="flex items-center gap-1">
          <span className="w-1 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_100ms] h-3"></span>
          <span className="w-1 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_300ms] h-5"></span>
          <span className="w-1 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_200ms] h-2"></span>
          <span className="w-1 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_400ms] h-6"></span>
          <span className="w-1 bg-emerald-400 rounded-full animate-[bounce_1s_infinite_150ms] h-4"></span>
          <span className="text-xs font-mono font-semibold text-emerald-400 ml-2">
            {formatDuration(seconds)}
          </span>
        </div>
      </div>

      <div className="mt-4 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-800/60 rounded-xl p-3 border border-slate-700/60">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Phone className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Caller (Exotel Inbound)</div>
            <div className="text-sm font-bold text-white font-mono">+91 92325 67894 (Praveen)</div>
          </div>
        </div>

        <div className="text-left md:text-right">
          <div className="text-xs text-slate-400">Active Routing Department</div>
          <div className="text-sm font-semibold text-purple-300">
            General Medicine → Dr. Amit Roy
          </div>
        </div>
      </div>

      {/* AI Conversation State Machine Progression */}
      <div className="mt-5">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2.5">
          <span>AI Decision & Conversation State</span>
          <span className="text-purple-300 flex items-center gap-1 font-mono">
            State: {CONVERSATION_STEPS[activeStepIndex]?.label.toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-7 gap-1.5">
          {CONVERSATION_STEPS.map((step, idx) => {
            const isCompleted = idx < activeStepIndex;
            const isCurrent = idx === activeStepIndex;

            return (
              <div
                key={step.id}
                onClick={() => setActiveStepIndex(idx)}
                className={`flex flex-col items-center justify-center py-2 px-1 rounded-lg text-center cursor-pointer transition-all ${
                  isCurrent
                    ? 'bg-blue-600 text-white font-bold ring-2 ring-blue-400/50 scale-105'
                    : isCompleted
                    ? 'bg-slate-800 text-emerald-400 font-medium'
                    : 'bg-slate-800/40 text-slate-500'
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-3.5 h-3.5 mb-1 text-emerald-400" />
                ) : isCurrent ? (
                  <span className="w-2.5 h-2.5 rounded-full bg-white mb-1.5 animate-ping"></span>
                ) : (
                  <Circle className="w-3.5 h-3.5 mb-1 text-slate-600" />
                )}
                <span className="text-[10px] leading-tight truncate w-full">{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
