"""
File: fuzzhub/collectors/metrics.py

Metric collection thread for fuzzer instances.
"""

import threading
import time
from datetime import datetime

from fuzzhub.database.session import SessionLocal
from fuzzhub.database.models import MetricSnapshot


class MetricsCollector(threading.Thread):

    def __init__(self, fuzzer, interval: int = 5):
        super().__init__(daemon=True)
        self.fuzzer = fuzzer
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:
            try:
                metrics = self.fuzzer.collect_metrics()
                if metrics:
                    self._persist(metrics)
            except Exception as e:
                print(f"[!] Metrics error: {e}")

            time.sleep(self.interval)

    def stop(self):
        self._running = False

    def _persist(self, metrics):
        db = SessionLocal()

        snapshot = MetricSnapshot(
            fuzzer_instance_id=self.fuzzer.id,
            exec_per_sec=metrics.get("exec_per_sec"),
            corpus_size=metrics.get("corpus_size"),
            coverage=metrics.get("coverage"),
            crashes_found=metrics.get("crashes_found"),
            timestamp=datetime.utcnow(),
        )

        db.add(snapshot)
        db.commit()
        db.close()
