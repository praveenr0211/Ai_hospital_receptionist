import React, { useState, useEffect, useCallback } from 'react';
import {
  Sidebar,
  type NavTab,
} from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { StatCard } from './components/dashboard/StatCard';
import { EmergencyBanner } from './components/dashboard/EmergencyBanner';
import { LiveCallWidget } from './components/dashboard/LiveCallWidget';
import { CallsAnalyticsChart } from './components/dashboard/CallsAnalyticsChart';
import { DepartmentDistributionChart } from './components/dashboard/DepartmentDistributionChart';
import { TodayAppointmentsTable } from './components/dashboard/TodayAppointmentsTable';

import { DoctorCard } from './components/doctors/DoctorCard';
import { DoctorScheduleModal } from './components/doctors/DoctorScheduleModal';

import { AppointmentsTable } from './components/appointments/AppointmentsTable';
import { AppointmentDetailModal } from './components/appointments/AppointmentDetailModal';
import { RescheduleModal } from './components/appointments/RescheduleModal';

import { PatientList } from './components/patients/PatientList';
import { PatientProfileModal } from './components/patients/PatientProfileModal';

import { CallsTable } from './components/calls/CallsTable';
import { CallTranscriptModal } from './components/calls/CallTranscriptModal';

import { AIReceptionistView } from './components/ai/AIReceptionistView';
import { SettingsView } from './components/settings/SettingsView';

import { api } from './lib/api';
import type {
  Doctor,
  Appointment,
  Patient,
  Call,
  DashboardSummary,
} from './types';
import {
  PhoneCall,
  CalendarCheck,
  Stethoscope,
  Sparkles,
} from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [isAiOnline, setIsAiOnline] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Core Data
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [calls, setCalls] = useState<Call[]>([]);
  const [specialties, setSpecialties] = useState<string[]>([]);
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>('All');

  // Modals state
  const [selectedDoctorForSchedule, setSelectedDoctorForSchedule] = useState<Doctor | null>(null);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [appointmentToReschedule, setAppointmentToReschedule] = useState<Appointment | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);

  // Fetch all initial data
  const loadData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [sum, docs, appts, pats, clls, specs, health] = await Promise.all([
        api.getDashboardSummary(),
        api.getDoctors(),
        api.getAppointments(),
        api.getPatients(),
        api.getCalls(),
        api.getSpecialties(),
        api.checkHealth(),
      ]);

      setSummary(sum);
      setDoctors(docs);
      setAppointments(appts);
      setPatients(pats);
      setCalls(clls);
      setSpecialties(specs);
      setIsAiOnline(health.status === 'ok');
    } catch {
      // Fallback handlers inside api.ts provide offline defaults
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Poll updates every 25 seconds
    const interval = setInterval(loadData, 25000);
    return () => clearInterval(interval);
  }, [loadData]);

  // Emergency calls filter
  const emergencyCalls = calls.filter((c) => c.emergency_detected);

  // Cancel handler
  const handleCancelAppointment = async (apptId: number, reason: string) => {
    try {
      await api.cancelAppointment(apptId, reason);
      setAppointments((prev) =>
        prev.map((a) =>
          a.id === apptId ? { ...a, status: 'cancelled', cancellation_reason: reason } : a
        )
      );
    } catch (err) {
      alert(`Cancellation failed: ${err}`);
    }
  };

  // Doctors filter
  const filteredDoctors =
    selectedSpecialty === 'All'
      ? doctors
      : doctors.filter(
          (d) => d.specialty.toLowerCase() === selectedSpecialty.toLowerCase()
        );

  const getPageTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return { title: 'Hospital Operations Dashboard', subtitle: 'Overview of telephony calls, scheduled appointments, and clinical safety' };
      case 'doctors':
        return { title: 'Doctors & Medical Specialists', subtitle: 'Specialist directories, consultation fees, and schedule calendars' };
      case 'appointments':
        return { title: 'Appointment Registry', subtitle: 'Deterministic appointments booked by AI Receptionist and desk staff' };
      case 'patients':
        return { title: 'Registered Patients', subtitle: 'Patient directory and historical appointment consultation logs' };
      case 'calls':
        return { title: 'Telephony & Voice Call Records', subtitle: 'Exotel inbound call sessions, speech transcripts, and clinical routing outcomes' };
      case 'ai-receptionist':
        return { title: 'AI Receptionist Live Engine', subtitle: 'Gemini Live 3.8 speech agent telemetry, state machine, and accuracy benchmarks' };
      case 'settings':
        return { title: 'System & Safety Settings', subtitle: 'Hospital configurations, language restrictions, and emergency protocols' };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        emergencyCount={emergencyCalls.length}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          title={title}
          subtitle={subtitle}
          isAiOnline={isAiOnline}
          emergencyCount={emergencyCalls.length}
          onRefresh={loadData}
          isRefreshing={isRefreshing}
        />

        <main className="p-6 md:p-8 flex-1 overflow-y-auto">
          {/* TAB 1: DASHBOARD */}
          {currentTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Emergency Protocol Banner */}
              <EmergencyBanner
                emergencyCalls={emergencyCalls}
                onViewCall={(c) => setSelectedCall(c)}
              />

              {/* Top 4 Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Today's Inbound Calls"
                  value={summary?.calls_today || 128}
                  subtitle="Handled by AI Voicebot"
                  change="12.4%"
                  isPositive={true}
                  icon={PhoneCall}
                  colorScheme="blue"
                />
                <StatCard
                  title="Appointments Booked"
                  value={summary?.appointments_today || 46}
                  subtitle="38 Confirmed, 4 Pending"
                  change="8.1%"
                  isPositive={true}
                  icon={CalendarCheck}
                  colorScheme="teal"
                />
                <StatCard
                  title="Active Specialists"
                  value={`${summary?.active_doctors || 14} / ${summary?.total_doctors || 16}`}
                  subtitle="Available on Duty"
                  icon={Stethoscope}
                  colorScheme="violet"
                />
                <StatCard
                  title="AI Call Resolution"
                  value={`${summary?.ai_resolution_rate || 91.2}%`}
                  subtitle="Without human intervention"
                  change="4.2%"
                  isPositive={true}
                  icon={Sparkles}
                  colorScheme="amber"
                />
              </div>

              {/* Live Call Widget with animated waveform and state tracker */}
              <LiveCallWidget onViewCall={(c) => setSelectedCall(c)} />

              {/* Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <CallsAnalyticsChart />
                <DepartmentDistributionChart />
              </div>

              {/* Today's Appointments Table */}
              <TodayAppointmentsTable
                appointments={appointments}
                onViewDetails={(a) => setSelectedAppointment(a)}
                onViewAll={() => setCurrentTab('appointments')}
              />
            </div>
          )}

          {/* TAB 2: DOCTORS */}
          {currentTab === 'doctors' && (
            <div className="space-y-6">
              {/* Department Filter Bar */}
              <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between gap-4 overflow-x-auto">
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
                  {['All', ...specialties].map((spec) => (
                    <button
                      key={spec}
                      onClick={() => setSelectedSpecialty(spec)}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap cursor-pointer transition-all ${
                        selectedSpecialty === spec
                          ? 'bg-blue-600 text-white shadow-xs'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      {spec}
                    </button>
                  ))}
                </div>

                <span className="text-xs font-bold text-slate-500 shrink-0">
                  {filteredDoctors.length} Doctors
                </span>
              </div>

              {/* Doctors Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {filteredDoctors.map((doc) => (
                  <DoctorCard
                    key={doc.id}
                    doctor={doc}
                    onViewSchedule={(d) => setSelectedDoctorForSchedule(d)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: APPOINTMENTS */}
          {currentTab === 'appointments' && (
            <AppointmentsTable
              appointments={appointments}
              onSelectAppointment={(a) => setSelectedAppointment(a)}
              onReschedule={(a) => setAppointmentToReschedule(a)}
              onCancel={(a) => setSelectedAppointment(a)}
            />
          )}

          {/* TAB 4: PATIENTS */}
          {currentTab === 'patients' && (
            <PatientList
              patients={patients}
              appointments={appointments}
              onSelectPatient={(p) => setSelectedPatient(p)}
            />
          )}

          {/* TAB 5: CALLS */}
          {currentTab === 'calls' && (
            <CallsTable
              calls={calls}
              onSelectCall={(c) => setSelectedCall(c)}
            />
          )}

          {/* TAB 6: AI RECEPTIONIST MONITORING */}
          {currentTab === 'ai-receptionist' && (
            <AIReceptionistView summary={summary || {
              total_doctors: 16,
              active_doctors: 14,
              total_patients: 65,
              appointments_today: 46,
              confirmed_appointments: 38,
              cancelled_appointments: 4,
              calls_today: 128,
              successful_bookings_today: 42,
              escalated_calls_today: 7,
              ai_resolution_rate: 91.2,
              reference_date: '2026-10-05',
            }} />
          )}

          {/* TAB 7: SETTINGS */}
          {currentTab === 'settings' && <SettingsView />}
        </main>
      </div>

      {/* Global Interactive Modals */}
      {selectedDoctorForSchedule && (
        <DoctorScheduleModal
          doctor={selectedDoctorForSchedule}
          onClose={() => setSelectedDoctorForSchedule(null)}
        />
      )}

      {selectedAppointment && (
        <AppointmentDetailModal
          appointment={selectedAppointment}
          onClose={() => setSelectedAppointment(null)}
          onConfirmCancel={handleCancelAppointment}
          onOpenReschedule={(a) => setAppointmentToReschedule(a)}
        />
      )}

      {appointmentToReschedule && (
        <RescheduleModal
          appointment={appointmentToReschedule}
          onClose={() => setAppointmentToReschedule(null)}
          onSuccess={loadData}
        />
      )}

      {selectedPatient && (
        <PatientProfileModal
          patient={selectedPatient}
          appointments={appointments}
          onClose={() => setSelectedPatient(null)}
          onSelectAppointment={(a) => setSelectedAppointment(a)}
        />
      )}

      {selectedCall && (
        <CallTranscriptModal
          call={selectedCall}
          onClose={() => setSelectedCall(null)}
        />
      )}
    </div>
  );
};

export default App;
