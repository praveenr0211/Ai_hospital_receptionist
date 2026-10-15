"""Server launcher with telephony-compatible WebSocket settings."""

import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(base_dir, "lib")
if os.path.exists(lib_dir):
    sys.path.insert(0, lib_dir)
sys.path.insert(0, base_dir)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT", os.environ.get("PORT", 9000)))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        ws_ping_interval=None,
        ws_ping_timeout=None,
    )
