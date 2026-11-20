"""
Instant alerts for the owner's app over a WebSocket.

FastAPI supports WebSockets out of the box (uvicorn[standard] already includes
the websockets library), so no new packages are needed. The app runs as one
process, so keeping the open connections in memory is enough.
"""

import anyio
from fastapi import WebSocket


class OwnerHub:
    def __init__(self):
        self.clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.add(ws)

    def disconnect(self, ws: WebSocket):
        self.clients.discard(ws)

    async def broadcast(self, message: dict):
        for ws in list(self.clients):
            try:
                await ws.send_json(message)
            except Exception:
                self.clients.discard(ws)


hub = OwnerHub()


def notify_owner(event: str, **data):
    """Send an event to every open owner tab. Safe to call from normal (sync) endpoints."""
    if not hub.clients:
        return
    try:
        # Sync endpoints run in a worker thread; this hops back to the event loop
        anyio.from_thread.run(hub.broadcast, {"type": event, **data})
    except RuntimeError:
        pass  # not running inside the server (e.g. a script)
