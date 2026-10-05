import React from 'react';
import { X, Phone, Clock, Bot, User, AlertTriangle, ShieldCheck, Stethoscope } from 'lucide-react';
import type { Call } from '../../types';
import { getStatusBadgeClass } from '../../lib/utils';

interface CallTranscriptModalProps {
  call: Call | null;
  onClose: () => void;
}

export const CallTranscriptModal: React.FC<CallTranscriptModalProps> = ({ call, onClose }) => {
  if (!call) return null;

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-2xl w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-start justify-between shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Telephony Session Details
              </span>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${getStatusBadgeClass(
                  call.call_status
                )}`}
              >
                {call.call_status.toUpperCase()}
              </span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 mt-0.5">
              Call Session #{call.id} • {call.session_id}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metadata Banner */}
        <div className="p-4 bg-slate-100/70 border-b border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-3 shrink-0 text-xs">
          <div>
            <span className="text-slate-400 block font-medium">Caller</span>
            <span className="font-bold text-slate-900 font-mono flex items-center gap-1 mt-0.5">
              <Phone className="w-3 h-3 text-blue-600" />
              {call.caller_phone}
            </span>
          </div>

          <div>
            <span className="text-slate-400 block font-medium">Duration</span>
            <span className="font-bold text-slate-900 flex items-center gap-1 mt-0.5">
              <Clock className="w-3 h-3 text-slate-500" />
              {formatSeconds(call.duration_seconds)}
            </span>
          </div>

          <div>
            <span className="text-slate-400 block font-medium">Routed Specialty</span>
            <span className="font-bold text-blue-600 flex items-center gap-1 mt-0.5">
              <Stethoscope className="w-3 h-3 text-teal-600" />
              {call.specialty_routed || 'General Medicine'}
            </span>
          </div>

          <div>
            <span className="text-slate-400 block font-medium">Safety Status</span>
            <span className="font-bold mt-0.5 block">
              {call.emergency_detected ? (
                <span className="text-rose-600 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Emergency
                </span>
              ) : (
                <span className="text-emerald-600 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" /> Standard
                </span>
              )}
            </span>
          </div>
        </div>

        {/* Transcript Dialogue Scroll Container */}
        <div className="p-6 overflow-y-auto flex-1 space-y-3.5 bg-slate-50/50">
          <div className="text-center">
            <span className="px-3 py-1 bg-slate-200/70 text-slate-600 rounded-full text-[10px] font-semibold tracking-wider uppercase">
              Bidirectional Audio Transcript (Gemini Live 3.8 Speech-to-Speech)
            </span>
          </div>

          {call.transcript && call.transcript.length > 0 ? (
            call.transcript.map((msg, index) => {
              if (msg.speaker === 'safety') {
                return (
                  <div
                    key={index}
                    className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 font-semibold flex items-start gap-2 shadow-xs"
                  >
                    <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                    <div>{msg.message}</div>
                  </div>
                );
              }

              const isAi = msg.speaker === 'ai';
              return (
                <div
                  key={index}
                  className={`flex gap-3 ${isAi ? 'justify-start' : 'justify-end'}`}
                >
                  {isAi && (
                    <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[80%] p-3.5 rounded-2xl text-xs ${
                      isAi
                        ? 'bg-white border border-slate-200 text-slate-800 shadow-xs rounded-tl-sm'
                        : 'bg-blue-600 text-white shadow-xs rounded-tr-sm'
                    }`}
                  >
                    <div className="text-[10px] font-bold mb-1 opacity-70">
                      {isAi ? '🤖 Apollo AI Receptionist' : '👤 Caller'}
                    </div>
                    <p className="leading-relaxed font-medium">{msg.message}</p>
                  </div>

                  {!isAi && (
                    <div className="w-8 h-8 rounded-xl bg-slate-700 text-white flex items-center justify-center shrink-0 shadow-xs">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="py-8 text-center text-xs text-slate-400">
              No detailed speech transcript recorded for this session.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-white border-t border-slate-200 flex items-center justify-between shrink-0 text-xs">
          <span className="text-slate-400">
            Audio stream: 8kHz PCM telephony ↔ 16kHz PCM Google GenAI Live
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
