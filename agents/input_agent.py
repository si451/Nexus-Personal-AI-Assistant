"""
Input Subagent (Idle Monitor)
=============================
Tracks user activity (Keyboard/Mouse) to detect idle state.
Uses pynput.
"""
import time
import threading
try:
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

from soul.subconscious import get_subconscious, EventPriority

class InputAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.last_activity = time.time()
        self.is_idle = False
        self.idle_threshold = 60 # Seconds
    
    def _on_move(self, x, y):
        self.last_activity = time.time()
        if self.is_idle:
            self.is_idle = False
            self.output_bus.publish("input", "USER_ACTIVE", {}, EventPriority.NORMAL)

    def _on_press(self, key):
        self.last_activity = time.time()
        if self.is_idle:
            self.is_idle = False
            self.output_bus.publish("input", "USER_ACTIVE", {}, EventPriority.NORMAL)

    def start(self):
        if not PYNPUT_AVAILABLE:
            print("[InputAgent] pynput not installed. Disabled.")
            return

        self.running = True
        
        # Listeners (non-blocking)
        self.mouse_listener = mouse.Listener(on_move=self._on_move)
        self.mouse_listener.start()
        
        self.key_listener = keyboard.Listener(on_press=self._on_press)
        self.key_listener.start()
        
        # Idle check loop
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[InputAgent] Started")

    def stop(self):
        self.running = False
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        if hasattr(self, 'key_listener'):
            self.key_listener.stop()

    def _loop(self):
        while self.running:
            time.sleep(5)
            if not self.is_idle:
                idle_time = time.time() - self.last_activity
                if idle_time > self.idle_threshold:
                    self.is_idle = True
                    self.output_bus.publish("input", "USER_IDLE", {"seconds": int(idle_time)}, EventPriority.LOW)

# Singleton
_input_agent = None
def get_input_agent():
    global _input_agent
    if _input_agent is None:
        _input_agent = InputAgent()
    return _input_agent
