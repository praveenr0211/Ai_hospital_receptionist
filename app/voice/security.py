"""Security utilities for webhook verification and secret protection."""

import hmac
import hashlib
from typing import Optional
from fastapi import Header, HTTPException, status
from app.config import settings


def verify_telephony_webhook(
    x_exotel_signature: Optional[str] = Header(None, alias="X-Exotel-Signature"),
    authorization: Optional[str] = Header(None)
) -> bool:
    """Verify incoming Exotel webhook authenticity.
    
    If credentials are not configured (local development / testing), permit the request.
    In production with tokens configured, validates signature or auth header.
    """
    if settings.ENVIRONMENT == "development" or not settings.EXOTEL_API_TOKEN:
        return True

    # If auth header provided, match against token
    if authorization and authorization == f"Bearer {settings.EXOTEL_API_TOKEN}":
        return True

    # Signature verification if provided by webhook
    if x_exotel_signature and settings.EXOTEL_API_KEY:
        expected = hmac.new(
            settings.EXOTEL_API_TOKEN.encode("utf-8"),
            settings.EXOTEL_API_KEY.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        if hmac.compare_digest(x_exotel_signature, expected):
            return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized telephony webhook request"
    )
