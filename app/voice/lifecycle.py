"""Call lifecycle management and state transition rules."""

from typing import Set
from app.voice.session import CallStatus, VoiceSession


# Valid state transitions
VALID_TRANSITIONS: dict[CallStatus, Set[CallStatus]] = {
    CallStatus.INCOMING: {CallStatus.CONNECTING, CallStatus.ACTIVE, CallStatus.FAILED},
    CallStatus.CONNECTING: {CallStatus.ACTIVE, CallStatus.COMPLETED, CallStatus.FAILED},
    CallStatus.ACTIVE: {CallStatus.PROCESSING, CallStatus.HUMAN_TRANSFER, CallStatus.COMPLETED, CallStatus.FAILED},
    CallStatus.PROCESSING: {CallStatus.ACTIVE, CallStatus.HUMAN_TRANSFER, CallStatus.COMPLETED, CallStatus.FAILED},
    CallStatus.HUMAN_TRANSFER: {CallStatus.COMPLETED, CallStatus.FAILED},
    CallStatus.COMPLETED: set(),  # Terminal state
    CallStatus.FAILED: set(),     # Terminal state
}


class InvalidStateTransitionError(Exception):
    """Raised when an illegal call state transition is attempted."""
    pass


class CallLifecycleManager:
    """Validates and applies call lifecycle state changes."""

    @staticmethod
    def transition(session: VoiceSession, target_status: CallStatus) -> None:
        """Validate and transition a voice session to a target state."""
        allowed = VALID_TRANSITIONS.get(session.status, set())
        if target_status not in allowed:
            raise InvalidStateTransitionError(
                f"Cannot transition voice call {session.call_id} from {session.status.value} to {target_status.value}."
            )

        if target_status == CallStatus.ACTIVE and session.status in (CallStatus.INCOMING, CallStatus.CONNECTING):
            session.mark_answered()
        elif target_status == CallStatus.COMPLETED:
            session.mark_completed()
        elif target_status == CallStatus.FAILED:
            session.mark_failed("Unspecified failure")
        else:
            session.status = target_status

    @staticmethod
    def is_terminal(status: CallStatus) -> bool:
        """Check if call state is terminal."""
        return status in (CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.HUMAN_TRANSFER)
