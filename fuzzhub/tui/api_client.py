"""
File: fuzzhub/tui/api_client.py

Simple REST API client for FuzzHub TUI.
"""

import httpx


class APIClient:

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    # -----------------------------------------
    # Health
    # -----------------------------------------

    def health(self):
        r = httpx.get(f"{self.base_url}/health", timeout=5)
        r.raise_for_status()
        return r.json()

    # -----------------------------------------
    # List fuzzers
    # -----------------------------------------

    def list_fuzzers(self):
        r = httpx.get(f"{self.base_url}/fuzzers", timeout=5)
        r.raise_for_status()
        return r.json()

    # -----------------------------------------
    # Start dummy fuzzer
    # -----------------------------------------

    def start_dummy(self):
        r = httpx.post(
            f"{self.base_url}/fuzzers/start",
            json={
                "campaign_id": "test_campaign",
                "fuzzer_type": "dummy",
                "config": {},
            },
            timeout=5,
        )
        r.raise_for_status()
        return r.json()

    # -----------------------------------------
    # Stop fuzzer
    # -----------------------------------------

    def stop_fuzzer(self, fuzzer_id):
        r = httpx.post(
            f"{self.base_url}/fuzzers/{fuzzer_id}/stop",
            timeout=5,
        )
        r.raise_for_status()
        return r.json()

    # -----------------------------------------
    # Restart fuzzer
    # -----------------------------------------

    def restart_fuzzer(self, fuzzer_id):
        r = httpx.post(
            f"{self.base_url}/fuzzers/{fuzzer_id}/restart",
            timeout=5,
        )
        r.raise_for_status()
        return r.json()
