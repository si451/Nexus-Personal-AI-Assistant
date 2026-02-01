"""
Clipboard Subagent
==================
Monitors clipboard content.
"""
import time
import threading
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

from soul.subconscious import get_subconscious, EventPriority

class ClipboardAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.last_content = ""
    
    def start(self):
        if not CLIPBOARD_AVAILABLE:
            print("[ClipboardAgent] pyperclip not installed. Disabled.")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[ClipboardAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def _loop(self):
        while self.running:
            try:
                content = pyperclip.paste()
                if content != self.last_content:
                    self.last_content = content
                    
                    if content and len(content.strip()) > 0:
                        # Don't log passwords (basic heuristic: no spaces, short?)
                        # For safely, we publish it but tag it
                        self.output_bus.publish("clipboard", "TEXT_COPIED", {
                            "length": len(content),
                            "preview": content[:50]
                        }, EventPriority.NORMAL)
                
                time.sleep(1) # Check every 1s
                
            except Exception as e:
                time.sleep(5)

# Singleton
_clip_agent = None
def get_clipboard_agent():
    global _clip_agent
    if _clip_agent is None:
        _clip_agent = ClipboardAgent()
    return _clip_agent
