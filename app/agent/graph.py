from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.agent.state import session_store, ReceptionistState
from app.agent.router import route_conversation
from app.schemas.agent import AgentResponse

class ReceptionistAgent:
    """
    Orchestrates the AI Hospital Receptionist state machine.
    Manages session isolation, turn routing, tool execution boundaries,
    and structured responses.
    """
    def __init__(self) -> None:
        self.store = session_store

    def process_message(
        self,
        session_id: str,
        message: str,
        phone_number: str | None = None,
        db: Session | None = None,
    ) -> AgentResponse:
        """
        Execute one conversation turn for the given session.
        """
        is_local_db = False
        if db is None:
            db = SessionLocal()
            is_local_db = True

        try:
            # 1. Retrieve or initialize isolated session state
            state: ReceptionistState = self.store.get_or_create(
                session_id=session_id,
                phone_number=phone_number,
            )

            # 2. Append incoming message to conversation history
            state.add_message(role="user", content=message)

            # Auto-resolve patient record if caller phone is available and not yet loaded
            phone_to_check = phone_number or state.patient_phone
            if phone_to_check and not state.patient_id:
                from app.agent.tools.patient_tools import find_patient_by_phone
                p_lookup = find_patient_by_phone(db, phone_to_check)
                if p_lookup.exists:
                    state.patient_id = p_lookup.patient_id
                    state.patient_name = p_lookup.patient_name
                    state.patient_phone = p_lookup.phone_number

            # 3. Route conversation through state machine nodes
            reply_text, action_required = route_conversation(
                state=state,
                user_message=message,
                db=db,
            )

            # 4. Append assistant response to history
            state.add_message(role="assistant", content=reply_text)

            # 5. Save updated state back into session store
            self.store.save(state)

            if is_local_db:
                db.commit()

            return AgentResponse(
                session_id=session_id,
                message=reply_text,
                state=state.current_state,
                action_required=action_required,
                appointment_id=state.appointment_id,
                escalation_required=state.escalation_required,
                data={
                    "patient_id": state.patient_id,
                    "doctor_id": state.doctor_id,
                    "doctor_name": state.doctor_name,
                    "specialty": state.specialty,
                    "appointment_date": state.appointment_date,
                    "selected_slot": state.selected_slot,
                },
            )

        except Exception as e:
            if is_local_db:
                db.rollback()
            raise e
        finally:
            if is_local_db:
                db.close()

agent = ReceptionistAgent()
