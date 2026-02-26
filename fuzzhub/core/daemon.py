"""
File: fuzzhub/core/daemon.py
"""

import uvicorn

from fuzzhub.database.init_db import init_database
from fuzzhub.core.event_bus import EventBus
from fuzzhub.core.campaign_manager import CampaignManager
from fuzzhub.api.app import create_api


class FuzzHubDaemon:
    """
    Main daemon entrypoint for FuzzHub.

    Responsibilities:
    - Initialize database
    - Create shared EventBus
    - Create CampaignManager
    - Create FastAPI app
    - Launch Uvicorn server
    """

    def __init__(self):

        print("[*] Starting FuzzHub daemon")

        # -----------------------------------------
        # Initialize database
        # -----------------------------------------

        init_database()

        # -----------------------------------------
        # Shared EventBus (single instance)
        # -----------------------------------------

        self.event_bus = EventBus()
        print("EVENT BUS:", id(self.event_bus))

        # -----------------------------------------
        # Campaign Manager (uses same EventBus)
        # -----------------------------------------

        self.campaign_manager = CampaignManager(self.event_bus)

        print("[*] Recovering running fuzzers")
        self.campaign_manager.recover_running_fuzzers()

        # -----------------------------------------
        # FastAPI application (same EventBus)
        # -----------------------------------------

        self.app = create_api(
            campaign_manager=self.campaign_manager,
            event_bus=self.event_bus,
        )

    # -----------------------------------------
    # Run server
    # -----------------------------------------

    def run(self):
        """
        Start the ASGI server.

        Uvicorn handles:
        - Signal management (SIGINT/SIGTERM)
        - Graceful shutdown
        - Lifespan events
        """

        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
        )
