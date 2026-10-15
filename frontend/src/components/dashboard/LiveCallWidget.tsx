import React, { useState, useEffect } from 'react';
import { Sparkles, Phone, PhoneCall, CheckCircle2, Circle, ShieldCheck, Radio, Eye, ChevronRight } from 'lucide-react';
import type { Call } from '../../types';

interface LiveCallWidgetProps {
  activeCall?: Call | null;
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

export const LiveCallWidget: React.FC<LiveCallWidgetProps> = ({ activeCall, onViewCall }) => {
  const [showDemoSimulation, setShowDemoSimulation] = useState(false);
  const [simulatedStep, setSimulatedStep] = useState(5);
  const [seconds, setSeconds] = useState(0);

  // Timer when active call or demo is running
  const isCallActive = Boolean(activeCall || showDemoSimulation);

  useEffect(() => {
    if (!isCallActive) {
      setSeconds(0);
      return;
    }
    const startMs = activeCall?.started_at ? new Date(activeCall.started_at).getTime() : 0;
    const initialElapsed = startMs > 0 ? Math.max(0, Math.floor((Date.now() - startMs) / 1000)) : 0;
    setSeconds(initialElapsed);

    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [isCallActive, activeCall?.id]);

  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Determine current caller details
  const callerPhone = activeCall?.caller_phone || (showDemoSimulation ? '+91 92325 67894 (Praveen)' : '');
  const department = activeCall?.specialty_routed || (showDemoSimulation ? 'General Medicine → Dr. Amit Roy' : 'General Medicine');

  // If NO active call and not viewing demo simulation -> IDLE STANDBY STATE
  if (!isCallActive) {
    return (
      <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 text-white rounded-2xl p-5 border border-slate-800 shadow-md relative overflow-hidden">
        {/* Subtle background ambient pulse */}
        <div className="absolute -top-12 -right-12 w-48 h-48 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-emerald-400" />
              AI Telephony Desk — Standing By
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setShowDemoSimulation(true);
                setSeconds(24);
              }}
              className="text-[11px] font-semibold text-slate-400 hover:text-white bg-slate-800/80 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700/60 transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <Eye className="w-3.5 h-3.5 text-purple-400" />
              <span>Simulate Live Call Flow</span>
            </button>
            <span className="text-[11px] font-mono text-slate-400 bg-slate-800/50 px-2.5 py-1 rounded-lg border border-slate-700/40">
              Trunk: Exotel 8000Hz PCM
            </span>
          </div>
        </div>

        {/* Standby Status Card */}
        <div className="mt-4 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-800/40 rounded-xl p-4 border border-slate-800/80">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <PhoneCall className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                <span>No Active Inbound Call</span>
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                  Ready
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                AI Receptionist is online and ready to answer calls via Exotel webhook to Gemini Live 3.8.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-[11px] font-semibold text-slate-300 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-purple-400" />
              Gemini Live 3.8
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-[11px] font-semibold text-slate-300">
              EN / TE Voice
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              Safety Protocols Active
            </span>
          </div>
        </div>
      </div>
    );
  }

  // ACTIVE LIVE CALL (OR SIMULATED DEMO)
  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950 text-white rounded-2xl p-5 border border-slate-800 shadow-md relative overflow-hidden animate-in fade-in duration-200">
      {/* Background ambient glow */}
      <div className="absolute -top-12 -right-12 w-48 h-48 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            {showDemoSimulation ? 'Live AI Call (Simulation Preview)' : 'Live AI Telephony Call'}
          </span>
        </div>

        {/* Live Audio Waveform & Timer */}
        <div className="flex items-center gap-3">
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

          {showDemoSimulation && (
            <button
              onClick={() => setShowDemoSimulation(false)}
              className="text-[11px] font-semibold text-slate-400 hover:text-white bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700 transition-colors cursor-pointer"
            >
              Exit Simulation
            </button>
          )}
        </div>
      </div>

      <div className="mt-4 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-800/60 rounded-xl p-3 border border-slate-700/60">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Phone className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Caller (Exotel Inbound)</div>
            <div className="text-sm font-bold text-white font-mono">{callerPhone}</div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-left md:text-right">
            <div className="text-xs text-slate-400">Active Routing Department</div>
            <div className="text-sm font-semibold text-purple-300">{department}</div>
          </div>

          {activeCall && onViewCall && (
            <button
              onClick={() => onViewCall(activeCall)}
              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer shadow-xs"
            >
              <span>Inspect Call</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* AI Conversation State Machine Progression */}
      <div className="mt-5">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2.5">
          <span>AI Decision & Conversation State</span>
          <span className="text-purple-300 flex items-center gap-1 font-mono">
            State: {CONVERSATION_STEPS[simulatedStep]?.label.toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-7 gap-1.5">
          {CONVERSATION_STEPS.map((step, idx) => {
            const isCompleted = idx < simulatedStep;
            const isCurrent = idx === simulatedStep;

            return (
              <div
                key={step.id}
                onClick={() => setSimulatedStep(idx)}
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
