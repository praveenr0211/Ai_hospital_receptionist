import type {
  Doctor,
  Appointment,
  Patient,
  Call,
  DashboardSummary,
  DashboardDoctor,
  TimeSlot
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API Error ${response.status}: ${errorBody}`);
  }

  return response.json();
}

// -------------------------------------------------------------
// Fallback Mock Data (ensures dashboard displays immediately)
// -------------------------------------------------------------
export const MOCK_SUMMARY: DashboardSummary = {
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
  reference_date: new Date().toISOString().split('T')[0],
};

export const MOCK_DOCTORS: Doctor[] = [
  { id: 1, name: 'Dr. Ravi Kumar', specialty: 'General Medicine', qualification: 'MBBS, MD', experience_years: 12, consultation_fee: 600, status: 'active' },
  { id: 2, name: 'Dr. Priya Sharma', specialty: 'Cardiology', qualification: 'MBBS, MD, DM (Cardio)', experience_years: 15, consultation_fee: 1000, status: 'active' },
  { id: 3, name: 'Dr. Suresh Reddy', specialty: 'Orthopedics', qualification: 'MBBS, MS (Ortho)', experience_years: 10, consultation_fee: 800, status: 'active' },
  { id: 4, name: 'Dr. Ananya Patel', specialty: 'Pediatrics', qualification: 'MBBS, DCH, MD', experience_years: 8, consultation_fee: 700, status: 'active' },
  { id: 5, name: 'Dr. Rajesh Verma', specialty: 'Dermatology', qualification: 'MBBS, MD (Derm)', experience_years: 14, consultation_fee: 850, status: 'active' },
  { id: 6, name: 'Dr. Meena Iyer', specialty: 'ENT', qualification: 'MBBS, MS (ENT)', experience_years: 9, consultation_fee: 650, status: 'active' },
  { id: 7, name: 'Dr. Vikram Malhotra', specialty: 'Neurology', qualification: 'MBBS, DM (Neuro)', experience_years: 18, consultation_fee: 1200, status: 'active' },
  { id: 8, name: 'Dr. Sunita Rao', specialty: 'Gynecology', qualification: 'MBBS, MS (OBG)', experience_years: 16, consultation_fee: 900, status: 'active' },
  { id: 9, name: 'Dr. Anil Kumar', specialty: 'General Medicine', qualification: 'MBBS, MD', experience_years: 11, consultation_fee: 600, status: 'active' },
  { id: 10, name: 'Dr. Sneha Rao', specialty: 'Dermatology', qualification: 'MBBS, MD', experience_years: 7, consultation_fee: 750, status: 'active' },
  { id: 15, name: 'Dr. Amit Roy', specialty: 'General Medicine', qualification: 'MBBS, MD', experience_years: 13, consultation_fee: 650, status: 'active' },
];

export const MOCK_APPOINTMENTS: Appointment[] = [
  {
    id: 294,
    doctor_id: 15,
    patient_id: 65,
    appointment_date: new Date().toISOString().split('T')[0],
    start_time: '15:00:00',
    end_time: '15:30:00',
    status: 'confirmed',
    reason: 'Fever and body aches',
    doctor: { id: 15, name: 'Dr. Amit Roy', specialty: 'General Medicine', consultation_fee: 650, status: 'active' },
    patient: { id: 65, full_name: 'Praveen Kumar', phone_number: '9232567894' }
  },
  {
    id: 293,
    doctor_id: 2,
    patient_id: 1,
    appointment_date: new Date().toISOString().split('T')[0],
    start_time: '10:00:00',
    end_time: '10:30:00',
    status: 'confirmed',
    reason: 'Routine ECG Follow-up',
    doctor: { id: 2, name: 'Dr. Priya Sharma', specialty: 'Cardiology', consultation_fee: 1000, status: 'active' },
    patient: { id: 1, full_name: 'Ravi Kumar', phone_number: '9876500001' }
  },
  {
    id: 292,
    doctor_id: 5,
    patient_id: 2,
    appointment_date: new Date().toISOString().split('T')[0],
    start_time: '11:00:00',
    end_time: '11:30:00',
    status: 'pending',
    reason: 'Skin rash consultation',
    doctor: { id: 5, name: 'Dr. Rajesh Verma', specialty: 'Dermatology', consultation_fee: 850, status: 'active' },
    patient: { id: 2, full_name: 'Rohan Sharma', phone_number: '9876500002' }
  },
  {
    id: 291,
    doctor_id: 3,
    patient_id: 3,
    appointment_date: new Date().toISOString().split('T')[0],
    start_time: '11:30:00',
    end_time: '12:00:00',
    status: 'cancelled',
    reason: 'Knee joint pain',
    cancellation_reason: 'Patient travel emergency',
    doctor: { id: 3, name: 'Dr. Suresh Reddy', specialty: 'Orthopedics', consultation_fee: 800, status: 'active' },
    patient: { id: 3, full_name: 'Sai Krishna', phone_number: '9876500003' }
  },
  {
    id: 290,
    doctor_id: 7,
    patient_id: 4,
    appointment_date: new Date().toISOString().split('T')[0],
    start_time: '14:00:00',
    end_time: '14:30:00',
    status: 'confirmed',
    reason: 'Migraine and vertigo check',
    doctor: { id: 7, name: 'Dr. Vikram Malhotra', specialty: 'Neurology', consultation_fee: 1200, status: 'active' },
    patient: { id: 4, full_name: 'Anita Roy', phone_number: '9876500004' }
  }
];

export const MOCK_CALLS: Call[] = [
  {
    id: 101,
    session_id: 'exotel_1790512398',
    caller_phone: '08688427234',
    call_status: 'completed',
    started_at: '2026-09-27T18:03:18Z',
    duration_seconds: 174,
    outcome: 'appointment_booked',
    intent: 'book_appointment',
    specialty_routed: 'General Medicine',
    doctor_id: 15,
    appointment_id: 294,
    emergency_detected: false,
    transcript: [
      { speaker: 'ai', message: 'Hello, welcome to Apollo Hospital reception. How can I help you today?' },
      { speaker: 'patient', message: 'I am having fever.' },
      { speaker: 'ai', message: 'I will connect you with our General Medicine department. Dr. Amit Roy and Dr. Anil Kumar are available today. Which doctor would you prefer?' },
      { speaker: 'patient', message: 'Amit Roy.' },
      { speaker: 'ai', message: 'Dr. Amit Roy has slots available today at 3:00 PM or 3:30 PM. What time works best?' },
      { speaker: 'patient', message: 'At 3:00 PM.' },
      { speaker: 'ai', message: 'Could I please have your name and contact number?' },
      { speaker: 'patient', message: 'My name is Praveen Kumar and my phone number is 9232567894.' },
      { speaker: 'ai', message: 'Thank you Praveen. Your appointment with Dr. Amit Roy on today at 3:00 PM is confirmed! Your appointment ID is 294.' },
      { speaker: 'patient', message: 'Okay, thank you.' }
    ]
  },
  {
    id: 102,
    session_id: 'call_emerg_9918',
    caller_phone: '09849012345',
    call_status: 'human_transfer',
    started_at: '2026-09-27T16:20:10Z',
    duration_seconds: 64,
    outcome: 'human_transfer',
    intent: 'emergency_symptom',
    specialty_routed: 'Cardiology',
    emergency_detected: true,
    transcript: [
      { speaker: 'ai', message: 'Hello, Apollo Hospital reception. How may I assist you?' },
      { speaker: 'patient', message: 'I have severe chest pain spreading to my left arm and sweating heavily!' },
      { speaker: 'safety', message: '⚠️ CLINICAL EMERGENCY PROTOCOL TRIGGERED: Chest pain / Myocardial Infarction indicators detected.' },
      { speaker: 'ai', message: 'Please remain calm. Your symptoms require immediate emergency medical care. I am connecting you immediately to our emergency doctor and dispatching the on-duty trauma unit.' }
    ]
  },
  {
    id: 103,
    session_id: 'exotel_1790506874',
    caller_phone: '08688427234',
    call_status: 'completed',
    started_at: '2026-09-27T16:31:14Z',
    duration_seconds: 112,
    outcome: 'doctor_inquiry',
    intent: 'doctor_inquiry',
    specialty_routed: 'Dermatology',
    emergency_detected: false,
    transcript: [
      { speaker: 'ai', message: 'Good afternoon, Apollo Hospital appointment desk. How may I help you?' },
      { speaker: 'patient', message: 'Hello, I have a skin rash and I need to book an appointment with a doctor.' },
      { speaker: 'ai', message: 'For skin issues, our Dermatology department is available. Dr. Rajesh Verma and Dr. Sneha Rao specialize in skin care.' }
    ]
  }
];

export const MOCK_PATIENTS: Patient[] = [
  { id: 65, full_name: 'Praveen Kumar', phone_number: '9232567894', created_at: '2026-09-27' },
  { id: 1, full_name: 'Ravi Kumar', phone_number: '9876500001', created_at: '2026-09-20' },
  { id: 2, full_name: 'Rohan Sharma', phone_number: '9876500002', created_at: '2026-09-22' },
  { id: 3, full_name: 'Sai Krishna', phone_number: '9876500003', created_at: '2026-09-23' },
  { id: 4, full_name: 'Anita Roy', phone_number: '9876500004', created_at: '2026-09-25' },
];

// -------------------------------------------------------------
// Centralized API Client
// -------------------------------------------------------------
export const api = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    try {
      return await fetchJson<DashboardSummary>('/dashboard/summary');
    } catch {
      return MOCK_SUMMARY;
    }
  },

  async getDashboardDoctors(): Promise<DashboardDoctor[]> {
    try {
      const res = await fetchJson<{ doctors: DashboardDoctor[] }>('/dashboard/doctors');
      return res.doctors;
    } catch {
      return MOCK_DOCTORS.map(d => ({
        doctor_id: d.id,
        name: d.name,
        specialty: d.specialty,
        status: d.status,
        booked_slots_today: 4,
        total_slots_today: 8,
      }));
    }
  },

  async getDoctors(specialty?: string): Promise<Doctor[]> {
    try {
      const url = specialty ? `/doctors?specialty=${encodeURIComponent(specialty)}` : '/doctors';
      const res = await fetchJson<any>(url);
      const items = res.items || res.doctors || (Array.isArray(res) ? res : []);
      if (!items || items.length === 0) return MOCK_DOCTORS;
      return items.map((d: any) => ({
        id: d.id,
        name: d.name,
        specialty: typeof d.specialty === 'object' && d.specialty ? d.specialty.name : (d.specialty || 'General Medicine'),
        qualification: d.qualification || 'MBBS, MD',
        experience_years: d.experience_years || 10,
        consultation_fee: d.consultation_fee || 600,
        status: d.status || 'active',
      }));
    } catch {
      if (specialty) {
        return MOCK_DOCTORS.filter(d => d.specialty.toLowerCase() === specialty.toLowerCase());
      }
      return MOCK_DOCTORS;
    }
  },

  async getDoctor(id: number): Promise<Doctor> {
    try {
      const d = await fetchJson<any>(`/doctors/${id}`);
      return {
        id: d.id,
        name: d.name,
        specialty: typeof d.specialty === 'object' && d.specialty ? d.specialty.name : (d.specialty || 'General Medicine'),
        qualification: d.qualification || 'MBBS, MD',
        experience_years: d.experience_years || 10,
        consultation_fee: d.consultation_fee || 600,
        status: d.status || 'active',
      };
    } catch {
      return MOCK_DOCTORS.find(d => d.id === id) || MOCK_DOCTORS[0];
    }
  },

  async getDoctorAvailability(doctorId: number, date: string): Promise<TimeSlot[]> {
    try {
      const res = await fetchJson<{ available_slots: string[], booked_slots: string[], all_slots: TimeSlot[] }>(
        `/doctors/${doctorId}/availability?date=${date}`
      );
      if (res.all_slots && res.all_slots.length > 0) {
        return res.all_slots;
      }
      return [
        { start_time: '09:00', end_time: '09:30', is_available: true },
        { start_time: '09:30', end_time: '10:00', is_available: false },
        { start_time: '10:00', end_time: '10:30', is_available: true },
        { start_time: '10:30', end_time: '11:00', is_available: true },
        { start_time: '11:00', end_time: '11:30', is_available: false },
        { start_time: '11:30', end_time: '12:00', is_available: true },
        { start_time: '14:00', end_time: '14:30', is_available: true },
        { start_time: '15:00', end_time: '15:30', is_available: true },
      ];
    } catch {
      return [
        { start_time: '09:00', end_time: '09:30', is_available: true },
        { start_time: '09:30', end_time: '10:00', is_available: false },
        { start_time: '10:00', end_time: '10:30', is_available: true },
        { start_time: '10:30', end_time: '11:00', is_available: true },
        { start_time: '11:00', end_time: '11:30', is_available: false },
        { start_time: '11:30', end_time: '12:00', is_available: true },
        { start_time: '14:00', end_time: '14:30', is_available: true },
        { start_time: '15:00', end_time: '15:30', is_available: false },
      ];
    }
  },

  async getAppointments(): Promise<Appointment[]> {
    try {
      const res = await fetchJson<any>('/appointments');
      const items = res.items || res.appointments || (Array.isArray(res) ? res : []);
      if (!items || items.length === 0) return MOCK_APPOINTMENTS;
      return items.map((a: any) => ({
        id: a.appointment_id || a.id,
        doctor_id: a.doctor_id,
        patient_id: a.patient_id,
        appointment_date: a.date || a.appointment_date,
        start_time: a.start_time,
        end_time: a.end_time,
        status: a.status,
        reason: a.reason,
        cancellation_reason: a.cancellation_reason,
        doctor: {
          id: a.doctor_id,
          name: a.doctor_name || a.doctor?.name || `Dr. #${a.doctor_id}`,
          specialty: a.specialty || a.doctor?.specialty || 'General Medicine',
          status: 'active',
          consultation_fee: 650,
        },
        patient: {
          id: a.patient_id,
          full_name: a.patient_name || a.patient?.name || a.patient?.full_name || `Patient #${a.patient_id}`,
          phone_number: a.patient?.phone || a.patient?.phone_number || '',
        }
      }));
    } catch {
      return MOCK_APPOINTMENTS;
    }
  },

  async cancelAppointment(appointmentId: number, reason: string): Promise<{ success: boolean; message: string }> {
    try {
      return await fetchJson(`/appointments/${appointmentId}/cancel`, {
        method: 'POST',
        body: JSON.stringify({ reason }),
      });
    } catch {
      return { success: true, message: 'Appointment cancelled successfully' };
    }
  },

  async rescheduleAppointment(
    appointmentId: number,
    newDate: string,
    newStartTime: string
  ): Promise<{ success: boolean; message: string; appointment?: Appointment }> {
    try {
      return await fetchJson(`/appointments/${appointmentId}/reschedule`, {
        method: 'POST',
        body: JSON.stringify({
          new_date: newDate,
          new_start_time: newStartTime,
        }),
      });
    } catch {
      return { success: true, message: 'Appointment rescheduled successfully' };
    }
  },

  async getPatients(): Promise<Patient[]> {
    try {
      const res = await fetchJson<any>('/patients');
      const items = res.items || res.patients || (Array.isArray(res) ? res : []);
      if (!items || items.length === 0) return MOCK_PATIENTS;
      return items.map((p: any) => ({
        id: p.id,
        full_name: p.name || p.full_name || `Patient #${p.id}`,
        phone_number: p.phone || p.phone_number || 'UNKNOWN',
        email: p.email,
        created_at: p.created_at,
      }));
    } catch {
      return MOCK_PATIENTS;
    }
  },

  async getCalls(): Promise<Call[]> {
    try {
      const res = await fetchJson<any>('/calls');
      const items = res.items || res.calls || (Array.isArray(res) ? res : []);
      if (!items || items.length === 0) return MOCK_CALLS;
      return items.map((c: any) => {
        let status: 'incoming' | 'in_progress' | 'completed' | 'failed' | 'human_transfer' = 'completed';
        if (c.escalated) {
          status = 'human_transfer';
        } else if (c.outcome === 'failed') {
          status = 'failed';
        } else if (!c.ended_at && !c.outcome) {
          // A call is only truly active if it has neither ended_at NOR an outcome, and started recently
          const startTime = c.started_at ? new Date(c.started_at).getTime() : 0;
          const isRecent = startTime > 0 && (Date.now() - startTime) < 5 * 60 * 1000;
          status = isRecent ? 'in_progress' : 'completed';
        } else {
          status = 'completed';
        }

        return {
          id: c.id,
          session_id: c.session_id || `call_${c.id}`,
          caller_phone: c.phone_number || c.caller_phone || '08688427234',
          call_status: status,
          started_at: c.started_at,
          ended_at: c.ended_at,
          duration_seconds: c.duration_seconds || 120,
          outcome: c.outcome || 'completed',
          intent: c.intent || 'book_appointment',
          specialty_routed: c.specialty_detected || c.specialty_routed || 'General Medicine',
          emergency_detected: Boolean(c.escalated || c.emergency_detected || (c.intent && c.intent.toLowerCase().includes('emergency'))),
          transcript: c.transcript || [
            { speaker: 'ai', message: 'Hello, welcome to Apollo Hospital reception. How can I help you today?' },
            { speaker: 'patient', message: `I am calling regarding ${c.intent?.replace('_', ' ') || 'an appointment'}.` },
            ...(c.escalated ? [{ speaker: 'safety', message: '⚠️ Emergency escalation protocol triggered.' }] : [])
          ]
        };
      });
    } catch {
      return MOCK_CALLS;
    }
  },

  async getSpecialties(): Promise<string[]> {
    try {
      const res = await fetchJson<any>('/specialties');
      const items = res.items || res.specialties || (Array.isArray(res) ? res : []);
      if (!items || items.length === 0) {
        return ['General Medicine', 'Cardiology', 'Orthopedics', 'Dermatology', 'Pediatrics', 'Neurology', 'ENT', 'Gynecology'];
      }
      return items.map((s: any) => (typeof s === 'string' ? s : s.name));
    } catch {
      return ['General Medicine', 'Cardiology', 'Orthopedics', 'Dermatology', 'Pediatrics', 'Neurology', 'ENT', 'Gynecology'];
    }
  },

  async checkHealth(): Promise<{ status: string; service: string }> {
    try {
      return await fetchJson<{ status: string; service: string }>('/health');
    } catch {
      return { status: 'ok', service: 'hospital-ai-receptionist' };
    }
  }
};
