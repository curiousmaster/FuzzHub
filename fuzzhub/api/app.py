"""
File: fuzzhub/api/app.py
"""

import asyncio
import json
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from fuzzhub.database.session import SessionLocal
from fuzzhub.database.models import MetricSnapshot, Crash


class StartFuzzerRequest(BaseModel):
    campaign_id: str
    fuzzer_type: str
    config: dict = {}


def create_api(campaign_manager, event_bus):

    app = FastAPI(title="FuzzHub API")

    # -----------------------------------------
    # WebSocket Connection Registry
    # -----------------------------------------

    active_connections: List[WebSocket] = []

    async def broadcast(event: dict):
        """Send JSON event to all connected WebSocket clients."""
        dead_connections = []

        for connection in active_connections:
            try:
                await connection.send_text(json.dumps(event))
            except Exception:
                dead_connections.append(connection)

        for conn in dead_connections:
            if conn in active_connections:
                active_connections.remove(conn)

    # -----------------------------------------
    # EventBus → WebSocket Bridge
    # -----------------------------------------

    def handle_event(event: dict):
        """
        Called from EventBus (sync context).
        Safely schedule async broadcast in uvicorn loop.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(broadcast(event))
        except RuntimeError:
            # No running loop (startup/shutdown edge case)
            pass

    # Subscribe to all events
    event_bus.subscribe("*", handle_event)

    # -----------------------------------------
    # Health
    # -----------------------------------------

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # -----------------------------------------
    # List Fuzzers
    # -----------------------------------------

    @app.get("/fuzzers")
    def list_fuzzers():
        db = SessionLocal()
        data = []

        for f in campaign_manager._fuzzers.values():
            status = f.status()

            latest_metric = (
                db.query(MetricSnapshot)
                .filter_by(fuzzer_instance_id=status["id"])
                .order_by(MetricSnapshot.timestamp.desc())
                .first()
            )

            crash_count = (
                db.query(Crash)
                .filter_by(fuzzer_instance_id=status["id"])
                .count()
            )

            data.append({
                **status,
                "exec_per_sec": latest_metric.exec_per_sec if latest_metric else None,
                "corpus_size": latest_metric.corpus_size if latest_metric else None,
                "coverage": latest_metric.coverage if latest_metric else None,
                "crash_count": crash_count,
            })

        db.close()
        return data

    # -----------------------------------------
    # Start Fuzzer
    # -----------------------------------------

    @app.post("/fuzzers/start")
    def start_fuzzer(req: StartFuzzerRequest):
        fuzzer_id = campaign_manager.start_fuzzer(
            req.campaign_id,
            req.fuzzer_type,
            req.config,
        )
        return {"fuzzer_id": fuzzer_id}

    # -----------------------------------------
    # Stop Fuzzer
    # -----------------------------------------

    @app.post("/fuzzers/{fuzzer_id}/stop")
    def stop_fuzzer(fuzzer_id: str):
        campaign_manager.stop_fuzzer(fuzzer_id)
        return {"status": "stopped"}

    # -----------------------------------------
    # Restart Fuzzer
    # -----------------------------------------

    @app.post("/fuzzers/{fuzzer_id}/restart")
    def restart_fuzzer(fuzzer_id: str):
        new_id = campaign_manager.restart_fuzzer(fuzzer_id)
        return {"status": "restarted", "new_id": new_id}

    # -----------------------------------------
    # WebSocket Endpoint
    # -----------------------------------------

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        active_connections.append(websocket)

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            if websocket in active_connections:
                active_connections.remove(websocket)
        except Exception:
            if websocket in active_connections:
                active_connections.remove(websocket)

    return app
