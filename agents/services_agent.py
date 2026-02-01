"""
Services Subagent
=================
Monitors Windows Services (using psutil).
"""
import time
import threading
import psutil
from soul.subconscious import get_subconscious, EventPriority

class ServicesAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.monitored_services = ["docker", "sql", "wuauserv", "windefend"]
        self.known_states = {} # {name: status}

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[ServicesAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
             self.thread.join(timeout=2)

    def _loop(self):
        while self.running:
            try:
                # psutil.win_service_iter() returns all services
                current_states = {}
                
                for service in psutil.win_service_iter():
                    try:
                        name = service.name().lower()
                        status = service.status()
                        
                        # Only care about some or all? Let's track interesting ones
                        # Tracking ALL is too noisy.
                        # Let's track changes in 'running' state for ANY service? No, too much.
                        # Just tracked ones for now.
                        for target in self.monitored_services:
                            if target in name:
                                current_states[name] = status
                                if name in self.known_states and self.known_states[name] != status:
                                     # Change detected
                                     print(f"[ServicesAgent] {name} changed to {status}")
                                     prio = EventPriority.HIGH if status == 'stopped' else EventPriority.NORMAL
                                     self.output_bus.publish("services", "SERVICE_STATE_CHANGED", {
                                         "name": name,
                                         "status": status
                                     }, prio)
                    except:
                        pass
                
                # Update known
                for n, s in current_states.items():
                    self.known_states[n] = s
                    
                time.sleep(5)
            except Exception as e:
                print(f"[ServicesAgent] Error: {e}")
                time.sleep(10)

# Singleton
_srv_agent = None
def get_services_agent():
    global _srv_agent
    if _srv_agent is None:
        _srv_agent = ServicesAgent()
    return _srv_agent
