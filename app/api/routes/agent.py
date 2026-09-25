from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.agent import ChatRequest, AgentResponse
from app.agent.graph import agent
from app.agent.state import session_store

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post(
    "/chat",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI Hospital Receptionist Agent",
)
def chat_with_agent(
    req: ChatRequest,
    db: Session = Depends(get_db),
) -> AgentResponse:
    """
    Process one conversation turn with the AI Hospital Receptionist.
    Maintains isolated conversational state per session_id.
    """
    return agent.process_message(
        session_id=req.session_id,
        message=req.message,
        phone_number=req.phone_number,
        db=db,
    )

@router.post(
    "/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset an agent conversation session",
)
def reset_agent_session(
    session_id: str,
) -> dict[str, str]:
    """Clear memory and state for a specific session_id."""
    session_store.clear(session_id)
    return {"message": "Session state reset successfully.", "session_id": session_id}

@router.get(
    "/state/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Inspect current state of an agent session",
)
def get_session_state(
    session_id: str,
) -> dict:
    """Retrieve structured internal state for an active session."""
    state = session_store.get_or_create(session_id)
    return state.model_dump()
