export interface Doctor {
  id: number;
  name: string;
  specialty: string;
  qualification?: string;
  experience_years?: number;
  consultation_fee: number;
  status: 'active' | 'inactive' | 'on_leave';
  created_at?: string;
}

export interface DoctorSchedule {
  id: number;
  doctor_id: number;
  day_of_week: number; // 0=Mon, 6=Sun
  start_time: string;
  end_time: string;
  slot_duration_minutes: number;
  is_active: boolean;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
  appointment_id?: number | null;
  patient_name?: string | null;
}

export interface Appointment {
  id: number;
  doctor_id: number;
  patient_id: number;
  appointment_date: string;
  start_time: string;
  end_time: string;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'no_show';
  reason?: string;
  cancellation_reason?: string;
  doctor?: Doctor;
  patient?: Patient;
}

export interface Patient {
  id: number;
  full_name: string;
  phone_number: string;
  email?: string;
  date_of_birth?: string;
  gender?: string;
  created_at?: string;
  appointments?: Appointment[];
}

export interface CallTranscriptMessage {
  speaker: 'ai' | 'patient' | 'safety' | 'system';
  message: string;
  timestamp?: string;
}

export interface Call {
  id: number;
  session_id: string;
  provider_call_id?: string;
  caller_phone: string;
  call_status: 'incoming' | 'in_progress' | 'completed' | 'failed' | 'human_transfer';
  started_at: string;
  ended_at?: string;
  duration_seconds: number;
  outcome?: string;
  intent?: string;
  specialty_routed?: string;
  doctor_id?: number;
  appointment_id?: number;
  emergency_detected: boolean;
  transcript?: CallTranscriptMessage[];
  recording_url?: string;
}

export interface DashboardSummary {
  total_doctors: number;
  active_doctors: number;
  total_patients: number;
  appointments_today: number;
  confirmed_appointments: number;
  cancelled_appointments: number;
  calls_today: number;
  successful_bookings_today: number;
  escalated_calls_today: number;
  ai_resolution_rate: number;
  reference_date: string;
}

export interface DashboardDoctor {
  doctor_id: number;
  name: string;
  specialty: string;
  status: string;
  booked_slots_today: number;
  total_slots_today: number;
}
