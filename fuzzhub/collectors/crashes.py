"""
File: fuzzhub/collectors/crashes.py

Crash collection and deduplication thread.
"""

import threading
import time
import hashlib
from datetime import datetime

from fuzzhub.database.session import SessionLocal
from fuzzhub.database.models import Crash


class CrashCollector(threading.Thread):

    def __init__(self, fuzzer, interval: int = 3):
        super().__init__(daemon=True)
        self.fuzzer = fuzzer
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:
            try:
                crashes = self.fuzzer.collect_crashes()
                for crash in crashes:
                    self._process_crash(crash)
            except Exception as e:
                print(f"[!] Crash collector error: {e}")

            time.sleep(self.interval)

    def stop(self):
        self._running = False

    # -----------------------------------------
    # Deduplication Logic
    # -----------------------------------------

    def _process_crash(self, crash_data):
        crash_hash = self._generate_hash(crash_data)

        db = SessionLocal()
        existing = db.query(Crash).filter_by(crash_hash=crash_hash).first()

        if existing:
            existing.occurrences += 1
            existing.last_seen = datetime.utcnow()
        else:
            crash = Crash(
                campaign_id=self.fuzzer.campaign_id,
                fuzzer_instance_id=self.fuzzer.id,
                crash_hash=crash_hash,
                crash_type=crash_data.get("type"),
                input_path=crash_data.get("input_path"),
                stack_trace=crash_data.get("stack_trace"),
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                occurrences=1,
            )
            db.add(crash)

        db.commit()
        db.close()

    def _generate_hash(self, crash_data):
        base = (
            crash_data.get("type", "") +
            crash_data.get("stack_trace", "")
        )
        return hashlib.sha256(base.encode()).hexdigest()
