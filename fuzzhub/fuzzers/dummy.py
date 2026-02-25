"""
File: fuzzhub/fuzzers/dummy.py

Dummy test fuzzer for validating FuzzHub core systems.
"""

import random
import time
from fuzzhub.fuzzers.base import BaseFuzzer


class DummyFuzzer(BaseFuzzer):

    def setup(self):
        pass

    def build_command(self):
        # Simulate long-running background process
        return ["sleep", "10000"]

    def collect_metrics(self):
        return {
            "exec_per_sec": random.uniform(1000, 5000),
            "corpus_size": random.randint(100, 500),
            "coverage": random.uniform(10.0, 85.0),
            "crashes_found": random.randint(0, 5),
        }

    def collect_crashes(self):
        # Randomly simulate crash
        if random.random() < 0.2:
            return [{
                "type": "segmentation_fault",
                "input_path": f"/tmp/input_{random.randint(1,1000)}",
                "stack_trace": "dummy_stack_trace_line_1\nline_2\nline_3"
            }]
        return []
