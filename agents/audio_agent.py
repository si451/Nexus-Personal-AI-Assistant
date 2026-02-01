"""
Audio Subagent
==============
Monitors audio state changes.
"""
import time
import threading
from senses.ears import get_ears
from soul.subconscious import get_subconscious, EventPriority

class AudioAgent:
    def __init__(self):
        self.ears = get_ears()
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.last_vol = -1.0
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[AudioAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def _loop(self):
        while self.running:
            try:
                current_vol = self.ears.get_volume()
                
                if abs(current_vol - self.last_vol) > 0.05: # Changed by > 5%
                    self.output_bus.publish("audio", "VOLUME_CHANGED", {
                        "level": current_vol,
                        "percent": int(current_vol * 100)
                    }, EventPriority.LOW)
                    self.last_vol = current_vol
                
                time.sleep(1) # Fast check
                
            except Exception as e:
                time.sleep(5)

# Singleton
_audio_agent = None
def get_audio_agent():
    global _audio_agent
    if _audio_agent is None:
        _audio_agent = AudioAgent()
    return _audio_agent
