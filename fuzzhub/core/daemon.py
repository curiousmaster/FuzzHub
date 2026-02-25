"""
File: fuzzhub/core/daemon.py

FuzzHub backend daemon.
Responsible for:
- EventBus initialization
- CampaignManager lifecycle
- API startup
- Heartbeat loop
"""

import threading
import time
import signal
import sys

import uvicorn

from fuzzhub.core.event_bus import EventBus
from fuzzhub.core.campaign_manager import CampaignManager
from fuzzhub.api.app import create_api


class FuzzHubDaemon:
    def __init__(self, host="0.0.0.0", port=8000, heartbeat_interval=5):
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval

        self._running = False
        self._heartbeat_thread = None

        # -----------------------------------------
        # Core Architecture Wiring
        # -----------------------------------------

        self.event_bus = EventBus()
        self.campaign_manager = CampaignManager(self.event_bus)
        self.app = create_api(self.campaign_manager, self.event_bus)

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def start(self):
        print("[*] Starting FuzzHub daemon")

        self._running = True

        # Recover running fuzzers from DB
        print("[*] Recovering running fuzzers")
        self.campaign_manager.recover_running_fuzzers()

        # Start heartbeat thread
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
        )
        self._heartbeat_thread.start()

        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # Start API server (blocking)
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )

    def stop(self):
        print("[*] Stopping FuzzHub daemon")
        self._running = False

        # Stop all fuzzers safely
        self.campaign_manager.stop_all()

        print("[*] Shutdown complete")

    # --------------------------------------------------
    # Heartbeat
    # --------------------------------------------------

    def _heartbeat_loop(self):
        while self._running:
            try:
                self.campaign_manager.heartbeat()
            except Exception as e:
                print(f"[!] Heartbeat error: {e}")

            time.sleep(self.heartbeat_interval)

    # --------------------------------------------------
    # Signal Handling
    # --------------------------------------------------

    def _handle_shutdown(self, signum, frame):
        print(f"[*] Received signal {signum}, shutting down")
        self.stop()
        sys.exit(0)
