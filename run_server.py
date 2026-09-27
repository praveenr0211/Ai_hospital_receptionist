"""Server launcher with telephony-compatible WebSocket settings."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws_ping_interval=None,  # Disable keepalive ping so Exotel telephony stream doesn't time out
        ws_ping_timeout=None,
    )
