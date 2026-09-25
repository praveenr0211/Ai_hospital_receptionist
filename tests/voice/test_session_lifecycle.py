"""Tests for voice session state machine and lifecycle manager."""

import pytest
from app.voice.session import VoiceSession, VoiceSessionStore, CallStatus
from app.voice.lifecycle import CallLifecycleManager, InvalidStateTransitionError


def test_voice_session_creation():
    store = VoiceSessionStore()
    session = store.create(call_id="call_99", phone_number="+919876543210")
    assert session.call_id == "call_99"
    assert session.agent_session_id == "voice_call_99"
    assert session.status == CallStatus.INCOMING
    assert session.duration_seconds == 0
    assert store.get("call_99") == session


def test_valid_lifecycle_transitions():
    session = VoiceSession(
        call_id="call_1",
        phone_number="+919876543210",
        agent_session_id="voice_call_1",
        status=CallStatus.INCOMING
    )

    CallLifecycleManager.transition(session, CallStatus.CONNECTING)
    assert session.status == CallStatus.CONNECTING

    CallLifecycleManager.transition(session, CallStatus.ACTIVE)
    assert session.status == CallStatus.ACTIVE
    assert session.answered_at is not None

    CallLifecycleManager.transition(session, CallStatus.PROCESSING)
    assert session.status == CallStatus.PROCESSING

    CallLifecycleManager.transition(session, CallStatus.COMPLETED)
    assert session.status == CallStatus.COMPLETED
    assert session.ended_at is not None
    assert session.duration_seconds >= 0


def test_invalid_lifecycle_transition():
    session = VoiceSession(
        call_id="call_2",
        phone_number="+919876543210",
        agent_session_id="voice_call_2",
        status=CallStatus.INCOMING
    )

    # Cannot jump directly from INCOMING to COMPLETED
    with pytest.raises(InvalidStateTransitionError):
        CallLifecycleManager.transition(session, CallStatus.COMPLETED)


def test_mark_transferred():
    session = VoiceSession(
        call_id="call_3",
        phone_number="+919876543210",
        agent_session_id="voice_call_3",
        status=CallStatus.ACTIVE
    )
    session.mark_transferred("Patient requested supervisor")
    assert session.status == CallStatus.HUMAN_TRANSFER
    assert session.transferred is True
    assert session.transfer_reason == "Patient requested supervisor"
