"""
Window Subagent
===============
Manages window focus and arrangement.
"""
import time
import threading
try:
    import pygetwindow as gw
    GW_AVAILABLE = True
except ImportError:
    GW_AVAILABLE = False

from soul.subconscious import get_subconscious, EventPriority

class WindowAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.last_active_title = ""

    def start(self):
        if not GW_AVAILABLE:
            print("[WindowAgent] pygetwindow not installed. Disabled.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[WindowAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
             self.thread.join(timeout=2)

    def minimize_all(self):
        try:
             # Basic implementation
             windows = gw.getAllWindows()
             for w in windows:
                 if not w.isMinimized:
                     w.minimize()
             return "Minimized all windows."
        except Exception as e:
             return f"Error minimizing: {e}"

    def focus_app(self, app_name: str):
        try:
            windows = gw.getWindowsWithTitle(app_name)
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                return f"Focused {app_name}"
            return f"App {app_name} not found."
        except Exception as e:
            return f"Error focusing: {e}"

    def _loop(self):
        while self.running:
            try:
                # Monitor active window changes if Vision Agent misses it
                # Or just be ready for commands
                win = gw.getActiveWindow()
                if win:
                    title = win.title
                    if title != self.last_active_title:
                        # We could publish, but Vision Agent does this.
                        # Let's just keep track for now.
                        self.last_active_title = title
                        
                time.sleep(1)
            except Exception as e:
                time.sleep(2)

# Singleton
_win_agent = None
def get_window_agent():
    global _win_agent
    if _win_agent is None:
        _win_agent = WindowAgent()
    return _win_agent
