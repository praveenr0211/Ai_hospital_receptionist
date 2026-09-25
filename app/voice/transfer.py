"""Human operator transfer coordinator."""

import logging
from typing import Optional
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.call import Call
from app.models.enums import CallOutcome
from app.voice.session import voice_session_store, CallStatus
from app.voice.providers.exotel import exotel_provider

logger = logging.getLogger("voice.transfer")

DEFAULT_OPERATOR_NUMBER = "+919876543210"  # Configurable hospital desk


class TransferCoordinator:
    """Manages call escalation and telephony handoff to human hospital staff."""

    @staticmethod
    async def transfer_to_human(
        call_id: str,
        reason: str = "Patient requested human operator",
        destination_phone: Optional[str] = None
    ) -> bool:
        """Execute complete transfer of an active call to a human operator."""
        target_number = destination_phone or DEFAULT_OPERATOR_NUMBER
        session = voice_session_store.get(call_id)

        if session:
            session.mark_transferred(reason)
            logger.info("Marked voice session %s as HUMAN_TRANSFER (reason: %s)", call_id, reason)

        # Call telephony provider to initiate transfer
        transferred = await exotel_provider.transfer_call(call_id, target_number)

        # Update persistent database record
        try:
            with SessionLocal() as db:
                call_record = db.query(Call).filter(
                    (Call.provider_call_id == call_id) | (Call.id == int(call_id) if call_id.isdigit() else False)
                ).first()
                if call_record:
                    call_record.transfer_requested = True
                    call_record.transfer_reason = reason
                    call_record.call_status = CallStatus.HUMAN_TRANSFER.value
                    call_record.escalated = True
                    call_record.outcome = CallOutcome.ESCALATED
                    call_record.ended_at = datetime.now(timezone.utc)
                    db.commit()
        except Exception as exc:
            logger.error("Failed to update database for transferred call %s: %s", call_id, exc)

        return transferred


transfer_coordinator = TransferCoordinator()
