"""
Automation Subagent (The Hands)
===============================
Provides capability to physical interact with the OS.
SAFETY: To stop, slam mouse to any corner (PyAutoGUI fail-safe).
"""
import time
import threading
try:
    import pyautogui
    PYAG_AVAILABLE = True
except ImportError:
    PYAG_AVAILABLE = False

from soul.subconscious import get_subconscious, EventPriority

class AutomationAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        if PYAG_AVAILABLE:
            pyautogui.FAILSAFE = True
        
    def start(self):
        if not PYAG_AVAILABLE:
            print("[AutomationAgent] PyAutoGUI not installed.")
            return

        self.running = True
        # This agent is mostly REACTIVE (it does what it's told), 
        # but it can loop to report mouse position or idle status if needed.
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[AutomationAgent] Started (Hands Ready)")

    def stop(self):
        self.running = False
        if self.thread:
             self.thread.join(timeout=2)

    # --- Actions ---
    def click(self, x, y, clicks=1):
        try:
            pyautogui.click(x, y, clicks=clicks)
            return True
        except Exception as e:
            print(f"[AutomationAgent] Click Failed: {e}")
            return False

    def type_text(self, text):
        try:
            pyautogui.write(text, interval=0.05)
            return True
        except Exception as e:
            print(f"[AutomationAgent] Type Failed: {e}")
            return False

    def press_key(self, key):
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"[AutomationAgent] Press Failed: {e}")
            return False

    def _loop(self):
        while self.running:
            # Just keep thread alive. 
            time.sleep(1)

# Singleton
_auto_agent = None
def get_automation_agent():
    global _auto_agent
    if _auto_agent is None:
        _auto_agent = AutomationAgent()
    return _auto_agent
