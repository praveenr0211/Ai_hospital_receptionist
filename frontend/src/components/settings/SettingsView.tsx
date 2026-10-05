import React, { useState } from 'react';
import { Save, Shield, Check, Globe } from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [saved, setSaved] = useState(false);
  const [emergencyEscalation, setEmergencyEscalation] = useState(true);
  const [englishTeluguOnly, setEnglishTeluguOnly] = useState(true);
  const [fastVad, setFastVad] = useState(true);
  const [autoRegister, setAutoRegister] = useState(true);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Hospital & AI Receptionist Settings</h2>
          <p className="text-xs text-slate-500 font-medium">
            Configure hospital profiles, telephony parameters, and conversational safety protocols
          </p>
        </div>

        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-xs transition-colors cursor-pointer"
        >
          {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          <span>{saved ? 'Changes Saved!' : 'Save Configuration'}</span>
        </button>
      </div>

      {/* Hospital Information */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
          Hospital Profile
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Hospital Name</label>
            <input
              type="text"
              defaultValue="Apollo Hospital"
              className="w-full text-xs font-medium text-slate-800 p-2.5 bg-slate-50 border border-slate-200 rounded-xl"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Branch / Location</label>
            <input
              type="text"
              defaultValue="Jubilee Hills, Hyderabad, Telangana"
              className="w-full text-xs font-medium text-slate-800 p-2.5 bg-slate-50 border border-slate-200 rounded-xl"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Exotel Virtual Telephone Number</label>
            <input
              type="text"
              defaultValue="095-138-86363"
              className="w-full text-xs font-mono font-bold text-slate-800 p-2.5 bg-slate-50 border border-slate-200 rounded-xl"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Default Slot Duration</label>
            <input
              type="text"
              defaultValue="30 Minutes (Deterministic)"
              disabled
              className="w-full text-xs font-medium text-slate-500 p-2.5 bg-slate-100 border border-slate-200 rounded-xl"
            />
          </div>
        </div>
      </div>

      {/* Language Policy */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
          <Globe className="w-4 h-4 text-teal-600" />
          Language & Voice Policy
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <div className="text-xs font-bold text-slate-900">
                Lock AI to English (en-IN) & Telugu (te-IN) Only
              </div>
              <div className="text-[11px] text-slate-500">
                Enforces strict BCP-47 language codes and prompt rules to permanently block Spanish, Portuguese, or foreign phonetic hallucinations on noisy lines.
              </div>
            </div>
            <input
              type="checkbox"
              checked={englishTeluguOnly}
              onChange={(e) => setEnglishTeluguOnly(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded-sm"
            />
          </div>

          <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <div className="text-xs font-bold text-slate-900">
                Ultra-Low-Latency VAD (400ms Silence Duration)
              </div>
              <div className="text-[11px] text-slate-500">
                Cuts end-of-speech silence wait time from 1,200ms to 400ms and disables internal thinking token budget for snappier telephone responses.
              </div>
            </div>
            <input
              type="checkbox"
              checked={fastVad}
              onChange={(e) => setFastVad(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded-sm"
            />
          </div>
        </div>
      </div>

      {/* Clinical Safety & Emergency Rules */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
          <Shield className="w-4 h-4 text-rose-600" />
          Phase 4 Clinical Safety & Emergency Escalation
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3.5 bg-rose-50/60 rounded-xl border border-rose-200">
            <div>
              <div className="text-xs font-bold text-rose-950">
                Immediate Emergency Call Escalation & Booking Block
              </div>
              <div className="text-[11px] text-rose-700">
                Automatically block regular appointment booking and trigger emergency instructions (108/911 + human operator transfer) when critical symptoms (chest pain, stroke, breathing distress) are detected.
              </div>
            </div>
            <input
              type="checkbox"
              checked={emergencyEscalation}
              onChange={(e) => setEmergencyEscalation(e.target.checked)}
              className="w-4 h-4 text-rose-600 rounded-sm"
            />
          </div>

          <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <div className="text-xs font-bold text-slate-900">
                Automatic New Patient Phone Registration
              </div>
              <div className="text-[11px] text-slate-500">
                Auto-register first-time callers in PostgreSQL when booking rather than escalating to human.
              </div>
            </div>
            <input
              type="checkbox"
              checked={autoRegister}
              onChange={(e) => setAutoRegister(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded-sm"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
