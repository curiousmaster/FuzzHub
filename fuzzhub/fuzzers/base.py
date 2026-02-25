"""
File: fuzzhub/fuzzers/base.py

Base fuzzer abstraction for FuzzHub.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import threading
import subprocess
import uuid
import time


class FuzzerState:
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    CRASHED = "crashed"
    ERROR = "error"


class BaseFuzzer(ABC):

    def __init__(self, campaign_id: str, config: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.campaign_id = campaign_id
        self.config = config

        self._state = FuzzerState.STOPPED
        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._started_at: Optional[float] = None

    # -----------------------------------------
    # Required Overrides
    # -----------------------------------------

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def build_command(self) -> list:
        pass

    @abstractmethod
    def collect_metrics(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def collect_crashes(self) -> list:
        pass

    # -----------------------------------------
    # Lifecycle
    # -----------------------------------------

    def start(self) -> None:
        with self._lock:
            if self._state == FuzzerState.RUNNING:
                return

            self._state = FuzzerState.STARTING
            cmd = self.build_command()

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self._started_at = time.time()
            self._state = FuzzerState.RUNNING

    def stop(self) -> None:
        with self._lock:
            if self._process:
                self._process.terminate()
                self._process.wait()
            self._state = FuzzerState.STOPPED

    # -----------------------------------------
    # Monitoring
    # -----------------------------------------

    def status(self) -> Dict[str, Any]:
        with self._lock:
            uptime = None
            if self._started_at:
                uptime = time.time() - self._started_at

            return {
                "id": self.id,
                "campaign_id": self.campaign_id,
                "state": self._state,
                "pid": self._process.pid if self._process else None,
                "uptime_seconds": uptime,
            }
