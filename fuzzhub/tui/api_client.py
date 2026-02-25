"""
File: fuzzhub/tui/api_client.py

Simple REST API client for FuzzHub TUI.
"""

import httpx


class APIClient:

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def health(self):
        r = httpx.get(f"{self.base_url}/health", timeout=5)
        r.raise_for_status()
        return r.json()

    def list_fuzzers(self):
        r = httpx.get(f"{self.base_url}/fuzzers", timeout=5)
        r.raise_for_status()
        return r.json()

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
