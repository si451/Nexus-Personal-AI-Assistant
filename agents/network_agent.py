"""
Network Subagent
================
Monitors internet connectivity.
"""
import time
import threading
import socket
from soul.subconscious import get_subconscious, EventPriority

class NetworkAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.is_connected = True
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[NetworkAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def check_connection(self):
        try:
            # Connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def _loop(self):
        while self.running:
            try:
                status = self.check_connection()
                
                if status != self.is_connected:
                    self.is_connected = status
                    event = "INTERNET_RESTORED" if status else "INTERNET_LOST"
                    priority = EventPriority.HIGH if not status else EventPriority.NORMAL
                    
                    self.output_bus.publish("network", event, {
                        "connected": status
                    }, priority)
                
                time.sleep(10) # Check every 10 seconds
                
            except Exception as e:
                time.sleep(10)

# Singleton
_net_agent = None
def get_network_agent():
    global _net_agent
    if _net_agent is None:
        _net_agent = NetworkAgent()
    return _net_agent
