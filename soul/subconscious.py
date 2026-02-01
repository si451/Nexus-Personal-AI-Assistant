"""
Nexus Subconscious (The Event Bus)
==================================
The central nervous system of Nexus.
It receives events from all subagents (Vision, Audio, System, etc.)
and allows the Conscious Brain (autonomous_loop) to react to them.

Features:
- Pub/Sub architecture.
- Thread-safe event queue.
- Event priority handling.
- Short-term event memory.
"""

import queue
import time
import threading
from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Callable, Any

class EventPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class NexusEvent:
    def __init__(self, channel: str, type: str, payload: Any, priority: EventPriority = EventPriority.NORMAL):
        self.id = f"{int(time.time()*1000)}"
        self.channel = channel
        self.type = type
        self.payload = payload
        self.priority = priority
        self.timestamp = datetime.now()
        self.processed = False

    def __repr__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.type} ({self.priority.name})"

class NexusSubconscious:
    def __init__(self):
        # Event Queue for processing
        self.event_queue = queue.PriorityQueue()
        
        # History (Short-term memory of events)
        self.event_history: List[NexusEvent] = []
        self.history_lock = threading.Lock()
        
        # Pub/Sub callbacks
        self.subscribers: Dict[str, List[Callable[[NexusEvent], None]]] = {}
        
        # State tracking (Current state of the world)
        self.world_state = {}
        self.state_lock = threading.Lock()

    def publish(self, channel: str, type: str, payload: Any, priority: EventPriority = EventPriority.NORMAL):
        """
        Publish an event to the subconscious.
        Non-blocking.
        """
        event = NexusEvent(channel, type, payload, priority)
        
        # 1. Store in history
        with self.history_lock:
            self.event_history.append(event)
            # Keep only last 1000 events
            if len(self.event_history) > 1000:
                self.event_history.pop(0)
        
        # 2. Update World State (Simple key-value store based on latest event type)
        # e.g., type="VOLUME_CHANGED" -> updates state["volume"]
        with self.state_lock:
            self.world_state[type] = payload
            self.world_state["last_updated"] = datetime.now()

        # 3. Notify subscribers immediately (in separate threads to not block publisher)
        # For simplicity, we might run this in a background worker, but for now simple dispatch
        self._dispatch(event)
        
        # 4. Enqueue for the Conscious Brain to pick up if high priority
        if priority >= EventPriority.HIGH:
            # Check if recently queued similar event to reduce spam?
            # For now, just queue it. 
            # PriorityQueue stores tuples, lower number = higher priority.
            # So we store (-priority, event)
            self.event_queue.put((-int(priority), event))
            
        return event

    def subscribe(self, channel: str, callback: Callable[[NexusEvent], None]):
        """Subscribe to a specific channel (e.g. 'vision', 'system')."""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)

    def _dispatch(self, event: NexusEvent):
        """Internal dispatch to subscribers."""
        # Channel subscribers
        if event.channel in self.subscribers:
            for cb in self.subscribers[event.channel]:
                try:
                    cb(event)
                except Exception as e:
                    print(f"[Subconscious] Dispatch Error: {e}")
        
        # 'all' channel subscribers
        if 'all' in self.subscribers:
             for cb in self.subscribers['all']:
                try:
                    cb(event)
                except Exception as e:
                    pass

    def get_high_priority_events(self) -> List[NexusEvent]:
        """
        Called by the Conscious Brain to see what needs attention.
        Returns all queued high-priority events.
        """
        events = []
        while not self.event_queue.empty():
            try:
                _, event = self.event_queue.get_nowait()
                events.append(event)
            except queue.Empty:
                break
        return events

    def get_recent_history(self, limit=10) -> List[NexusEvent]:
        with self.history_lock:
            return self.event_history[-limit:]
            
    def get_recent_events(self, limit=10) -> List[NexusEvent]:
        """Alias for get_recent_history, used by Brain."""
        return self.get_recent_history(limit)

# Singleton
_subconscious = None

def get_subconscious() -> NexusSubconscious:
    global _subconscious
    if _subconscious is None:
        _subconscious = NexusSubconscious()
    return _subconscious
