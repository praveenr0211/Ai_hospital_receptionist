# AI Hospital Receptionist Agent 🏥📞

An intelligent, multi-phase enterprise AI receptionist and booking engine designed for hospitals and healthcare clinics.

---

## 🏗️ Architecture Overview

The system is built on a clean layered architecture where deterministic business logic, database integrity, and medical safety guardrails remain strictly isolated from LLM decision-making:

```text
                    PATIENT (Phone / Chat)
                              │
                              ▼
                   ┌─────────────────────┐
                   │    Phase 5: Agent   │
                   │   State Machine     │
                   │   LLM Reasoning     │
                   └──────────┬──────────┘
                              │ Tool Calls
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Phase 4: Safety │ │  Phase 3: APIs   │ │ Phase 2: Booking │
│  Medical Routing │ │  FastAPI REST    │ │ Availability     │
│  Triage & Redflag│ │  Pydantic V2     │ │ Concurrency Lock │
└──────────────────┘ └──────────────────┘ └────────┬─────────┘
                                                   │
                                                   ▼
                                        ┌────────────────────┐
                                        │ Phase 1: DB Engine │
                                        │ PostgreSQL 18      │
                                        │ SQLAlchemy 2.0     │
                                        │ Alembic Migrations │
                                        └────────────────────┘
```

---

## 🚀 Key Modules & Completed Phases

### 1. Phase 1 — Database & Persistence
- **PostgreSQL 18** with **SQLAlchemy 2.0** ORM and **Alembic** migrations.
- 7 core entities: `doctors`, `specialties`, `patients`, `doctor_schedules`, `appointments`, `calls`, `notifications`.
- Database-level double-booking protection using exclusion constraints / unique active slot index:
  `UNIQUE (doctor_id, appointment_date, start_time) WHERE status != 'CANCELLED'`.
- Realistic medical seed data with doctors across Cardiology, Neurology, Orthopedics, Pediatrics, and Dermatology.

### 2. Phase 2 — Availability & Deterministic Booking Engine
- Dynamic slot generation with shift boundary enforcement, duration handling, and existing appointment blocking.
- Atomic, transactional booking with race-condition handling (`SlotAlreadyBookedError`).
- Rescheduling with rollback safety and cancellation with audit history preservation.
- Smart alternative slot search (next available slots for the same doctor or same specialty).

### 3. Phase 3 — FastAPI REST API Layer
- Clean, decoupled RESTful endpoints conforming to RFC 7807 problem details:
  - `/api/v1/doctors` — List and filter doctors by specialty.
  - `/api/v1/availability` — Query open booking slots.
  - `/api/v1/appointments` — Book, reschedule, cancel, and retrieve appointments.
  - `/api/v1/calls` — Inbound call tracking and analytics.
  - `/api/v1/dashboard` — Live operational statistics.
  - `/health` — PostgreSQL and system health monitoring.

### 4. Phase 4 — Medical Routing & Clinical Safety Engine
- Red-flag emergency symptom detection (e.g., chest pain radiating to arm, sudden numbness, severe respiratory distress).
- Immediate booking blocker and emergency protocol activation (`CALL_911_OR_EMERGENCY`).
- Specialty routing matching symptoms to relevant clinical departments with confidence scores.
- Multi-symptom ambiguity resolution and human operator escalation.

### 5. Phase 5 — AI Agent & State Machine Orchestrator
- Session-isolated conversational state machine (`ReceptionistState`).
- Multi-turn conversational flow preserving patient history, symptoms, chosen doctor, and slot selection.
- Explicit booking confirmation gate before executing irreversible DB transactions.
- In-memory session management with conversation reset capabilities.

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+ (tested on Python 3.14)
- **Framework**: FastAPI, Pydantic V2, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy 2.0, Alembic, psycopg v3
- **Testing**: pytest, pytest-asyncio, HTTPX

---

## 🚦 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/praveenr0211/Ai_hospital_receptionist.git
cd Ai_hospital_receptionist
```

### 2. Set up virtual environment & install dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file based on `.env.example`:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hospital_receptionist
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/hospital_receptionist
```

### 4. Run database migrations & seed data
```bash
alembic upgrade head
python scripts/seed_data.py
```

### 5. Run the test suite
```bash
pytest
```
*Current test suite: 125 tests passing (100% pass rate).*

### 6. Start the API server
```bash
uvicorn app.main:app --reload --port 8000
```
Visit the interactive API docs at `http://localhost:8000/docs`.

---

## 🧪 Verification Scripts

- `python scripts/verify_db.py` — Database schema & seed verification
- `python scripts/verify_booking_engine.py` — Availability & race condition verification
- `python scripts/verify_medical_routing.py` — Medical safety & emergency triage test
- `python scripts/verify_agent.py` — 11-step end-to-end multi-turn conversation test
