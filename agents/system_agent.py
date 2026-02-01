"""
System Subagent
===============
Monitors system resources (CPU, RAM, Battery) and App Events.
"""
import time
import threading
import psutil
from soul.subconscious import get_subconscious, EventPriority

class SystemAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[SystemAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def _loop(self):
        while self.running:
            try:
                # 1. Resource Monitoring
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                battery = psutil.sensors_battery()
                
                # Events
                if cpu > 90:
                    self.output_bus.publish("system", "CPU_HIGH", {"percent": cpu}, EventPriority.HIGH)
                
                if ram > 90:
                    self.output_bus.publish("system", "RAM_HIGH", {"percent": ram}, EventPriority.HIGH)
                    
                if battery and battery.percent < 20 and not battery.power_plugged:
                    self.output_bus.publish("system", "BATTERY_LOW", {"percent": battery.percent}, EventPriority.CRITICAL)
                
                # Publish General Stats (Low Priority)
                self.output_bus.publish("system", "STATS_UPDATE", {
                    "cpu": cpu,
                    "ram": ram,
                    "battery": battery.percent if battery else "AC"
                }, EventPriority.LOW)
                
                time.sleep(5) # Check every 5 seconds
                
            except Exception as e:
                print(f"[SystemAgent] Error: {e}")
                time.sleep(5)

# Singleton
_sys_agent = None
def get_system_agent():
    global _sys_agent
    if _sys_agent is None:
        _sys_agent = SystemAgent()
    return _sys_agent
