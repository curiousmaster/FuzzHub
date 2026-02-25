"""
File: fuzzhub/utils/process.py

Process utilities for PID validation.
"""

import os
import signal


def pid_exists(pid: int) -> bool:
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def terminate_pid(pid: int):
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        pass
