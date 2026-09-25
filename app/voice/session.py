"""Voice session state management and in-memory session registry.

Maps Exotel Call SIDs to Phase 5 Agent session IDs and tracks real-time call lifecycle.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class CallStatus(str, Enum):
    """Voice call lifecycle status."""
    INCOMING = "incoming"
    CONNECTING = "connecting"
    ACTIVE = "active"
    PROCESSING = "processing"
    HUMAN_TRANSFER = "human_transfer"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceSession(BaseModel):
    """Represents an active or historical voice call session."""
    call_id: str = Field(..., description="Provider Call SID (e.g. Exotel Call SID)")
    stream_id: Optional[str] = Field(None, description="WebSocket media stream ID")
    phone_number: str = Field(..., description="Caller's phone number in E.164 format")
    agent_session_id: str = Field(..., description="Phase 5 agent session identifier")
    status: CallStatus = Field(default=CallStatus.INCOMING, description="Current lifecycle state")

    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0

    transferred: bool = False
    transfer_reason: Optional[str] = None
    failure_reason: Optional[str] = None
    patient_id: Optional[int] = None
    conversation_summary: Optional[str] = None
    meta: Dict = Field(default_factory=dict)

    def mark_answered(self) -> None:
        """Mark call as answered and active."""
        now = datetime.now(timezone.utc)
        self.answered_at = now
        self.status = CallStatus.ACTIVE

    def mark_completed(self) -> None:
        """Mark call as completed and calculate duration."""
        now = datetime.now(timezone.utc)
        self.ended_at = now
        self.status = CallStatus.COMPLETED
        if self.started_at:
            self.duration_seconds = int((now - self.started_at).total_seconds())

    def mark_failed(self, reason: str) -> None:
        """Mark call as failed with failure reason."""
        now = datetime.now(timezone.utc)
        self.ended_at = now
        self.status = CallStatus.FAILED
        self.failure_reason = reason
        if self.started_at:
            self.duration_seconds = int((now - self.started_at).total_seconds())

    def mark_transferred(self, reason: str) -> None:
        """Mark call as transferred to human operator."""
        now = datetime.now(timezone.utc)
        self.ended_at = now
        self.transferred = True
        self.transfer_reason = reason
        self.status = CallStatus.HUMAN_TRANSFER
        if self.started_at:
            self.duration_seconds = int((now - self.started_at).total_seconds())


class VoiceSessionStore:
    """Thread-safe in-memory store for tracking active voice sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, VoiceSession] = {}

    def create(self, call_id: str, phone_number: str, stream_id: Optional[str] = None) -> VoiceSession:
        """Create a new VoiceSession mapped to a Phase 5 session."""
        agent_session_id = f"voice_{call_id}"
        session = VoiceSession(
            call_id=call_id,
            stream_id=stream_id,
            phone_number=phone_number,
            agent_session_id=agent_session_id,
            status=CallStatus.INCOMING
        )
        self._sessions[call_id] = session
        return session

    def get(self, call_id: str) -> Optional[VoiceSession]:
        """Retrieve a voice session by call_id."""
        return self._sessions.get(call_id)

    def get_by_stream(self, stream_id: str) -> Optional[VoiceSession]:
        """Retrieve a voice session by stream_id."""
        for session in self._sessions.values():
            if session.stream_id == stream_id:
                return session
        return None

    def update(self, session: VoiceSession) -> None:
        """Update or persist voice session in memory."""
        self._sessions[session.call_id] = session

    def delete(self, call_id: str) -> None:
        """Remove voice session from memory."""
        if call_id in self._sessions:
            del self._sessions[call_id]

    def all_active_sessions(self) -> Dict[str, VoiceSession]:
        """Return all active non-terminal sessions."""
        return {
            cid: s for cid, s in self._sessions.items()
            if s.status not in (CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.HUMAN_TRANSFER)
        }


# Global in-memory voice session registry
voice_session_store = VoiceSessionStore()
