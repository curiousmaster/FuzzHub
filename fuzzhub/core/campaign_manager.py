"""
File: fuzzhub/core/campaign_manager.py

Campaign and fuzzer orchestration logic with recovery support.
"""

import threading
from datetime import datetime
from typing import Dict

from fuzzhub.fuzzers.registry import FuzzerRegistry
from fuzzhub.database.session import SessionLocal
from fuzzhub.database.models import FuzzerInstance
from fuzzhub.collectors.metrics import MetricsCollector
from fuzzhub.collectors.crashes import CrashCollector
from fuzzhub.utils.process import pid_exists


class CampaignManager:

    def __init__(self, event_bus):
        self._fuzzers: Dict[str, object] = {}
        self._lock = threading.Lock()
        self._bus = event_bus
        print("EVENT BUS (inside campaign manager init):", id(self._bus))

    # -----------------------------------------
    # Recovery Logic
    # -----------------------------------------

    def recover_running_fuzzers(self):
        db = SessionLocal()
        instances = db.query(FuzzerInstance).filter_by(state="running").all()

        for instance in instances:
            if pid_exists(instance.pid):
                print(f"[+] Recovered fuzzer {instance.id} (PID {instance.pid})")
                self._fuzzers[instance.id] = self._create_placeholder(instance)
            else:
                print(f"[!] Stale fuzzer {instance.id} marked crashed")
                instance.state = "crashed"
                db.commit()

        db.close()

    def _create_placeholder(self, instance):
        class Placeholder:
            def __init__(self, db_instance):
                self.id = db_instance.id
                self.campaign_id = db_instance.campaign_id
                self._pid = db_instance.pid
                self._state = db_instance.state

            def status(self):
                return {
                    "id": self.id,
                    "campaign_id": self.campaign_id,
                    "state": self._state,
                    "pid": self._pid,
                }

            def stop(self):
                import os
                import signal
                try:
                    os.kill(self._pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass

        return Placeholder(instance)

    # -----------------------------------------
    # Campaign Control
    # -----------------------------------------

    def start_fuzzer(self, campaign_id: str, fuzzer_type: str, config: dict):

        fuzzer_cls = FuzzerRegistry.get(fuzzer_type)
        fuzzer = fuzzer_cls(campaign_id, config)

        fuzzer.setup()
        fuzzer.start()

        metrics_thread = MetricsCollector(fuzzer)
        crash_thread = CrashCollector(fuzzer)

        metrics_thread.start()
        crash_thread.start()

        fuzzer._metrics_thread = metrics_thread
        fuzzer._crash_thread = crash_thread

        with self._lock:
            self._fuzzers[fuzzer.id] = fuzzer

        self._persist_instance(fuzzer, fuzzer_type)

        self._bus.emit("fuzzer_update", {
            "type": "fuzzer_update",
            "fuzzer": fuzzer.status()
        })

        return fuzzer.id

    def stop_fuzzer(self, fuzzer_id: str):
        print("EMITTING ON BUS:", id(self._bus))
        print("STOP CALLED:", fuzzer_id)
        print("KNOWN FUZZERS:", list(self._fuzzers.keys()))
        with self._lock:
            if fuzzer_id in self._fuzzers:
                fuzzer = self._fuzzers[fuzzer_id]

                if hasattr(fuzzer, "_metrics_thread"):
                    fuzzer._metrics_thread.stop()
                if hasattr(fuzzer, "_crash_thread"):
                    fuzzer._crash_thread.stop()

                fuzzer.stop()
                self._mark_stopped_in_db(fuzzer_id)

                # Update internal state before emit
                status = {
                    "id": fuzzer_id,
                    "campaign_id": fuzzer.campaign_id,
                    "state": "stopped",
                    "pid": None,
                }

                print("EMIT: fuzzer_update(stop)")
                self._bus.emit("fuzzer_update", {
                    "fuzzer": status
                })


                del self._fuzzers[fuzzer_id]


    def restart_fuzzer(self, fuzzer_id: str):

        db = SessionLocal()
        instance = db.query(FuzzerInstance).filter_by(id=fuzzer_id).first()

        if not instance:
            db.close()
            return None

        campaign_id = instance.campaign_id
        fuzzer_type = instance.fuzzer_type

        db.close()

        # Stop old instance
        self.stop_fuzzer(fuzzer_id)

        # Start new instance
        new_id = self.start_fuzzer(
            campaign_id=campaign_id,
            fuzzer_type=fuzzer_type,
            config={}
        )

        return new_id

    def stop_all(self):
        with self._lock:
            for f in list(self._fuzzers.values()):
                f.stop()
            self._fuzzers.clear()

    # -----------------------------------------
    # Heartbeat & Monitoring
    # -----------------------------------------

    def heartbeat(self):
        with self._lock:
            for fuzzer in self._fuzzers.values():
                self._update_db_state(fuzzer)

                self._bus.emit("fuzzer_update", {
                    "type": "fuzzer_update",
                    "fuzzer": fuzzer.status()
                })

    # -----------------------------------------
    # Persistence
    # -----------------------------------------

    def _persist_instance(self, fuzzer, fuzzer_type: str):

        db = SessionLocal()

        instance = FuzzerInstance(
            id=fuzzer.id,
            campaign_id=fuzzer.campaign_id,
            fuzzer_type=fuzzer_type,
            pid=fuzzer.status()["pid"],
            state=fuzzer.status()["state"],
            started_at=datetime.utcnow(),
            last_heartbeat=datetime.utcnow(),
        )

        db.add(instance)
        db.commit()
        db.close()

    def _update_db_state(self, fuzzer):
        db = SessionLocal()
        instance = db.query(FuzzerInstance).filter_by(id=fuzzer.id).first()
        if instance:
            instance.state = fuzzer.status()["state"]
            instance.pid = fuzzer.status()["pid"]
            instance.last_heartbeat = datetime.utcnow()
            db.commit()
        db.close()

    def _mark_stopped_in_db(self, fuzzer_id: str):
        db = SessionLocal()
        instance = db.query(FuzzerInstance).filter_by(id=fuzzer_id).first()
        if instance:
            instance.state = "stopped"
            instance.last_heartbeat = datetime.utcnow()
            db.commit()
        db.close()
