"""
File: fuzzhub/core/event_bus.py

Thread-safe internal event bus with structured events
and optional wildcard + async handler support.
"""

import threading
import asyncio
from typing import Callable, Dict, List, Any
from datetime import datetime


class EventBus:
    def __init__(self):
        # event_type -> list[handler]
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    # --------------------------------------------------
    # Subscription Management
    # --------------------------------------------------

    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to a specific event type.

        Use "*" to subscribe to all events.
        """
        with self._lock:
            self._subscribers.setdefault(event_type, [])
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        with self._lock:
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)

                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]

    # --------------------------------------------------
    # Event Emission
    # --------------------------------------------------

    def emit(self, event_type: str, payload: Dict[str, Any]):
        """
        Emit an event.

        Handlers receive a structured event dict:
        {
            "type": str,
            "timestamp": str (UTC ISO),
            "payload": dict
        }
        """

        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
        }

        with self._lock:
            specific_handlers = list(self._subscribers.get(event_type, []))
            wildcard_handlers = list(self._subscribers.get("*", []))

        handlers = specific_handlers + wildcard_handlers

        for handler in handlers:
            try:
                # If handler is async, schedule it
                if asyncio.iscoroutinefunction(handler):
                    try:
                        asyncio.create_task(handler(event))
                    except RuntimeError:
                        # No running loop (e.g. non-async context)
                        pass
                else:
                    handler(event)

            except Exception:
                # Never let one subscriber break others
                pass
